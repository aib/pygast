#!/usr/bin/env python3

import numpy as np
import vispy.app

vertex = """
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

fragment = """
varying vec2 v_texcoord;

void main()
{
	gl_FragColor = vec4(v_texcoord.st, 0, 1);
}
"""

class Canvas(vispy.app.Canvas):
	def __init__(self):
		vispy.app.Canvas.__init__(self, size=(800, 600))
		vispy.gloo.set_state(clear_color='black')
		self.program = vispy.gloo.Program(vertex, fragment)

		self.view = vispy.util.transforms.translate((0, 0, -5))
		self.model = np.eye(4, dtype=np.float32)

		self.quad = np.array([
			([-1, -1, 0], [0, 0]),
			([-1, +1, 0], [0, 1]),
			([+1, +1, 0], [1, 1]),
			([+1, -1, 0], [1, 0])
		], dtype=[('a_position', np.float32, 3), ('a_texcoord', np.float32, 2)])

		self.on_resize(vispy.app.canvas.ResizeEvent('resize', self.size))
		self.show()

	def on_resize(self, event):
		(width, height) = event.physical_size
		vispy.gloo.set_viewport(0, 0, width, height)
		self.projection = vispy.util.transforms.perspective(45.0, width / height, 0.01, 1000.0)

	def on_draw(self, event):
		vispy.gloo.clear()

		self.program['u_model'] = self.model
		self.program['u_view'] = self.view
		self.program['u_projection'] = self.projection

		self.program.bind(vispy.gloo.VertexBuffer(self.quad))
		self.program.draw('triangles', vispy.gloo.IndexBuffer(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)))

		self.update()

def main():
	c = Canvas()
	vispy.app.run()

if __name__ == '__main__':
	main()
