from ex import example2, speedcheck
from pypathfinder.Astar import ANode, bestpath as a_bestpath
from pypathfinder.Dijkstra import Node, bestpath as d_bestpath
from pypathfinder.fast import CNode, astar_bestpath, djikstra_bestpath
#from Pathfinder.fast.ctools import CNode, astar_bestpath, djikstra_bestpath
from pypathfinder.utils import LowComby

def setup_astar():
    return example2(ANode, 2)

def setup_dijkstra():
    return example2(Node, 2)

def setup_fast():
    return example2(CNode, 2)

@speedcheck(50, setup_fast, print_=True)
def fast_djikstra(start, stop, matrix, solution):
    djikstra_bestpath(start, stop)

@speedcheck(50, setup_fast, print_=True)
def fast_astar(start, stop, matrix, solution):       
    x_len = len(matrix[0])
    y_len = len(matrix)
    func = lambda node, args: (args[0] - node.id[0]) + (args[1] - node.id[1])
    astar_bestpath(start, stop, func, args=[x_len, y_len])

@speedcheck(50, setup_astar, print_=True)
def astar_list(start, stop, matrix, solution):
    x_len = len(matrix[0])
    y_len = len(matrix)
    func = lambda node, args: (args[0] -node.id[0]) + (args[1] -node.id[1])
    a_bestpath(start, stop, func, args=(x_len, y_len))

@speedcheck(50, setup_astar, print_=True)
def astar_lowcomby(start, stop, matrix, solution):
    x_len = len(matrix[0])
    y_len = len(matrix)
    func = lambda node, args: (args[0] - node.id[0]) + (args[1] - node.id[1])

    a_bestpath(start, stop, func, queue_type=LowComby, args=(x_len, y_len))

@speedcheck(50, setup_dijkstra, print_=True)
def dijkstra_list(start, stop, matrix, solution):
    d_bestpath(start, stop)

@speedcheck(50, setup_dijkstra, print_=True)
def dijkstra_lowcomby(start, stop, matrix, solution):
    d_bestpath(start, stop, queue_type=LowComby)


if __name__ == "__main__":
    print("-"*40)
    astar_lowcomby()
    print("-"*40)
    dijkstra_lowcomby()
    print("-"*40)
    fast_djikstra()
    print("-"*40)
    fast_astar()

