#!/usr/bin/env python2.6

import operator
import optparse
import pprint
import unittest
import itertools
import copy
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

MOVING_TEST_DATA = {
    "base": 
        ('....', '....', '....', '....',
         '....', '..x.', '....', '....',
         '....', '.xx.', '..x.', '....',
         '....', '....', '....', '....'),
    "left": 
        ('....', '....', '....', '....',
         '....', '.x..', '....', '....',
         '....', 'xx..', '.x..', '....',
         '....', '....', '....', '....'),
    "right": 
        ('....', '....', '....', '....',
         '....', '...x', '....', '....',
         '....', '..xx', '...x', '....',
         '....', '....', '....', '....'),
    "forward": 
        ('....', '..x.', '....', '....',
         '....', '.xx.', '..x.', '....',
         '....', '....', '....', '....',
         '....', '....', '....', '....'),
    "back": 
        ('....', '....', '....', '....',
         '....', '....', '....', '....',
         '....', '..x.', '....', '....',
         '....', '.xx.', '..x.', '....'),
    "up": 
        ('....', '....', '....', '....',
         '....', '....', '..x.', '....',
         '....', '....', '.xx.', '..x.',
         '....', '....', '....', '....'),
    "down": 
        ('....', '....', '....', '....',
         '..x.', '....', '....', '....',
         '.xx.', '..x.', '....', '....',
         '....', '....', '....', '....'),
}

class Mover(object):
    # Move up is easy.  We discard the top part (48-63), and fill the
    # bottom with zeros.
    MOVE_UP = range(48, 64) + range(0, 48)
    MASK_UP = [False] * 48 + [True] * 16
    ROTATIONS = {
            # (axis, direction): (pre_rotate, post_rotate),
            (0, 0): ("yyy", "y"),
            (0, 1): ("y", "yyy"),
            (1, 0): ("xxx", "x"),
            (1, 1): ("x", "xxx"),
            (2, 0): ("i", "i"),
            (2, 1): ("xx", "xx"),
    }

    def __init__(self):
        self.r = Rotator()
        self.rotation_masks = self.get_rotation_masks()

    def get_rotation_masks(self):
        """Generate all rotation masks."""
        rotation_masks = {}
        for rot_id, defs in self.ROTATIONS.iteritems():
            rotated_mask = self.r.RotateByDef(self.MASK_UP, defs[1])
            rotation_masks[rot_id] = rotated_mask
        return rotation_masks

    def _shift_up(self, piece_list):
        return shuffle_list(piece_list, self.MOVE_UP)

    def move(self, piece_list, axis, direction):
        """Move a piece in designated direction.

        The idea is to combine a simple shift up, defined in
        self._shift_up, and rotations, implemented in rotate.Rotator.

        Args:
            piece_list: A piece in list format
            axis: 0 for X, 1 for Y, 2 for Z
            direction: 0 for left, forward or up,
                       1 for right, back or down
        Returns:
            A tuple, with values:
            move_valid, new_piece
        """
        # Need to get a rotated piece, 6 combinations.
        rotation_mask = self.rotation_masks[(axis, direction)]
        # This would be an AND operation if we were operating on number
        # representations.
        move_valid = not any(
                x and y
                for x, y in itertools.izip(piece_list, rotation_mask))
        rotation_def_1 = self.ROTATIONS[(axis, direction)][0]
        rotation_def_2 = self.ROTATIONS[(axis, direction)][1]
        rotated = self.r.RotateByDef(piece_list, rotation_def_1)
        shifted = self._shift_up(rotated)
        rotated_back = self.r.RotateByDef(shifted, rotation_def_2)
        return move_valid, rotated_back



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
  piece_num = parse_raw_piece(signif_def)
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


def parse_raw_piece(raw_piece):
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

