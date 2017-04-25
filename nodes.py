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


@tree.node('trigonometry')
class sin:
	def syntax(c):
		return "sin(TAU * %s)" % (c(),)
