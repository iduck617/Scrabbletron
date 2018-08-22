from collections import defaultdict
from player import Player
from board import Board
import time

class Ai(Player):
	TIMEOUT = 15000

	def __init__(self, root, board, bag):
		Player.__init__(self, root)
		self.__board = board
		self.__bag = bag

	def get_rack_balance(self):
		vowels = ['A','E','I','O','U']
		num_vowels = sum(1 if c.get_value() in vowels else 0 for c in self._rack)

		return num_vowels / len(self._rack)

	def get_anchor_squares(self):
		return self.__board.get_anchor_squares()

	def permute_rack_tiles(self, tile_slots):
		possible_placements = []
		board_points, placed_points = set(), set()
		rack = self._rack
		permute_dict = defaultdict(list)

		for placement in tile_slots:
			for (row,col),tile in placement:
				if not tile is None:
					board_points.add((row,col))
				else:
					for tile in rack:
						permute_dict[(row,col)].append(tile)
						placed_points.add((row,col))
			possible_placements.append((list(board_points),list(placed_points),permute_dict))
			board_points, placed_points = set(), set()
			permute_dict = defaultdict(list)

		return possible_placements

	# GIVE CREDIT HERE
	def reorderTileSlots(self, slots):
		orderedBySlots = [[] for i in range(self.get_rack_size()+1)]
		
		for tile_slot in slots:
			i = 0
			for pos, slot in tile_slot:
				if slot == None:
					i += 1
			assert i < len(orderedBySlots)	
			orderedBySlots[i].append(tile_slot)
		
		newTileSlots = []	
		for ranking in orderedBySlots:
			if len(ranking) > 0:
				for tile_slot in ranking:
					newTileSlots.append(tile_slot)
					
		return newTileSlots		
						
	def calculate_cross_checks(self,anchors):
		tile_slots = []

		for row,col in anchors:
			for lo in range(0, len(self._rack)):
				for hi in range(0, len(self._rack)-lo):
					horz = [((row, col), self.__board.get_entry(row,col)[0])]
					lo_count = 0
					hi_count = 0
					x_pos, y_pos = row-1, col

					while x_pos > 0 and (lo_count < lo or self.__board.get_entry(x_pos,y_pos)[0] != None):
						lo_count += 1
						horz.insert(0, ((x_pos, y_pos), self.__board.get_entry(x_pos,y_pos)[0]))
						x_pos -= 1

					x_pos, y_pos = row+1, col
					while x_pos < Board.SIZE-1 and (hi_count < hi or self.__board.get_entry(x_pos,y_pos)[0] != None):
						hi_count += 1
						horz.append(((x_pos, y_pos), self.__board.get_entry(x_pos,y_pos)[0]))	
						x_pos += 1	
					
					vert = [((row, col), self.__board.get_entry(row,col)[0])]
					lo_count = 0
					hi_count = 0
					x_pos, y_pos = row, col-1

					while y_pos > 0 and (lo_count < lo or self.__board.get_entry(x_pos,y_pos)[0] != None):
						lo_count += 1
						vert.insert(0, ((x_pos, y_pos), self.__board.get_entry(x_pos,y_pos)[0]))
						y_pos -= 1

					x_pos, y_pos = row, col+1
					while y_pos < Board.SIZE-1 and (hi_count < hi or self.__board.get_entry(x_pos,y_pos)[0] != None):
						hi_count += 1
						vert.append(((x_pos, y_pos), self.__board.get_entry(x_pos,y_pos)[0]))
						y_pos += 1
						
					tile_slots.append(horz)
					tile_slots.append(vert)	


		tileSlotsMap = {}
		i = 0
		while i < len(tile_slots):
			slot = tile_slots[i]
			(x1, y1) = slot[0]
			(x2, y2) = slot[-1]
			if tileSlotsMap.get((x1,y1,x2,y2), False):
				tile_slots.pop(i)
			else:
				tileSlotsMap[(x1,y1,x2,y2)] = True
				i += 1
				
		tile_slots = self.reorderTileSlots(tile_slots)
		
		return tile_slots


