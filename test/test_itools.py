from unittest import TestCase, main

from ex import from_file
from pypathfinder.Dijkstra import INode, ibestpath
from pypathfinder.fast import CINode, idijkstra_bestpath


class TestDijkstra(TestCase):
    def test_bestpath1(self):
        with open("mazes/fivefive.txt") as file:
            start, stop, matrix = from_file(INode, file)
        
        matrix[0][2].t_func = lambda x: x%6 != 2 # top
        matrix[4][2].t_func = lambda x: x%6 != 5 # bottom
        matrix[2][2].t_func = lambda x: x%6 not in {0, 1, 3, 4} # middle
        
        matrix[1][2].t_func = lambda x: x%6 not in {1, 2, 3} # higher then middle
        matrix[3][2].t_func = lambda x: x%6 not in {0, 4, 5} # lower then middle
        # t_func simulates a wall of height 2 moving up (and down and up ...), upperblock starts at matrix[2][2]

        path = ibestpath(start, stop)
        self.assertEqual(path, [INode((0, 0)), INode((0, 1)), INode((0, 2)), INode((1, 2)), 
            INode((1, 3)), INode((1, 4)), INode((2, 4)), INode((3, 4)), INode((4, 4))])
        self.assertEqual(stop.mincost(), 27)
        self.assertEqual(True, True)

    def test_bestpath2(self):
        with open("mazes/sevenfivespecial.txt") as file:
            start, stop, matrix = from_file(INode, file)
        
        matrix[0][4].t_func = lambda x: x%6 != 4 # top
        matrix[4][4].t_func = lambda x: x%6 != 1 # bottom
        matrix[2][4].t_func = lambda x: x%6 not in {0, 2, 3, 5} # middle
        
        matrix[1][4].t_func = lambda x: x%6 not in {3, 4, 5} # higher then middle
        matrix[3][4].t_func = lambda x: x%6 not in {0, 1, 2} # lower then middle
        # t_func simulates a wall of height 2 moving down (and up and down ...), upperblock starts at matrix[2][4]

        path = ibestpath(start, stop)
        self.assertEqual(path[-1].mincost(), 26)
    
    def test_cythonbestpath1(self):
        with open("mazes/fivefive.txt") as file:
            start, stop, matrix = from_file(CINode, file)
        
        matrix[0][2].t_func = lambda x: x%6 != 2 # top
        matrix[4][2].t_func = lambda x: x%6 != 5 # bottom
        matrix[2][2].t_func = lambda x: x%6 not in {0, 1, 3, 4} # middle
        
        matrix[1][2].t_func = lambda x: x%6 not in {1, 2, 3} # higher then middle
        matrix[3][2].t_func = lambda x: x%6 not in {0, 4, 5} # lower then middle
        # t_func simulates a wall of height 2 moving up (and down and up ...), upperblock starts at matrix[2][2]

        path = idijkstra_bestpath(start, stop)
        self.assertEqual(path, [CINode((0, 0)), CINode((0, 1)), CINode((0, 2)), CINode((1, 2)), 
            CINode((1, 3)), CINode((1, 4)), CINode((2, 4)), CINode((3, 4)), CINode((4, 4))])
        self.assertEqual(stop.mincost(), 27)
        self.assertEqual(True, True)

    def test_cythonbestpath2(self):
        with open("mazes/sevenfivespecial.txt") as file:
            start, stop, matrix = from_file(CINode, file)
        
        matrix[0][4].t_func = lambda x: x%6 != 4 # top
        matrix[4][4].t_func = lambda x: x%6 != 1 # bottom
        matrix[2][4].t_func = lambda x: x%6 not in {0, 2, 3, 5} # middle
        
        matrix[1][4].t_func = lambda x: x%6 not in {3, 4, 5} # higher then middle
        matrix[3][4].t_func = lambda x: x%6 not in {0, 1, 2} # lower then middle
        # t_func simulates a wall of height 2 moving down (and up and down ...), upperblock starts at matrix[2][4]

        path = idijkstra_bestpath(start, stop)
        self.assertEqual(path[-1].mincost(), 26)
    
if __name__ == "__main__":
    main()