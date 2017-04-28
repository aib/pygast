#!/usr/bin/env python3

import tree
import nodes

import numpy as np
import pyaudio
import scipy.misc
import vispy.app

import array
import random
import time

class Canvas(vispy.app.Canvas):
	def __init__(self):
		self._init_trees()

		vispy.app.Canvas.__init__(self, size=(1024, 768), keys='interactive')
		vispy.gloo.set_state(clear_color='black')

		self.fbotex = vispy.gloo.Texture2D((self.size[1], self.size[0], 4), 'rgba')
		self.fbo = vispy.gloo.FrameBuffer(self.fbotex)

		self.view = vispy.util.transforms.translate((0, 0, -5))
		self.model = np.eye(4, dtype=np.float32)

		self.quad = np.array([
			([-1, -1, 0], [0, 0]),
			([-1, +1, 0], [0, 1]),
			([+1, +1, 0], [1, 1]),
			([+1, -1, 0], [1, 0])
		], dtype=[('a_position', np.float32, 3), ('a_texcoord', np.float32, 2)])

		self.save = False

		self.update_program()

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
			pix = self.fbo.read('color')

		if self.save:
			self._do_save(pix, frame_time)
			self.save = False

		vispy.gloo.clear()
		self.render_from_texture['u_model'] = self.model
		self.render_from_texture['u_view'] = self.view
		self.render_from_texture['u_projection'] = self.projection
		self.render_from_texture['u_texture'] = self.fbotex
		self.render_from_texture.bind(vispy.gloo.VertexBuffer(self.quad))
		self.render_from_texture.draw('triangles', vispy.gloo.IndexBuffer(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)))

		self.update()

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

	def on_audio_stream(self, in_data, frame_count, time_info, status):
		data = list(map(lambda n: random.random(), range(frame_count)))
		adata = array.array('H', map(lambda x: int(65535 * x), data))
		return (adata.tobytes(), pyaudio.paContinue)

	def _init_trees(self):
		self.trees = [tree.Tree(), tree.Tree(), tree.Tree(), tree.Tree()]

	def _do_save(self, pix, frame_time):
		fn = "pygast_%s_t%.3f.png" % (time.strftime("%Y%m%d_%H%M%S"), frame_time)
		scipy.misc.imsave(fn, pix[:,:,0:3])

def main():
	c = Canvas()
	pa = pyaudio.PyAudio()

	stream = pa.open(format=pa.get_format_from_width(2, False), channels=1, rate=44100, output=True, stream_callback=c.on_audio_stream)

	stream.start_stream()
	vispy.app.run()

if __name__ == '__main__':
	main()