def list_to_long(piece):
    str_format = "".join(['1' if x else '0' for x in piece])
    long_format = long(str_format, 2)
    return long_format

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

    # http://www.euclideanspace.com/
    # maths/discrete/groups/categorise/finite/cube/index.htm
    ROTATION_DEF_DATA = """i x y xx  xy  yx  yy  xxx xxy xyx xyy yxx yyx yyy
        xxxy  xxyx  xxyy  xyxx xyyy  yxxx  yyyx  xxxyx xyxxx xyyyx"""

    def __init__(self):
        self.r = Rotator()

    def all_rotations(self, piece):
        """All rotations of a piece.  Accepts the list format.

        """
        # This variable represents all the 24 rotations of a piece.
        rotation_defs = re.split(r"\s+", self.ROTATION_DEF_DATA)
        rotations = []
        for rotation_def in rotation_defs:
          rotated = self.r.RotateByDef(piece, rotation_def)
          rotations.append(tuple(rotated))

        return rotations

    def all_positions_dim(self, m, piece_list, dim, direction=1):
        """Find all positions along the given dimension."""
        assert dim in range(3)
        positions = []
        cur_pos = piece_list
        while True:
            positions.append(cur_pos)
            move_valid, tmp_moved = m.move(cur_pos, dim, direction)
            if move_valid:
                cur_pos = tmp_moved
            else:
                break
        return positions

    def all_positions(self, piece_list):
        """All positions of a piece.  Accepts the list format.

        The algorithm:
        - center -> all X positions
          all X positions -> all X + Y positions
        """
        # Move to a corner
        m = Mover()
        cornered = piece_list
        for dim in range(3):
            while True:
                move_valid, tmp_moved = m.move(cornered, dim, 0)
                if move_valid:
                    cornered = tmp_moved
                else:
                    break
        positions = [cornered]
        # Now, iterate through dimensions, finding all the positions.
        for dim in range(3):
            new_positions = []
            for position in positions:
                new_positions.extend(
                        self.all_positions_dim(m, position, dim))
            positions = new_positions
        return positions

    def all_positions_and_rotations(self, piece):
        """Find all positions and rotations of a piece."""
        assert len(piece) == 64
        all_rotations = self.all_rotations(piece)
        positions = []
        for rotation in all_rotations:
            positions.extend(
                    self.all_positions(rotation))
        return positions

    def all_pieces(self):
        return [make_list(parse_notation_2(x)) for x in RAW_PIECES]

    def MatcherData(self):
        pieces = self.all_pieces()
        a_listformat = [
                self.all_positions_and_rotations(x)
                for x in pieces]
        a_numformat = []
        for piece_rotations_listformat in a_listformat:
            a_numformat.append(
                    [list_to_long(x) for x in piece_rotations_listformat])
        return a_numformat
        

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

  def test_parse_raw_piece(self):
    r =  '.xx.xx..............x...........................................'
    e = 0b0110110000000000000010000000000000000000000000000000000000000000
    self.assertEqual(e, parse_raw_piece(r))


class AllTheWaysUnitTest(unittest.TestCase):

    def setUp(self):
        self.a = AllTheWays()

    def test_1(self):
        piece = [0] * 64
        piece[0] = 1
        piece[1] = 1
        piece[2] = 1
        rotations = self.a.all_rotations(piece)
        self.assertEqual(24, len(set(rotations)))

    def testAllPositions(self):
        piece = [0] * 64
        piece[37] = 1
        piece[38] = 1
        piece[26] = 1
        self.a.all_positions(piece)

    def testMatcherData(self):
        # print "MatcherData:", self.a.MatcherData()[0]
        pass


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


class MoverUnitTest(unittest.TestCase):
    """Using list representations for the transformations."""

    def setUp(self):
        self.m = Mover()

    def data(self, name):
        d = MOVING_TEST_DATA[name]
        piece_num = parse_notation_2(d)
        return make_list(piece_num)

    def test_shift_up(self):
        """Test of the fundamental shifting code."""
        p = self.data("base")
        expected = self.data("up")
        self.assertEqual(expected, self.m._shift_up(p))

    def testMoveUp(self):
        p = self.data("base")
        expected = (True, self.data("up"))
        self.assertEqual(expected, self.m.move(p, 2, 0))

    def testMoveValid(self):
        p = self.data("up")
        move_valid, unused = self.m.move(p, 2, 0)
        self.assertEqual(False, move_valid)

    def testMoveValidLeft(self):
        p = self.data("left")
        move_valid, unused = self.m.move(p, 0, 0)
        self.assertEqual(False, move_valid)

    def testMoveRight(self):
        p = self.data("base")
        expected = (True, self.data("right"))
        result = self.m.move(p, 0, 1)
        self.assertEqual(expected, result)

    def testMoveBack(self):
        p = self.data("base")
        expected = (True, self.data("back"))
        result = self.m.move(p, 1, 1)
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
