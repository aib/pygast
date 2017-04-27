import inspect
import random
import types

all_nodes = []
all_nodes_by_group = {}

def get_random_node(picker, clause):
	def random_node(groups):
		group = random.choice(list(groups.keys()))
		ntype = random.choice(groups[group])
		return Node(ntype)

	if picker is None:
		picker = random_node

	node = picker(all_nodes_by_group)
	while not clause(node):
		node = picker(all_nodes_by_group)
	return node

def get_random_nonleaf_node(picker):
	return get_random_node(picker, lambda n: n.count_children() > 0)

def get_random_leaf_node(picker):
	return get_random_node(picker, lambda n: n.count_children() == 0)

class Counter:
	def __init__(self):
		self.count = 0
	def increment(self):
		self.count += 1

class Tree:
	def __init__(self, picker=None):
		self.picker = picker
		self.root = get_random_leaf_node(self.picker)

	def syntax(self):
		return self.root.syntax()

	def nodes(self):
		def get_nodes(node):
			nodes = [node]
			if node is not None and len(node.children) > 0:
				for c in node.children:
					nodes += get_nodes(c)
			return nodes
		return get_nodes(self.root)

	def grow(self):
		old_node = random.choice(self.nodes())
		new_node = get_random_nonleaf_node(self.picker)

		new_node.parent = old_node.parent
		new_node.children = [old_node]
		while len(new_node.children) < new_node.count_children():
			c = get_random_leaf_node(self.picker)
			c.parent = new_node
			new_node.children.append(c)
		random.shuffle(new_node.children)

		old_node.parent = new_node

		if new_node.parent is not None:
			new_node.parent.replace_child(old_node, new_node)
		else:
			self.root = new_node

	def prune(self):
		nonleaf_nodes = list(filter(lambda n: n.count_children() > 0, self.nodes()))
		if len(nonleaf_nodes) == 0:
			return

		node = random.choice(nonleaf_nodes)
		child = random.choice(node.children)

		child.parent = node.parent

		if node.parent is not None:
			node.parent.replace_child(node, child)
		else:
			self.root = child

class Node:
	class Data(object):
		pass
	class Counter:
		def __init__(self):
			self.count = 0
		def increment(self):
			self.count += 1

	def __init__(self, node_type):
		self.type = node_type
		self.data = self.Data()
		if hasattr(node_type, 'init'):
			node_type.init(self.data)
		self.parent = None
		self.children = [None] * self.count_children()

	def count_children(self):
		c = self.Counter()
		self._call_syntax(c.increment)
		return c.count

	def _call_syntax(self, print_func):
		replace = lambda l, o, n: list(map(lambda e: n if e == o else e, l))
		args = inspect.getfullargspec(self.type.syntax).args
		args = replace(args, 'c', print_func)
		args = replace(args, 'd', self.data)
		return self.type.syntax(*args)

	def replace_child(self, old_child, new_child):
		self.children = list(map(lambda c: new_child if c == old_child else c, self.children))

	def syntax(self):
		cgen = iter(self.children)
		return self._call_syntax(lambda: '(' + next(cgen).syntax() + ')')

	def __repr__(self):
		return "Node(%s)" % (self.type,)

class NodeType:
	def __init__(self, name, group):
		self.name = name
		self.group = group

	def __repr__(self):
		return "%s" % (self.name,)

def node(group=''):
	def wrapper(cls):
		name = cls.__name__
		node_type = NodeType(name, group)

		if hasattr(cls, 'init'):
			node_type.init = cls.init
		node_type.syntax = cls.syntax

		all_nodes.append(node_type)
		if group not in all_nodes_by_group:
			all_nodes_by_group[group] = []
		all_nodes_by_group[group].append(node_type)

		return node_type
	return wrapper
