from tile import Tile

import random

class Bag:
	def __init__(self):
		self.__tiles = []

		self.add(Tile('E'),12)
		self.add(Tile('A'),9)
		self.add(Tile('I'),9)
		self.add(Tile('O'),8)
		self.add(Tile('N'),6)
		self.add(Tile('R'),6)
		self.add(Tile('T'),6)
		self.add(Tile('L'),4)
		self.add(Tile('S'),4)
		self.add(Tile('U'),4)
		self.add(Tile('D'),4)
		self.add(Tile('G'),3)
		self.add(Tile('B'),2)
		self.add(Tile('C'),2)
		self.add(Tile('M'),2)
		self.add(Tile('P'),2)
		self.add(Tile('F'),2)
		self.add(Tile('H'),2)
		self.add(Tile('V'),2)
		self.add(Tile('W'),2)
		self.add(Tile('Y'),2)
		# self.add(Tile(' '),2)
		self.add(Tile('K'),1)
		self.add(Tile('J'),1)
		self.add(Tile('X'),1)
		self.add(Tile('Q'),1)
		self.add(Tile('Z'),1)

		random.shuffle(self.__tiles)

	def add(self, tile, amt=1):
		if len(self.__tiles) < 100:
			for _ in range(amt):
				self.__tiles.append(tile)
			return True
		else:
			return False

	def remove(self, tile):
		self.__tiles.remove(tile)

	def draw(self):
		return self.__tiles.pop(0)

	def size(self):
		return len(self.__tiles)

	def is_empty(self):
		return len(self.__tiles) == 0