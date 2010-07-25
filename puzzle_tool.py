#!/usr/bin/env python2.6
# vim:set sw=2 ts=2 sts=2 expandtab:

import optparse
import pieces
import pprint
import matcher
import cPickle

def display_piece(i, piece):
  print "Piece %d:" % i
  print pieces.visualize_piece(piece)

def main():
  parser = optparse.OptionParser()
  parser.add_option("-s", "--show", dest="show",
      default=False, action="store_true",
      help="Show all the pieces.")
  parser.add_option("-p", "--piece", dest="piece",
      default=None,
      help="Piece number (0--12)")
  parser.add_option("-l", "--solve", dest="solve",
      default=False, action="store_true",
      help="Solve the puzzle.")
  options, args = parser.parse_args()
  if options.show:
    if options.piece is not None:
    	piece_no = int(options.piece)
    	list_piece = pieces.make_list(pieces.PIECES[piece_no])
    	display_piece(piece_no, list_piece)
    else:
      for i, piece in enumerate(pieces.PIECES):
        list_piece = pieces.make_list(piece)
        display_piece(i, list_piece)
  if options.solve:
    m = matcher.RecursiveBacktrackingSearch()
    m.RecursiveBacktrackingSearch(m.Root(m.data))
    cPickle.dump(m.solutions, open("solutions.pickle", "w"))
    fd = open("solutions.py", "w")
    fd.write(pprint.pformat(m.solutions))
    fd.close()


if __name__ == '__main__':
  main()
