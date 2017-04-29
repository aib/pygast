#!/usr/bin/env python3

import helper
import tree
import nodes

import numpy as np
import pyaudio
import scipy.misc
import vispy.app

import array
import itertools
import math
import random
import time

class Canvas(vispy.app.Canvas):
	AUDIO_SAMPLE_RATE = 44100
	AUDIO_BUFFER_SIZE = AUDIO_SAMPLE_RATE // 10
	AUDIO_GENERATE_SIZE = AUDIO_BUFFER_SIZE // 2

	def __init__(self):
		self._init_trees()

		self.pa = pyaudio.PyAudio()

		vispy.app.Canvas.__init__(self, size=(1024, 768), keys='interactive')
		vispy.gloo.set_state(clear_color='black')

		self.fbotex = vispy.gloo.Texture2D((self.size[1], self.size[0], 4), 'rgba')
		self.fbo = vispy.gloo.FrameBuffer(self.fbotex)
		self.fbopix = None

		self.audio_buffer = helper.FIFO(self.AUDIO_BUFFER_SIZE, dtype='uint8')
		self.audio_buffer_position = 0
		self.audio_indices = list(itertools.islice(helper.spacefill2d1q(), self.audio_buffer.size//2))
		self.audio_indices = self.audio_indices + list(reversed(self.audio_indices))

		self.view = vispy.util.transforms.translate((0, 0, -5))
		self.model = np.eye(4, dtype=np.float32)

		self.quad = np.array([
			([-1, -1, 0], [0, 0]),
			([-1, +1, 0], [0, 1]),
			([+1, +1, 0], [1, 1]),
			([+1, -1, 0], [1, 0])
		], dtype=[('a_position', np.float32, 3), ('a_texcoord', np.float32, 2)])

		self.mute = True
		self.save = False

		self.update_program()

		self.audio_stream = self.pa.open(format=pyaudio.paUInt8, channels=1, rate=self.AUDIO_SAMPLE_RATE, output=True, stream_callback=self.on_audio_stream)
		self.audio_stream.start_stream()

		self.on_resize(vispy.app.canvas.ResizeEvent('resize', self.size))
		self.show()

		self.start_time = time.monotonic()

	def update_program(self):
		with open('passthrough.vert', 'r') as f:
			vertex = f.read()
		with open('render.frag', 'r') as f:
			fragment = f.read() % {
				'tree1': self.trees[0].syntax(),
				'tree2': self.trees[1].syntax(),
				'tree3': self.trees[2].syntax(),
				'tree4': self.trees[3].syntax()
			}
		self.render_to_texture = vispy.gloo.Program(vertex, fragment)

		with open('render.vert', 'r') as f:
			vertex = f.read()
		with open('fromtex.frag', 'r') as f:
			fragment = f.read()
		self.render_from_texture = vispy.gloo.Program(vertex, fragment)

		print("--")
		for tree in self.trees:
			print(tree.syntax())

	def on_resize(self, event):
		(width, height) = event.physical_size
		vispy.gloo.set_viewport(0, 0, width, height)
		self.projection = vispy.util.transforms.ortho(-1, 1, -1, 1, 0.01, 1000)
		self.fbotex.resize((height, width, 4))

	def on_draw(self, event):
		frame_time = time.monotonic() - self.start_time
		with self.fbo:
			vispy.gloo.clear()
			self.render_to_texture['u_time'] = frame_time
			self.render_to_texture.bind(vispy.gloo.VertexBuffer(self.quad))
			self.render_to_texture.draw('triangles', vispy.gloo.IndexBuffer(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)))
			self.fbopix = self.fbo.read('color')

		while self.audio_buffer.can_put(self.AUDIO_GENERATE_SIZE):
			t = (self.audio_buffer_position + np.array(range(self.AUDIO_GENERATE_SIZE))) / self.AUDIO_SAMPLE_RATE
			e = tree.Data()
			e.x = e.y = e.t = t
			ev = self.trees[3].eval(e)
			if not isinstance(ev, np.ndarray): #scalar
				ev = np.repeat(ev, self.AUDIO_GENERATE_SIZE)

			self.audio_buffer_position += self.AUDIO_GENERATE_SIZE
			tput = (np.mod(ev, 1.0) * 255).astype('uint8')
			self.audio_buffer.put(tput)

		if self.save:
			self._do_save(self.fbopix, frame_time)
			self.save = False

		vispy.gloo.clear()
		self.render_from_texture['u_model'] = self.model
		self.render_from_texture['u_view'] = self.view
		self.render_from_texture['u_projection'] = self.projection
		self.render_from_texture['u_texture'] = self.fbotex
		self.render_from_texture.bind(vispy.gloo.VertexBuffer(self.quad))
		self.render_from_texture.draw('triangles', vispy.gloo.IndexBuffer(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)))

		self.update()

	def on_audio_stream(self, in_data, frame_count, time_info, status):
		while not self.audio_buffer.can_get(frame_count):
			time.sleep(0.0001)

		if self.mute:
			return (np.zeros(frame_count, 'float32').tobytes(), pyaudio.paContinue)
		else:
			return (self.audio_buffer.get(frame_count).tobytes(), pyaudio.paContinue)

	def on_key_release(self, event):
		def new_trees(size):
			self._init_trees()
			for i in range(size):
				for t in self.trees:
					t.grow()
			self.update_program()

		if event.key.name == ' ':
			new_trees(0)

		if event.key.name == '1':
			new_trees(3)

		if event.key.name == '2':
			new_trees(5)

		if event.key.name == '3':
			new_trees(10)

		if event.key.name == '4':
			new_trees(20)

		if event.key.name == '5':
			new_trees(50)

		if event.key.name == '6':
			new_trees(100)

		if event.key.name == 'M':
			self.mute = not self.mute

		if event.key.name == 'S':
			self.save = True

		if event.key.name == 'Up':
			for t in self.trees:
				t.grow()
			self.update_program()

		if event.key.name == 'Down':
			for t in self.trees:
				t.prune()
			self.update_program()

	def _init_trees(self):
		self.trees = [tree.Tree(), tree.Tree(), tree.Tree(), tree.Tree()]

	def _do_save(self, pix, frame_time):
		fn = "pygast_%s_t%.3f.png" % (time.strftime("%Y%m%d_%H%M%S"), frame_time)
		scipy.misc.imsave(fn, pix[:,:,0:3])

def main():
	c = Canvas()
	vispy.app.run()

if __name__ == '__main__':
	main()
