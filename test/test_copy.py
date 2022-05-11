from unittest import TestCase, main

from pypathfinder.Dijkstra import copy_graph, Node, bestpath
from ex import example1

class TestDijkstra(TestCase):
    
    def test_copy1(self):
        point1 = Node(1)
        point2 = Node(2)
        point3 = Node(3)
        point4 = Node(4)

        point1.connect({point2: 10, point3: 5}, True)
        point4.connect({point2: 5, point3: 15}, True)

        path = bestpath(point1, point4) # Nodes will get a cost
        new_start, new_stop, all_nodes = copy_graph(point1, point4)
        self.assertEqual(point4.cost, 15)
        self.assertEqual(new_stop.cost, float("inf"))
        self.assertEqual(all_nodes.get(new_stop).cost, float("inf"))
        bestpath(new_start, new_stop)
        self.assertEqual(new_stop.cost, 15)


    def test_copy2(self):
        start, end = example1(Node)
        path = bestpath(start, end) # Nodes will get a cost
        new_start, new_end, all_nodes = copy_graph(start, end)
        self.assertEqual(end.cost, 487)
        self.assertEqual(new_end.cost, float("inf"))


if __name__ == "__main__":
    main()