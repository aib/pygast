#define TAU 6.283185307179586

uniform float u_time;

varying vec2 v_texcoord;

vec3 hsl2rgb(vec3 hsl) {
	hsl.z = abs(mod(0.5 - hsl.z, 2) - 1);
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
	float t4 = %(tree4)s;
/*
	float xx = (8 * x) - 4;
	float yy = (8 * y) - 4;
	t1 = t / 100;
	t2 = xx;
	t3 = yy;
*/
	gl_FragColor = vec4(hsl2rgb(vec3(t1, t2, t3)), t4);
}
