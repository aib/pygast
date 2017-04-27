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
	def eval(d):
		return d.val


@tree.node('variables')
class x:
	def syntax():
		return "x"
	def eval(e):
		return e.x

@tree.node('variables')
class y:
	def syntax():
		return "y"
	def eval(e):
		return e.y

@tree.node('variables')
class t:
	def syntax():
		return "t"
	def eval(e):
		return e.t


@tree.node('arithmetic')
class mul:
	def syntax(c):
		return "%s * %s" % (c(), c())
	def eval(c):
		return c() * c()

@tree.node('arithmetic')
class add:
	def syntax(c):
		return "%s + %s" % (c(), c())
	def eval(c):
		return c() + c()

@tree.node('arithmetic')
class mod:
	def syntax(c):
		return "mod(%s, %s)" % (c(), c())
	def eval(c):
		(a, b) = (c(), c())
		return a % b


@tree.node('inversion')
class neg:
	def syntax(c):
		return "-%s" % (c(),)
	def eval(c):
		return -c()

@tree.node('inversion')
class reciprocal:
	def syntax(c):
		return "1 / %s" % (c(),)
	def eval(c):
		return 1 / c()


@tree.node('trigonometry')
class sin:
	def syntax(c):
		return "sin(TAU * %s)" % (c(),)
	def eval(c):
		return math.sin(TAU * c())

@tree.node('interp')
class lerp:
	def syntax(c):
		return "mix(%s, %s, %s)" % (c(), c(), c())
	def eval(c):
		(a, b, t) = (c(), c(), c())
		return a*(1-t) + b*t
