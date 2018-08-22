from dawg import DAWG
from error import Error
from itertools import imap, chain, product
from operator import sub
from tile import Tile 
from Tkinter import *

class Board:
	SIZE = 15
	DIMENSION = Tile.DIMENSION * SIZE

	NORMAL = 'N'
	TRIPLE_WORD = 'TW'
	DOUBLE_WORD = 'DW'
	TRIPLE_LETTER = 'TL'
	DOUBLE_LETTER = 'DL'

	def __init__(self, root):
		self.__root = root
		self.__squares = []
		self.__tw_squares = [(0,0),(0,7),(0,14),(7,0),(7,14),(14,0),(14,7),(14,14)]
		self.__dw_sqaures = [(1,1),(2,2),(3,3),(4,4),(7,7),(10,10),(11,11),(12,12),(13,13),
								(13,1),(12,2),(11,3),(10,4),(4,10),(3,11),(2,12),(1,13)]
		self.__tl_squares = [(1,5),(1,9),(13,5),(13,9),(5,1),(5,5),(5,9),(5,13),
								(9,1),(9,5),(9,9),(9,13),(13,5),(13,9)]
		self.__dl_squares = [(0,3),(0,11),(2,6),(2,8),(3,0),(3,7),(3,14),(6,2),(6,6),
								(6,8),(6,12),(7,3),(7,11),(8,2),(8,6),(8,8),(8,12),
								(11,0),(11,7),(11,14),(12,6),(12,8),(14,3),(14,11)]
		self.__settled_tiles = {} # maps coordinates to tile frames (persist GUI)
		self.__placed_tiles  = {} 
		self.__dawg   = DAWG(open('ospd-us.txt').read().split('\n'))

		for i in range(Board.SIZE):
			self.__squares.append([])
			for j in range(Board.SIZE):
				if (i,j) in self.__tw_squares:
					type_ = Board.TRIPLE_WORD
				elif (i,j) in self.__dw_sqaures:
					type_ = Board.DOUBLE_WORD
				elif (i,j) in self.__tl_squares:
					type_ = Board.TRIPLE_LETTER
				elif (i,j) in self.__dl_squares:
					type_ = Board.DOUBLE_LETTER
				else:
					type_ = Board.NORMAL 
				self.__squares[i].append((None,type_))

	############################################################################

	def score_words(self,groups,is_ai=False):
		total = 0
		multiplier = 1
		words = [sorted(group[0] + group[1]) for group in groups]

		for word in words:
			for point in word:
				row, col = point
				tile, type_ = self.get_entry(row,col)

				if type_ == Board.DOUBLE_WORD:
					multiplier *= 2
					total += tile.get_points()
				elif type_ == Board.TRIPLE_WORD:
					multiplier *= 3
					total += tile.get_points()
				elif type_ == Board.DOUBLE_LETTER:
					total += 2*tile.get_points()
				elif type_ == Board.TRIPLE_LETTER:
					total += 3*tile.get_points()
				else:
					total += tile.get_points()
					
		return multiplier*total
	
	def get_settled_tiles(self):
		return self.__settled_tiles

	def reconcile_settled_tiles(self):
		'''In form: points[(row,col)] = (Tile object, frame object)'''
		for pt in self.__placed_tiles:
			row, col = pt
			entry = self.__placed_tiles[pt]
			tile = entry[0]
			frame = entry[1]
			self.add_entry(tile,row,col)
			self.__settled_tiles[(row,col)] = tile
		self.reset_placed_tiles()
	
	############################################################################

	def get_dawg(self):
		return self.__dawg

	def get_placed_tiles(self):
		return self.__placed_tiles

	def get_placed_tile(self,row,col):
		try:
			return self.__placed_tiles[(row,col)][0]
		except:
			return None

	def add_placed_tile(self,row,col,tile, make_frame=True):
		if not self.get_placed_tile(row,col):
			if make_frame:
				tile_frame = self.__make_tile_frame(row,col,tile)
			else:
				tile_frame = None
			self.__placed_tiles[(row,col)] = (tile, tile_frame)
			return True
		else:
			return False

	def remove_placed_tile(self,row,col):
		if self.get_placed_tile(row,col):
			entry = self.__placed_tiles.pop((row,col))
			entry[1].destroy()
			return entry[0]

	def reset_placed_tiles(self):
		self.__placed_tiles = {}

	def __make_tile_frame(self,row,col,tile):
		entry = Frame(board_frame, bd=1, relief=RAISED)
		entry.place(y=row*Tile.DIMENSION, x=col*Tile.DIMENSION, height=Tile.DIMENSION, 
			width=Tile.DIMENSION)  
		label = Label(entry, text=tile.display(), height=Tile.DIMENSION, 
			width=Tile.DIMENSION)
		label.pack()
		return entry

	############################################################################
	
	def get_entry(self,row,col):
		return self.__squares[row][col]

	def add_entry(self, tile, row, col):
		if row >= 0 and col >= 0 and row < Board.SIZE and col < Board.SIZE:
			entry = self.__squares[row][col]
			if not entry[0] is None or tile is None:
				raise Board.OccupationError()

			self.__squares[row][col] = (tile, entry[1])

	def remove_entry(self, row, col):
		if row < 0 or col < 0 or row >= Board.SIZE or col >= Board.SIZE:
			raise Board.PlacementError()

		type_ = self.__squares[row][col][1]
		self.__squares[row][col] = (None, type_)

	############################################################################

	def compute_cross_checks(self):
		pass

	def check_and_get_valid_placement(self,turn):
		placed_rows, placed_cols = [], []
		placed_row, placed_col = -1, -1
		possible_word_points = []
		board_points = []
		connected_squares = set()
		placed_points = self.__placed_tiles.keys()
		neighbors = self.__get_adj_placed_tiles()

		for tile in neighbors:
			row,col = tile
			for point in self.__get_extended_tiles(row,col):
				connected_squares.add(point)

		connected_squares = sorted(list(connected_squares))

		def separate(p):
			placed_rows.append(p[0])
			placed_cols.append(p[1])

		map(separate, placed_points)

		# player has placed 0 tiles, thus cannot play this turn yet
		if len(self.__placed_tiles) == 0:
			print '0 placed tiles'
			return False

		# ensure that the placed tiles touch at least one anchor square
		if not self.__is_connected(turn):
			print 'not connected'
			return False

		tiles_along_row = self.__check_same(placed_rows)
		tiles_along_col = self.__check_same(placed_cols)
		if not tiles_along_row and not tiles_along_col: # tiles not along one axis
			print 'not along axis'
			return False

		# account for word formed along major axis
		placed_axis = placed_rows[0] if tiles_along_row else placed_cols[0]
		axis = None

		for board_point in connected_squares:
			print board_point
			row,col = board_point
			dim = row if tiles_along_row else col
			if dim == placed_axis:
				board_points.append(board_point)
				# connected_squares.remove(board_point)
		
		# if turn != 1 and len(board_points) != 0:
		if turn == 1 or len(board_points) != 0:
			possible_word_points.append((board_points,placed_points))
		
		# if tiles_along_row and (not self.get_entry(dim-1,placed_cols[0]) is None or \
		# 						not self.get_entry(dim+1,placed_cols[0]) is None) or \
		# 	tiles_along_col and (not self.get_entry(placed_rows[0],dim-1) or \
		# 						not self.get_entry(placed_rows[0],dim+1) is None):

		print connected_squares

		# account for crosswords along other axis
		for placed_point in placed_points:
			placed_row, placed_col = placed_point
			board_points = []

			if len(connected_squares) != 0:
				for board_point in connected_squares:
					print board_point
					row,col = board_point
					dim = col if tiles_along_row else row
					other_axis = placed_col if tiles_along_row else placed_row

					if dim == other_axis:
						board_points.append(board_point)
						connected_squares.remove(board_point)

				if len(board_points) != 0:
					possible_word_points.append((board_points,[placed_point]))

		# check that all formed words are continuous
		for group in possible_word_points:
			word_combo = group[0] + group[1]
			if Board.__has_gaps(word_combo):
				print 'has gaps'
				return False

		return possible_word_points

	def __check_words(self):
		pass

	# change to check_and_get_valid_words
	def check_if_valid_word(self,group,tile_dict=[]):
		chars = []
		placed_tiles = []
		word_list = []
		groups = []
		board_points,placed_points = group
		entire_word_points = sorted(board_points + placed_points)
		source = None

		if len(tile_dict) != 0:
			for i, point in enumerate(entire_word_points):
				word_list.append([])
				placed_tiles.append({})
				if not point in tile_dict:
					row,col = point
					word_list[i].append(self.__squares[row][col][0].get_value())
				else:
					for tile in tile_dict[point]:
						word_list[i].append(tile.get_value())
						placed_tiles[i][point] = tile
			# placed_tiles = list(product(*placed_tiles))
			word_list = [''.join(t).lower() for t in product(*word_list)]
			word_list = [word for word in word_list if word in self.__dawg]

			return word_list
		else:
			for row,col in entire_word_points:
				if (row,col) in board_points:
					source = self.__squares[row][col][0]
				else:
					source = self.__placed_tiles[(row,col)][0]
				chars.append(source.get_value())
				word = ''.join(chars).lower()
			return word in self.__dawg

	# def check_if_valid_word(self,group,tile_dict=[]):
	# 	chars = []
	# 	board_points,placed_points = group
	# 	entire_word_points = sorted(board_points + placed_points)

	# 	for i in range(len(entire_word_points)):
	# 		point = entire_word_points[i]
	# 		row, col = point
	# 		source = None

	# 		if point in board_points:
	# 			source = self.__squares[row][col][0]
	# 		elif len(tile_dict) != 0:
	# 			source = tile_dict[(row,col)]
	# 		else:
	# 			source = self.__placed_tiles[(row,col)][0]
	# 		chars.append(source.get_value())

	# 	word = ''.join(chars).lower()
	# 	return word in self.__dawg

	@staticmethod
	def get_coordinates(event):
		col = abs((board_frame.winfo_rootx() - event.x_root)/Tile.DIMENSION) - 1
		row = abs((board_frame.winfo_rooty() - event.y_root)/Tile.DIMENSION) - 1
		row, col = (-1, -1) if row > 14 or col > 14 else (row, col)
		
		return row, col

	############################################################################

	@staticmethod
	def __check_same(l):
		return all(map(lambda p : p == l[0],l))

	# http://stackoverflow.com/questions/20718315/how-to-find-a-missing-number-from-a-list
	@staticmethod
	def __has_gaps(points):
		rows, cols = [], []

		def separate(p):
			rows.append(p[0])
			cols.append(p[1])

		map(separate, points)
		l = sorted(cols if Board.__check_same(rows) else rows)

		return list(chain.from_iterable((l[i] + d for d in xrange(1, diff)) 
			for i, diff in enumerate(imap(sub, l[1:], l)) if diff > 1))

	def __get_valid_adjacent_squares(self, row, col):
		candidates = [(row+1,col),(row-1,col),(row,col+1),(row,col-1)]
		valid = []

		for point in candidates:
			row, col = point
			if row < Board.SIZE and col < Board.SIZE:
				if self.__squares[row][col][0] is None:
					valid.append((row,col))

		return valid

	def get_anchor_squares(self):
		anchors = set()
		for i,row in enumerate(self.__squares):
			for j,col in enumerate(row):
				if not col[0] is None:
					for p in self.__get_valid_adjacent_squares(i,j):
						anchors.add(p)
		return anchors

	def __is_connected(self,turn):
		anchors = [(Board.SIZE/2,Board.SIZE/2)] if turn == 1 else self.get_anchor_squares()
		for p in self.__placed_tiles:
			if p in anchors:
				return True
		return False

	def __get_adj_placed_tiles(self):
		neighbors = set()
		print 'placed tiles'
		print self.__placed_tiles
		for point in self.__placed_tiles.keys():
			row,col = point

			try:
				if not self.get_entry(row+1,col)[0] is None:
					neighbors.add((row+1,col))
			except:
				pass
			try:
				if not self.get_entry(row-1,col)[0] is None:
					neighbors.add((row-1,col))
			except:
				pass
			try:
				if not self.get_entry(row,col+1)[0] is None:
					neighbors.add((row,col+1))
			except:
				pass
			try:
				if not self.get_entry(row,col-1)[0] is None:
					neighbors.add((row,col-1))
			except:
				pass
				
		return neighbors

	def __get_extended_tiles(self, row, col):
		candidates = set()

		# pos_or_neg = True (increasing coords)
		# pos_or_neg = False (decreasing coords)
		# row_or_col = True (along a row - increasing col)
		# row_or_col = False (along a col - increasing row)
		def repeat(row,col,pos_or_neg,row_or_col):
			if self.__squares[row][col][0] is None:
				return

			candidates.add((row,col))

			if pos_or_neg and row_or_col:
				return repeat(row,col+1,True,True)
			elif pos_or_neg and not row_or_col:
				return repeat(row+1,col,True,False)
			elif not pos_or_neg and row_or_col:
				return repeat(row,col-1,False,True)
			else:
				return repeat(row-1,col,False,False)

		repeat(row,col,True,True)
		repeat(row,col,True,False)
		repeat(row,col,False,True)
		repeat(row,col,False,False)
		return candidates

	############################################################################

	def draw(self):
		colors = {Board.TRIPLE_WORD: "#501E05", 
				  Board.DOUBLE_WORD: "#FFD122", 
				  Board.TRIPLE_LETTER: "#bf4305", 
				  Board.DOUBLE_LETTER: "#F95D0F",
				  Board.NORMAL: "white"}

		global board_frame
		board_frame = Frame(self.__root, width=Board.DIMENSION, height=Board.DIMENSION)

		for i,row in enumerate(self.__squares):
			for j,col in enumerate(row):
				type_ = col[1] if not col[1] == Board.NORMAL else ''
				color = colors[col[1]] if not (i,j) == (Board.SIZE/2,Board.SIZE/2) else '#F95D0F'
				entry = Frame(board_frame, bd=1, relief=RAISED)
				entry.place(x=i*Tile.DIMENSION, y=j*Tile.DIMENSION, 
					width=Tile.DIMENSION, height=Tile.DIMENSION)  
				label = Label(entry, text=type_, height=Tile.DIMENSION, 
					width=Tile.DIMENSION, bg=color)
				label.pack()

		board_frame.pack(pady=25)

	def __str__(self):
		out = ''
		for row in self.__squares:
			for col in row:
				out += (col[1] if col[0] is None else col[0].get_value() + ',' + col[1]) + '\t'
			out += '\n'

		return out

	class PlacementError(Error):
		def __init__(self, message='Indices out of bound'):
			Error.__init__(self, message)

	class OccupationError(Error):
		def __init__(self, message='Cannot place tile there'):
			Error.__init__(self, message)