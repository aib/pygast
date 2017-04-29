import itertools
import threading

import numpy as np

class spacefill2d1q:
	RIGHT = (lambda x: x+1, lambda y: y)
	UP    = (lambda x: x, lambda y: y + 1)
	LEFT  = (lambda x: x-1, lambda y: y)
	DOWN  = (lambda x: x, lambda y: y-1)

	def __init__(self):
		self.x = 0
		self.y = 1
		self.arm_length = 0
		self.arm_position = -1
		self.dir = self.DOWN

	def __iter__(self):
		while True:
			self._move(self.dir)
			yield (self.x, self.y)

			self.arm_position += 1
			if self.arm_position == self.arm_length:
				self.arm_position = 0

				if self.dir == self.DOWN:
					self._move(self.RIGHT)
					yield (self.x, self.y)

					self.dir = self.UP
					self.arm_length += 1

				elif self.dir == self.UP:
					self.dir = self.LEFT

				elif self.dir == self.LEFT:
					self._move(self.UP)
					yield (self.x, self.y)

					self.dir = self.RIGHT
					self.arm_length += 1

				elif self.dir == self.RIGHT:
					self.dir = self.DOWN

				else:
					raise AssertionError()

	def _move(self, mdir):
		self.x, self.y = mdir[0](self.x), mdir[1](self.y)

class FIFO:
	def __init__(self, size, dtype=None):
		self.lock = threading.Lock()
		self.data = np.empty(0, dtype)
		self.size = size
		self.count = 0

	def can_put(self, put_length):
		return self.count + put_length <= self.size

	def put(self, put_data):
		with self.lock:
			assert(self.can_put(len(put_data)))
			self.data = np.append(self.data, put_data)
			self.count += len(put_data)

	def can_get(self, get_length):
		return self.count >= get_length

	def get(self, get_length):
		with self.lock:
			assert(self.can_get(get_length))
			get_data = self.data[0:get_length]
			self.data = self.data[get_length:]
			self.count -= get_length
			return get_data
