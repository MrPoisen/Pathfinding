from unittest import TestCase, main

from ex import from_file
from pypathfinder.Dijkstra import INode, ibestpath


class TestDijkstra(TestCase):
    def test_bestpath1(self):
        with open("mazes/fivefive.txt") as file:
            start, stop, matrix = from_file(INode, file)
        
        matrix[0][2].t_func = lambda x: x%6 != 2 # top
        matrix[4][2].t_func = lambda x: x%6 != 5 # bottom
        matrix[2][2].t_func = lambda x: x%6 not in {0, 1, 3, 4} # middle
        
        matrix[1][2].t_func = lambda x: x%6 not in {1, 2, 3} # higher then middle
        matrix[1][2].t_func = lambda x: x%6 not in {0, 4, 5} # lower then middle
        # t_func simulates a wall of heigt 2 moving up (and down and up ...), upperblock starts at matrix[2][2]

        path = ibestpath(start, stop)
        self.assertEqual(path, [INode((0, 0)), INode((0, 1)), INode((0, 2)), INode((1, 2)), 
        INode((1, 3)), INode((1, 4)), INode((2, 4)), INode((3, 4)), INode((4, 4))])
        self.assertEqual(stop.cost, 27)

if __name__ == "__main__":
    #print(RAW_TEST_1)
    main()