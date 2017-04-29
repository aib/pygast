uniform sampler2D u_texture;

varying vec2 v_texcoord;

void main()
{
	gl_FragColor = vec4(texture2D(u_texture, v_texcoord.st).rgb, 1);
}
