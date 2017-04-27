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

vec3 hsl2rgb(vec3 hsl) {
	hsl.z = abs(mod(1 - hsl.z, 2) - 1);
	hsl.y = abs(mod(hsl.y - 1, 4) - 2) - 1;

	float Hp = hsl.x * 6;
	float C = (1 - abs(2*hsl.z - 1)) * hsl.y;
	float X = C * (1 - abs(mod(Hp, 2) - 1));
	vec3 rgb1;

	if (mod(Hp, 6) <= 1) {
		rgb1 = vec3(C, X, 0);
	} else if (mod(Hp, 6) <= 2) {
		rgb1 = vec3(X, C, 0);
	} else if (mod(Hp, 6) <= 3) {
		rgb1 = vec3(0, C, X);
	} else if (mod(Hp, 6) <= 4) {
		rgb1 = vec3(0, X, C);
	} else if (mod(Hp, 6) <= 5) {
		rgb1 = vec3(X, 0, C);
	} else {
		rgb1 = vec3(C, 0, X);
	}

	float m = hsl.z - C/2;
	return rgb1 + m;
}

void main()
{
	float x = v_texcoord.x;
	float y = v_texcoord.y;
	float t = u_time;

	float t1 = %(tree1)s;
	float t2 = %(tree2)s;
	float t3 = %(tree3)s;
/*
	float xx = (8 * x) - 4;
	float yy = (8 * y) - 4;
	t1 = t / 100;
	t2 = xx;
	t3 = yy;
*/
	gl_FragColor = vec4(hsl2rgb(vec3(fract(t1), t2, t3 + 0.5)), 1);
}
"""

class Canvas(vispy.app.Canvas):
	def __init__(self):
		self.trees = [tree.Tree(), tree.Tree(), tree.Tree()]

		vispy.app.Canvas.__init__(self, size=(1024, 768), keys='interactive')
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
		def new_trees(size):
			self.trees = [tree.Tree(), tree.Tree(), tree.Tree()]
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

		if event.key.name == 'Up':
			for t in self.trees:
				t.grow()
			self.update_program()

		if event.key.name == 'Down':
			for t in self.trees:
				t.prune()
			self.update_program()

def main():
	c = Canvas()
	vispy.app.run()

if __name__ == '__main__':
	main()
