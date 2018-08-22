from ai import Ai
from bag import Bag
from board import Board
from human import Human
from tile import Tile
from Tkinter import *

import time

import sys

class Game:
	HUMAN = 'human'
	AI = 'ai'

	def __init__(self,root):
		self.__root   = root
		self.__board  = Board(root)
		self.__bag    = Bag()
		self.__human  = Human(root)
		self.__ai     = Ai(root, self.__board, self.__bag)
		self.__turn   = 1
		self.__player = self.__human
		self.__human_score = StringVar()
		self.__ai_score    = StringVar()

	def __next_turn(self):
		self.__turn += 1
		self.__player = self.__human if self.__turn % 2 == 1 else self.__ai

	def main(self):
		print 'in main'
		width  = self.__root.winfo_screenwidth()/3.0
		height = 3*self.__root.winfo_screenheight()/4.0

		Game.pick_tiles(self.__human, self.__bag)
		Game.pick_tiles(self.__ai, self.__bag)

		self.__board.draw()
		self.__human.draw_rack()
		self.draw_game_buttons()

		self.__human_score.set(str(self.__human.get_points()))
		self.__ai_score.set(str(self.__ai.get_points()))

		self.__root.title('Scrabbletron')
		self.__root.geometry("%dx%d%+d%+d" % (width, height, 0, 0))
		self.__root.config(bg="#2F4F4F")

		self.__root.bind('<Button-1>', self.perform_placement)
		self.play()
		# self.__root.after(0, self.play)
		# self.__root.mainloop()

	def play(self):
		while self.__root:
			self.__root.update_idletasks()
			self.__root.update()

			if self.__turn % 2 == 0:
				start_time = time.time()
				anchors = self.__ai.get_anchor_squares()
				placements = self.__ai.calculate_cross_checks(anchors)
				possible_words = self.__ai.permute_rack_tiles(placements)
				print "len of possible moves: " + str(len(possible_words))
				valid_words = set()
				score_map = {}

				for board,placed,tile_dict in possible_words:
					for word in self.__board.check_if_valid_word((board,placed),tile_dict):
						valid_words.add(word)

				print self.__ai
				print 'len of valid moves: ' + str(len(valid_words))
				print valid_words
				print str(time.time()-start_time)
				# 	if self.__board.check_if_valid_word((board,placed),tile_dict):
				# 		valid_words.append(word)
				# print valid_words

				# for word in valid_words:
				# 	score_map[word] = self.__board.score_words(word,True)
				# print score_map
				self.__next_turn()
		# while not self.__bag.is_empty():
		# 	if self.__turn % 2 == 0:
		# 		self.__ai.get_anchor_squares()

		# while self.__human.get_rack_size() > 0 and self.__ai.get_rack_size() > 0:
		# 	pass

		# if self.__human.get_points() > self.__ai.get_points():
		# 	print 'You won!'
		# else:
		# 	print 'Sorry, Scrabbletron won :('
		# self.__root.after(0, self.play)


	def pass_turn(self):
		# remove any placed tiles and put on racks\
		self.__root.update()
		self.__next_turn()

	@staticmethod
	def pick_tiles(player, bag, allow_label=False):
		while not bag.is_empty():
			if not player.add_to_rack(bag.draw(),allow_label):
				break

	def exchange_letter(self):
		self.__root.update()
		tile = self.__player.get_selected_tile()
		# remove any placed tiles and put on rack
		if not tile and self.__turn % 2 == 1:
			alert_window = Toplevel(self.__root, height=500, width=500)
			alert = Label(alert_window, text='You must select a tile to exchange.')
			alert.pack()
			close = Button(alert_window, text="Close", command=alert_window.destroy)
			close.pack()
		elif tile: 
			if self.__bag.size() >= 7:
				self.__player.remove_from_rack(tile)
				self.__bag.add(tile)
				Game.pick_tiles(self.__player,self.__bag,self.__turn % 2 == 1)
				self.__next_turn()

	def play_word(self):
		if len(self.__board.get_placed_tiles()) != 0:
			possible_word_points = self.__board.check_and_get_valid_placement(self.__turn)
			if possible_word_points:
				for group in possible_word_points:
					if not self.__board.check_if_valid_word(group):
						print 'not a word'
						# put tiles back on rack
						return
				self.__board.reconcile_settled_tiles()
				word_score = self.__board.score_words(possible_word_points)
				self.__human_score.set(str(self.__human.add_points(word_score)))
				Game.pick_tiles(self.__human, self.__bag, True)
				self.__next_turn()
			else:
				#put tiles back on rack
				print 'invalid placing'
			self.__root.update_idletasks()

	# for human --> consider moving to human.py
	def perform_placement(self,event):
		if self.__turn % 2 == 1 :
			rack_tile = self.__human.get_selected_tile()
			row, col = Board.get_coordinates(event)
			board_tile = self.__board.get_placed_tile(row,col)
			if not (row,col) == (-1,-1):
				if rack_tile and not board_tile:
					self.__human.remove_from_rack(rack_tile)
					self.__board.add_placed_tile(row,col,rack_tile)
				elif not rack_tile and board_tile:
					removed_tile = self.__board.remove_placed_tile(row,col)
					removed_tile.toggle()
					self.__human.add_to_rack(board_tile, True)
				elif rack_tile and board_tile:
					print self.__human.get_selected_tile()
			self.__root.update_idletasks()

	def draw_game_buttons(self):
		control_frame = Frame(self.__root)
		
		score_frame = Frame(control_frame)
		human_score_label = Label(score_frame, text="Your score: ").pack(side=LEFT,padx=2)
		human_score = Label(score_frame, textvariable=self.__human_score).pack(side=LEFT)
	 	ai_score_label = Label(score_frame, text="Scrabbletron's score: ").pack(side=LEFT,padx=2)
	 	ai_score = Label(score_frame, textvariable=self.__ai_score).pack(side=LEFT)

	 	button_frame = Frame(control_frame)
	 	play_button = Button(button_frame, text='Play word', 
	 		command=self.play_word).pack(side=TOP,pady=5)
	 	exchange_button = Button(button_frame, text="Exchange tile", 
	 		command=self.exchange_letter).pack(side=TOP,pady=5)
	 	pass_button = Button(button_frame, text="Pass", command=self.pass_turn).pack(side=TOP,pady=5)

	 	state_frame = Frame(button_frame)
	 	instruction_button = Button(state_frame, text="Instructions", 
	 		command=self.display_instructions).pack(side=LEFT,padx=10)
		exit_button = Button(state_frame, text="Exit", command=self.exit).pack(side=LEFT)
		
		score_frame.pack(side=TOP,pady=15)
		state_frame.pack(side=TOP)
		button_frame.pack(side=TOP)
		control_frame.pack(side=TOP)

	def display_instructions(self):
	    text = """How to play against Scrabbletron:

	    You get a rack of 7 tiles to start the game. You must play words with these
	    7 tiles so that each word formed vertically and horizontally is a word. Whenever 
	    you play a word, make sure that it touches at least one other letter on the board 
	    (not diagonally.) The first move must touch the star in the middle of the board.
	    
	    To play a tile, click and drag the tile to the board. When you play a tile, make 
	    sure that it snaps into a space. If it doesn't, then it didn't place and you have 
	    to do it again.

	    " " tiles are blank tiles. They can be played as any letter.

	    If you can't find any words to make, you can exchange. Exchanging 
	    You get a certain amount of points based on the letters you played.
	    Special Score Tiles:
	    \tTWS (triple word score): Multiplies your score for that turn by 3.
	    \tDWS (double word score): Multiplies your score for that turn by 2.
	    \tTLS (triple letter score): Multiplies your score for that letter by 3.
	    \tDLS (double letter score): Multiplies your score for that letter by 2.
	    
	    Once you play a word, you draw tiles until you have seven again.
	    The game ends when there are no tiles left in the bag."""

	    instructions_window = Toplevel(self.__root, height=800, width=700)
	    instructions_window.title("Instructions")
	    instructions_label = Label(instructions_window, text=text, justify=LEFT)
	    instructions_label.place(height=750, width=650)
	    close_button = Button(instructions_label, text="Close", 
	    	command=instructions_window.destroy)
	    close_button.place(x=325, y=600)

	def exit(self):
		self.__root.update()
		self.__root.destroy()
		print("Thanks for playing!\n\t-Chaz & Isaiah")
		sys.exit(0)

if __name__ == '__main__':
	root = Tk()
	game = Game(root)
	game.main()
	# root.after(0, game.main)