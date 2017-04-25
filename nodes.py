import tree

import math
import random

TAU = 2 * math.pi

@tree.node('constants')
class const:
	def init(d):
		d.val = random.random()
	def syntax(d):
		return "%g" % (d.val,)

@tree.node('constants')
class bigconst:
	def init(d):
		n = random.randint(1, 1000)
		if random.random() < 0.5:
			d.val = n
		else:
			d.val = 1 / n
	def syntax(d):
		return "float(%g)" % (d.val,)


@tree.node('variables')
class x:
	def syntax():
		return "x"

@tree.node('variables')
class y:
	def syntax():
		return "y"

@tree.node('variables')
class t:
	def syntax():
		return "t"


@tree.node('arithmetic')
class mul:
	def syntax(c):
		return "%s * %s" % (c(), c())

@tree.node('arithmetic')
class add:
	def syntax(c):
		return "%s + %s" % (c(), c())

@tree.node('arithmetic')
class mod:
	def syntax(c):
		return "mod(%s, %s)" % (c(), c())


@tree.node('inversion')
class neg:
	def syntax(c):
		return "-%s" % (c(),)

@tree.node('inversion')
class reciprocal:
	def syntax(c):
		return "1 / %s" % (c(),)


@tree.node('trigonometry')
class sin:
	def syntax(c):
		return "sin(TAU * %s)" % (c(),)


@tree.node('periodic')
class sint:
	def syntax(c):
		return "sin(TAU * mod(t, %s))" % (c(),)


@tree.node('interp')
class lerp:
	def syntax(c):
		return "%(a)s*%(t)s + (%(b)s*(1-%(t)s))" % { 'a': c(), 'b': c(), 't': c() }


@tree.node('destructive')
class sign:
	def syntax(c):
		return "sign(%s)" % (c(),)

@tree.node('destructive')
class fract:
	def syntax(c):
		return "fract(%s)" % (c(),)
