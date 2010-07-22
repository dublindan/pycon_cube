#!/usr/bin/env python2.6

import operator
import optparse
import pprint
import unittest
import sys
from rotate import Rotator
import re

RAW_PIECES = [
    ('x...', '....', '....', '....', # 0
     'xx..', '....', '....', '....',
     '.xx.', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.xx.', '....', '....', '....', # 1
     'xx..', 'x...', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.x..', '.x..', '....', '....', # 2
     'xxx.', '....', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.xx.', '.x..', '....', '....', # 3
     'xx..', '....', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.x..', '....', '....', '....', # 4
     'xxx.', 'x...', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('xxx.', 'x...', '....', '....', # 5
     'x...', '....', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('x...', 'x...', '....', '....', # 6
     'xxx.', '....', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.x..', '....', '....', '....', # 7
     'xxx.', '....', '....', '....',
     '.x..', '....', '....', '....',
     '....', '....', '....', '....'),

    ('xx..', '....', '....', '....', # 8
     'x...', 'x...', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('..x.', '....', '....', '....', # 9
     'xxx.', 'x...', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('xxx.', '.x..', '....', '....', # 10
     '.x..', '....', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.x..', '.xx.', '....', '....', # 11
     'xx..', '....', '....', '....',
     '....', '....', '....', '....',
     '....', '....', '....', '....'),

    ('.x..', '....', '....', '....', # 12
     'xxx.', '....', '....', '....',
     'x...', '....', '....', '....',
     '....', '....', '....', '....'),
]

def show(pieces):
    """
    Take in raw pieces and represent them as x's and dots.
    """
    for i, piece in enumerate(pieces):
        print '%d:' % (i+1), piece


def shuffle_list(l, idxs):
  """Shuffles elements of a list based on index specs.
  
  Lengths of l and idx must be the same.
  """
  return [l[idxs[i]] for i in range(len(l))]



def visual_def_to_str(piece_def):
  idxs = reduce(operator.add, [range(x, x + 16, 4) for x in range(0, 4)])
  return "".join(reduce(operator.add, shuffle_list(piece_def, idxs)))


def parse_notation_2(input):
  """Reshuffles the '..xx' strings from the visual order to the binary
  order."""
  assert len(input) == 16
  signif_def = visual_def_to_str(input)
  # print signif_def
  piece_num = make_binary(signif_def)
  # print bin(piece_num)[2:]
  return piece_num


def visualize_piece(piece, spacing=" "):
  """Shows something that humans can interpret spacially."""
  s = ['X ' if x else '. ' for x in piece]
  out = []
  for i in range(0, 16, 4):
    for j in range(0, 64, 16):
      out.append("".join(s[i+j:i+j+4] + [spacing]))
    out.append("\n")
  return "".join(out)


def make_binary(raw_piece):
    val = 0L
    for i, char in enumerate(raw_piece, start=1):
        if char == 'x':
            val += 2**(64-i)
    return val

def make_list(piece):
    str_piece = bin(piece)[2:]
    str_piece = '0' * (64 - len(str_piece)) + str_piece
    l = [bool(int(c)) for c in str_piece]
    return l

PIECES = [parse_notation_2(x) for x in RAW_PIECES]
collision = lambda x, y: x & y

def total_collision_count(pieces):
    """
    Loop over pieces and return a total collision count.
    """
    cube = 0
    collision_count = 0
    for i, piece in enumerate(pieces):
        c = bin(collision(cube, piece)).count('1')
        if c:
            print "%d has %d collisions" % (i+1, c)
            collision_count += c
        cube |= piece
    return collision_count


class AllTheWays(object):

  def __init__(self):
    self.r = Rotator()

  def all_rotations(self, piece):
    """All rotations of a piece.  Accepts the list format.

    http://www.euclideanspace.com/maths/discrete/groups/categorise/finite/cube/index.htm
    """
    # This variable represents all the 24 rotations of a piece.
    data = """i x y xx  xy  yx  yy  xxx xxy xyx xyy yxx yyx yyy
    xxxy  xxyx  xxyy  xyxx xyyy  yxxx  yyyx  xxxyx xyxxx xyyyx"""
    rotation_defs = re.split(r"\s+", data)
    rotations = []
    functions = {
        'i': lambda x: x, # Identity
        'x': self.r.RotatePieceX,
        'y': self.r.RotatePieceY,
        'z': self.r.RotatePieceZ,
    }
    for rotation_def in rotation_defs:
      rotated = piece
      for rotation_dir in rotation_def:
      	rotated = functions[rotation_dir](rotated)
      rotations.append(tuple(rotated))
    return rotations

  def all_positions(self, piece):
    """All positions of a piece.  Accepts the list format.

    The algorithm:
    - move the piece near the (0, 0, 0) corner
    - while true # x
    	- while true # y
    		- while true # z
    			- record the position
          - if can move along z
          	- move
            - else break z
        - if can move along y
        	- move
          - else break y
      - if can move along x
      	- move
        - else break
    """
    pass



class MakeListUnitTest(unittest.TestCase):
  
  def testMakeList_1(self):
    piece = 0L
    self.assertEqual([False] * 64, make_list(piece))

  def testMakeList_2(self):
    piece = 1L
    self.assertEqual([False] * 63 + [True], make_list(piece))

  def testMakeList_3(self):
    piece = 255L
    self.assertEqual([False] * 56 + [True] * 8, make_list(piece))

  def test_make_binary(self):
    r =  '.xx.xx..............x...........................................'
    e = 0b0110110000000000000010000000000000000000000000000000000000000000
    self.assertEqual(e, make_binary(r))


class AllTheWaysUnitTest(unittest.TestCase):

  def test_1(self):
    a = AllTheWays()
    piece = [0] * 64
    piece[0] = 1
    piece[1] = 1
    piece[2] = 1
    rotations = a.all_rotations(piece)
    self.assertEqual(24, len(set(rotations)))


class ShufflingUnitTest(unittest.TestCase):

  def test_1(self):
    l = ['a', 'b']
    idxs = [1, 0]
    self.assertEqual(['b', 'a'], shuffle_list(l, idxs))

  def test_2(self):
    l = ['a', 'b', 'c', 'd']
    idxs = [3, 0, 1, 2]
    self.assertEqual(['d', 'a', 'b', 'c'], shuffle_list(l, idxs))


class ParseUnitTest(unittest.TestCase):

  def test_visual_to_str(self):
    data = RAW_PIECES[0]
    expected = ('x...xx...xx' + '.' * 53)
    self.assertEqual(expected, visual_def_to_str(data))

  def test_parse_notation_2(self):
    p = parse_notation_2(RAW_PIECES[0])

  def test_visualize_8(self):
    expected = """X X . .  . . . .  . . . .  . . . .  
X . . .  X . . .  . . . .  . . . .  
. . . .  . . . .  . . . .  . . . .  
. . . .  . . . .  . . . .  . . . .  
"""
    data = PIECES[8]
    result = visualize_piece(make_list(data))
    self.assertEqual(expected, result)

  def test_visualize_11(self):
    expected = """. X . .  . X X .  . . . .  . . . .  
X X . .  . . . .  . . . .  . . . .  
. . . .  . . . .  . . . .  . . . .  
. . . .  . . . .  . . . .  . . . .  
"""
    data = PIECES[11]
    result = visualize_piece(make_list(data))
    self.assertEqual(expected, result)


def main():
  """Can be substituted for unittest.main() to run other things."""
  parser = optparse.OptionParser()
  parser.add_option("-s", "--show", dest="show",
                    default=False, action="store_true",
                    help="Show the pieces")
  parser.add_option("-c", "--collisions", dest="collisions",
                    default=False, action="store_true",
                    help="Show the collisions")
  parser.add_option("-t", "--test", dest="test",
                    default=False, action="store_true",
                    help="Run tests")
  options, args = parser.parse_args()
  if options.show:
    pprint.pprint(make_list(PIECES))
    show(PIECES)
  if options.collisions:
    list_pieces = make_list(PIECES)
    print "Total collisions: %d" % total_collision_count(pieces)


if __name__ == '__main__':
  unittest.main()
