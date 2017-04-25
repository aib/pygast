#!/usr/bin/env python3

import tree
import nodes

import numpy as np
import vispy.app

import time

VERTEX = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

attribute vec3 a_position;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;

void main()
{
	gl_Position = u_projection * u_view * u_model * vec4(a_position, 1);
	v_texcoord = a_texcoord;
}
"""

FRAGMENT = """
#define TAU 6.283185307179586

uniform float u_time;

varying vec2 v_texcoord;

void main()
{
	float x = v_texcoord.x;
	float y = v_texcoord.y;
	float t = u_time;

	float t1 = %(tree1)s;
	float t2 = %(tree2)s;
	float t3 = %(tree3)s;

	gl_FragColor = vec4(t1, t2, t3, 1);
}
"""

class Canvas(vispy.app.Canvas):
	def __init__(self):
		self.trees = [tree.Tree(), tree.Tree(), tree.Tree()]

		vispy.app.Canvas.__init__(self, size=(800, 600))
		vispy.gloo.set_state(clear_color='black')

		self.view = vispy.util.transforms.translate((0, 0, -5))
		self.model = np.eye(4, dtype=np.float32)

		self.quad = np.array([
			([-1, -1, 0], [0, 0]),
			([-1, +1, 0], [0, 1]),
			([+1, +1, 0], [1, 1]),
			([+1, -1, 0], [1, 0])
		], dtype=[('a_position', np.float32, 3), ('a_texcoord', np.float32, 2)])

		self.update_program()

		self.on_resize(vispy.app.canvas.ResizeEvent('resize', self.size))
		self.show()

		self.start_time = time.monotonic()

	def update_program(self):
		vertex = VERTEX
		fragment = FRAGMENT % {
			'tree1': self.trees[0].syntax(),
			'tree2': self.trees[1].syntax(),
			'tree3': self.trees[2].syntax()
		}
		self.program = vispy.gloo.Program(vertex, fragment)
		print("--")
		for tree in self.trees:
			print(tree.syntax())

	def on_resize(self, event):
		(width, height) = event.physical_size
		vispy.gloo.set_viewport(0, 0, width, height)
		self.projection = vispy.util.transforms.ortho(-1, 1, -1, 1, 0.01, 1000)

	def on_draw(self, event):
		vispy.gloo.clear()

		self.program['u_model'] = self.model
		self.program['u_view'] = self.view
		self.program['u_projection'] = self.projection
		self.program['u_time'] = time.monotonic() - self.start_time

		self.program.bind(vispy.gloo.VertexBuffer(self.quad))
		self.program.draw('triangles', vispy.gloo.IndexBuffer(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)))

		self.update()

	def on_key_release(self, event):
		if event.key.name == 'Up':
			for tree in self.trees:
				tree.grow()
			self.update_program()

		if event.key.name == 'Down':
			for tree in self.trees:
				tree.prune()
			self.update_program()


def main():
	c = Canvas()
	vispy.app.run()

if __name__ == '__main__':
	main()
