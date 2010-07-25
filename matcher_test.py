#!/usr/bin/env python2.6
# coding=utf-8

import unittest
import matcher
from possibility import Possibility

class MatcherTest(unittest.TestCase):

    def setUp(self):
        self.matcher = matcher.Matcher()

    def test_it_should_be_able_to_create_instance(self):
        self.assertEquals(matcher.Matcher, self.matcher.__class__)

    def test_it_should_be_able_to_say_that_this_is_the_solution(self):      
        p = Possibility([
            0b1110000000000000111110000000000011100000000000001110000010000000, 
            0b0000000000110011111001100000000011100000000000001110000101000000, 
            0b0000001110000000111000011000000011100000000000001110001000100000, 
            0b0000110000000000111000000110000011100000000000001110010000010000,
            0b0001000001000000111000000001000011100000000000001110100000001000, 
            0b0000000000001100111000000000110011100000000000001111000000000100, 
            0b0000000000000000111000000000001111100000000000001110000000000010, 
            0b0000000000000000111000000000000011110000000000011110000000000000,
            0b0000000000000000111000000000000011101100000000101110000000000001, 
            0b0000000000000000111000000000000011100010000001001110000000000000, 
            0b0000000000000000111000000000000011100001000010001110000000000000, 
            0b0000000000000000111000000000000011100000100100001110000000000000,
            0b0000000000000000111000000000000011100000011000001110000000000000
        ])
        self.assertEquals(True, self.matcher.match(p))

    def test_it_should_be_able_to_say_that_this_pieces_are_fitting(self):
        self.assertEquals(True, self.matcher.areTheyFitting(
            0b1110000000000000111110000000000000000000000000000000000000000000, 
            0b0001100000000000000001100000000000000000000000000000000000000000
        ))

    def test_it_should_be_able_to_say_which_pieces_are_fitting(self):       
        p = Possibility([
            0b1111100000000000000000000000000000000000000000000000000000000000, 
            0b0000011111000000000000000000000000000000000000000000000000000000, 
            0b0000000000111110000000000000000000000000000000000000000000000000, 
            0b0000000000000001111100000000000000000000000000000000000000000000,
            0b0000000000000000000011111000000000000000000000000000000000000000, 
            0b0000000000000000000000000111110000000000000000000000000000000000, 
            0b0000000000000000000000000000001111100000000000000000000000000000, 
            0b0000000000000000000000000000000000011111100000000000110000000000,
            0b0000000000000000000000000000000000001110000000000000001101000000, 
            0b0000000000000000000000000000000000000000001111110000000011100000, 
            0b0000000000000000000000000000000000000000000001100000000000011100, 
            0b0000000000000000000000000000000000000000000000000000000000000111,
            0b0000000000000000000000000000000000000000011100000000000001110000
        ])
        self.matcher.evaluate(p)
        self.assertEquals([
            0b1111100000000000000000000000000000000000000000000000000000000000, 
            0b0000011111000000000000000000000000000000000000000000000000000000, 
            0b0000000000111110000000000000000000000000000000000000000000000000, 
            0b0000000000000001111100000000000000000000000000000000000000000000,
            0b0000000000000000000011111000000000000000000000000000000000000000,         
            0b0000000000000000000000000111110000000000000000000000000000000000,         
            0b0000000000000000000000000000001111100000000000000000000000000000, 
            0b0000000000000000000000000000000000011111100000000000110000000000,
            0b0000000000000000000000000000000000000000001111110000000011100000, 
            0b0000000000000000000000000000000000000000000000000000000000000111
        ].sort(), p.pieces_fitted.sort())


class RecursiveBacktrackingSearchUnitTest(unittest.TestCase):

    def setUp(self):
        self.data = [
                [0b11110000,
                 0b00110000, ],
                [0b00001110,
                 0b00011110,
                 0b00001111, ],
        ]
        self.rbs = matcher.RecursiveBacktrackingSearch(self.data, 8)

    def testRoot(self):
        self.assertEqual([], self.rbs.Root(self.rbs.data))

    def testFirst_FromEmpty(self):
        self.assertEqual([0], self.rbs.First(self.rbs.data, []))

    def testFirst_FromExisting(self):
        self.assertEqual([0, 0], self.rbs.First(self.rbs.data, [0]))

    def testNext_FromZero(self):
        self.assertEqual([1], self.rbs.Next(self.rbs.data, [0]))

    def testNext_FromZero_TwoElements(self):
        self.assertEqual([0, 1], self.rbs.Next(self.rbs.data, [0, 0]))

    def testNext_Overflow(self):
        """Giving an index beyond the list, which should trigger the
        Reject() function, and terminate this 'branch'."""
        self.assertEqual([2], self.rbs.Next(self.rbs.data, [1]))

    def testReject_OutOfBounds(self):
        self.assertEqual(True, self.rbs.Reject(self.rbs.data, [2]))

    def testReject_Missing(self):
        """Should not reject when pieces are missing."""
        self.assertEqual(False, self.rbs.Reject(self.rbs.data, [0, 0]))

    def testReject_Overlap(self):
        self.assertEqual(True, self.rbs.Reject(self.rbs.data, [0, 1]))

    def testReject_ShouldNotReject(self):
        self.assertEqual(False, self.rbs.Reject(self.rbs.data, [0, 2]))

    def testReject_Empty(self):
        self.assertEqual(False, self.rbs.Reject(self.rbs.data, []))

    def testReject_Incomplete(self):
        self.assertEqual(False, self.rbs.Reject(self.rbs.data, [0]))

    def testAccept_Missing(self):
        self.assertEqual(False, self.rbs.Accept(self.rbs.data, [0, 0]))

    def testAccept_Colission(self):
        self.assertEqual(False, self.rbs.Accept(self.rbs.data, [0, 0]))

    def testAccept_Good(self):
        self.assertEqual(True, self.rbs.Accept(self.rbs.data, [0, 2]))

    def testSolve_Small(self):
        self.rbs.RecursiveBacktrackingSearch(self.rbs.Root(self.rbs.data))
        self.assertEqual([[0, 2]], self.rbs.solutions)

    def testSolve_Bigger(self):
        data = [
                [0b10000000,
                 0b00000100,
                 0b00010000,
                ],
                [0b01000000,
                 0b00000001,
                 0b00001000,
                ],
                [0b11111100,
                 0b00111111,
                 0b01111110,
                ],
        ]
        rbs = matcher.RecursiveBacktrackingSearch(data, 8)
        rbs.RecursiveBacktrackingSearch(rbs.Root(rbs.data))
        expected = [[0, 0, 1], [0, 1, 2]]
        self.assertEqual(expected, rbs.solutions)


if __name__ == '__main__':
    unittest.main()
