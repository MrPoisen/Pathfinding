import imp
from ex import example2
from Pathfinder.Astar import ANode, bestpath
from Pathfinder.utils import LowComby
import cProfile
def run():
    start, stop, matrix, solution = example2(ANode, 2)
    func = lambda id_, args: (args[0]-id_[0]) + (args[1]-id_[1])
    
    path = bestpath(start, stop, func, queue_type=LowComby, args=(len(matrix[0]), len(matrix)))
    print(f"cost: {path[-1].cost}, solution: {solution}")

cProfile.run("run()")