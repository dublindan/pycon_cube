#!/usr/bin/env python2.6

"""Moving the pieces.

Direction naming:

Y

^
|
|
+----> X

X axis: left/right
Y axis: forward/back
Z axis: up/down

"""
import pieces
import itertools

right_edge_mask = 2459528346497712128L
bottom_edge_mask = 8444249301319680L


def move_right(piece_binary):
	return piece_binary / 2

def move_down(piece_binary):
	return piece_binary / 16

def can_move_right(piece_binary):
	return (piece_binary&right_edge_mask) == 0

def can_move_down(piece_binary):
	return (piece_binary&bottom_edge_mask) == 0

from pieces import make_binary
import unittest


# class MoveTest(unittest.TestCase):
class DisabledMoveTest(object):
	
	
	def test_move_right(self):
		cube = 'x...'
		binaries = make_binary(cube)
		binaries_results = make_binary('.x..')
		result = move_right(binaries)
		self.assertEquals(result, binaries_results)

	def test_move_right_bigger_piece(self):
		cube = 'x...............................'
		binaries = make_binary(cube)
		expected_result = make_binary('.x...............................')
		result = move_right(binaries)
		self.assertEquals(expected_result, result)

	def test_move_down(self):
		binary = make_binary('....x............')
		expected = make_binary('........x.......')
		result = move_down(binary)
		self.assertEquals(expected, result)

	def test_cannot_move_right(self):
		binary = make_binary('...x.............')
		self.assertFalse(can_move_right(binary))
		
	def test_cannot_move_right_on_edge(self):
		binary = make_binary('...............x')
		self.assertFalse(can_move_right(binary))
		
	def test_can_move_right(self):
		binary = make_binary('..x..............')
		self.assertTrue(can_move_right(binary))
		
	def test_can_move_down(self):
		binary = make_binary('....x............')
		self.assertTrue(can_move_down(binary))
	
		
	def test_cannot_move_down(self):
		binary = make_binary('...............x.')
		self.assertFalse(can_move_down(binary))


if __name__ == '__main__':
	unittest.main()
