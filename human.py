from player import Player
from Tkinter import *

class Human(Player):
	def __init__(self, root):
		self.__rack_labels = {}
		self.__rack_container = None
		super(Human,self).__init__(root)

	def select_tile(self, event, tile):
		clicked_label = event.widget
		for label in self.__rack_labels.values():
			if not (label is clicked_label):
				label.configure(bg='white')
		clicked_label.configure(bg='white' if clicked_label['bg'] == 'blue' else 'blue')
		
		if tile.is_selected():
			self._selected_tile = None
		else:
			if self._selected_tile:
				self._selected_tile.toggle()
			self._selected_tile = tile
		tile.toggle()

	def __add_rack_label(self,tile,allow_label=True):
		if allow_label:
			letter_label = Label(self.__rack_container, text=tile.display(), bd=1, relief=RAISED, bg='white', height=1, width=2)
			letter_label.pack(padx=5,pady=5,side=LEFT)
			letter_label.bind('<Button-1>', lambda event, t=tile : self.select_tile(event, t))
			self.__rack_labels[tile] = letter_label

	def add_to_rack(self,tile,allow_label=False):
		if Player.add_to_rack(self,tile,allow_label):
			self.__add_rack_label(tile,allow_label)
			return True
		else:
			return False

	def remove_from_rack(self,tile):
		if Player.remove_from_rack(self,tile):
			# tile.toggle()
			self.__rack_labels.pop(tile).destroy()
			self._selected_tile = None
			return True
		else:
			return False

	def draw_rack(self):
		self.__rack_container = Frame(self._root)
		for i,tile in enumerate(self._rack):
			self.__add_rack_label(tile)
		self.__rack_container.pack(pady=10)

