#!/usr/bin/env python2.6

import optparse
import pieces
import pprint

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


if __name__ == '__main__':
  main()
