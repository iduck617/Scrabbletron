from Tkinter import *

class Tile:
	POINT_VALUES = {'E':1, 'A':1, 'I':1, 'O':1, 'N':1, 'R':1, 'T':1, 'L':1, 
					'S':1, 'U':1, 'D':2, 'G':2, 'B':3, 'C':3, 'M':3, 'P':3,
					'F':4, 'H':4, 'V':4, 'W':4, 'Y':4, 'K':5, 'J':8, 'X':8,
					'Q':10, 'Z':10, ' ':0}
	DIMENSION = 31

	def __init__(self, char):
		self.__char    = char.upper()
		self.__points  = Tile.POINT_VALUES[self.__char]
		self.__is_blank = self.__char == ' '
		self.__selected = False

	def get_value(self):
		return self.__char

	def display(self):
		subs = {1:u'\u2081', 2:u'\u2082', 3:u'\u2083', 4:u'\u2084', 5:u'\u2085', 
				6:u'\u2086',7:u'\u2087', 8:u'\u2088', 9:u'\u2089', 10:u'\u2081\u2080'}
		return u''+ self.__char + subs[self.__points] if self.__points != 0 else ''

	def get_points(self):
		return self.__points

	def is_blank(self):
		return self.__is_blank

	def is_selected(self):
		return self.__selected

	def toggle(self):
		self.__selected = not self.__selected

	def draw(self, canvas, top_left, bottom_right):
		pass

	def __str__(self):
		return str(self.__char)