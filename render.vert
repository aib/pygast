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
