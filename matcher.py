#!/usr/bin/env python2.6
# coding=utf-8

import pieces
from possibility import Possibility

class Matcher(object):

	def __init__(self):
		self.solution = (2 ** 64 - 1)

	def match(self, possibility):
		sum = 0b00
		for piece in possibility.pieces:
			sum ^= piece
		return sum == self.solution
	
	def areTheyFitting(self, piece1, piece2):
		return (piece1 & piece2) == 0

	def evaluate(self, possibility):
		best_fit = {}
		for piece in possibility.pieces:
			best_fit[piece] = [piece]
			for test in possibility.pieces:
				if (self.areTheyFitting(piece, test) and self.doesItFitWithGroup(test, best_fit[piece])):
					best_fit[piece].append(test)
								
		the_best = max([len(s) for s in best_fit.values()])
		possibility.pieces_fitted = [s for x, y in best_fit.items() if the_best == len(y)][0]	

	def doesItFitWithGroup(self, piece, group): 			
		for item in group:
			if not self.areTheyFitting(item, piece):
				return False
		return True


class RecursiveBacktrackingSearch(object):
    """
    Probably will implement the following:

    procedure bt(c)
      if reject(P,c) then return
      if accept(P,c) then output(P,c)
      s ← first(P,c)
      while s ≠ Λ do
        bt(s)
        s ← next(P,s)

    Source:
    http://en.wikipedia.org/wiki/Backtracking#Pseudocode
    """

    def __init__(self, data=None, bits=64):
        self.bits = bits
        self.data = data
        if not self.data:
            self.data = pieces.AllTheWays().MatcherData()
        self.solutions = []
        self.length = len(self.data)
        self.last = [(len(x) - 1) for x in self.data]
    
    def Root(self, P):
        "Return the partial candidate at the root of the search tree"
        return []

    def Reject(self, P, c):
        """Return true only if the partial candidate c is not worth
        completing"""
        # print "Reject(%s)" % repr(c)
        # Check if the indexes aren't out of bounds.
        if self.BeyondScope(P, c):
            # Beyond scope, rejecting.
            return True
        if len(c) == 0:
            # Empty solution, not rejecting.
            return False
        if len(c) == 1:
            # One piece, not rejecting.
            return False
        n = P[0][c[0]]
        for el_idx, pos_idx in enumerate(c):
            n &= P[el_idx][pos_idx]
        if n > 0L:
            # print "%s: Overlapping bits, rejecting." % repr(n)
            return True
        return False

    def Accept(self, P, c):
        """return true if c is a solution of P, and false otherwise"""
        n = 0L
        for el_idx, pos_idx in enumerate(c):
            n |= P[el_idx][pos_idx]
        return n == (2 ** self.bits - 1)

    def First(self, P, c):
        """generate the first extension of candidate c."""
        # print "First(%s) ==> %s" % (repr(c), repr(c + [0]))
        return c + [0]

    def Next(self, P, s):
        """generate the next alternative extension of a candidate, after
        the extension s."""
        answer = s[:-1] + [s[-1] + 1]
        # print "Next(%s) ==> %s" % (repr(s), answer)
        return answer

    def Output(self, P, c):
        """use the solution c of P, as appropriate to the application"""
        self.solutions.append(c)

    def RecursiveBacktrackingSearch(self, c, P=None):
        # print "RecursiveBacktrackingSearch(%s)" % (repr(c))
        if not P:
            P = self.data
        if self.Reject(P, c):
            return
        if self.Accept(P, c):
            self.Output(P, c)
        s = self.First(P, c)
        while not self.BeyondScope(P, s):
            self.RecursiveBacktrackingSearch(s)
            s = self.Next(P, s)

    def BeyondScope(self, P, s):
        for i, idx in enumerate(s):
            if i >= len(P):
                return True
            if idx >= len(P[i]):
                # print "%s >= len(P[%s])" % (idx, i)
                return True
        return False
