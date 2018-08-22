from __future__ import division

class Player(object):
	def __init__(self, root):
		self._selected_tile = None
		self._root = root
		self._rack = []
		self._points = 0

	def get_selected_tile(self):
		return self._selected_tile

	def unselect_tile(self):
		self._selected_tile = None

	def get_rack_size(self):
		return len(self._rack)

	def get_points(self):
		return self._points

	def add_points(self,points):
		self._points += points
		return self._points

	def add_to_rack(self,tile,allow_label):
		if len(self._rack) < 7:
			self._rack.append(tile)
			return True
		else:
			return False

	def remove_from_rack(self,tile):
		if tile in self._rack:
			self._rack.remove(tile)
			return True
		else:
			return False

	def __str__(self):
		out = []
		for t in self._rack:
			out.append(t.get_value())
		return ", ".join(out)