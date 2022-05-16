from typing import Callable, Dict, Hashable, List, Union
from pypathfinder.Astar import ANode
from pypathfinder.Dijkstra import get_calc_visiter, get_set_visiter, Collecter, iconstruct
from pypathfinder.utils import HighComby, LowComby, PathError, get_pop, get_push
from functools import total_ordering

@total_ordering
class INode(ANode):
    Default_Collector_Size = 2
    def __init__(self, id: Hashable, t_func: Callable = None, connections: Dict["INode", int] = None, collector_size: int = None):
        super().__init__(id, connections)
        if collector_size is None:
            collector_size = self.Default_Collector_Size
        self.collector = Collecter(collector_size)
        self.collector.add(-1, float("inf"))
        if t_func is None:
            t_func = lambda x: True
        self.t_func = t_func
        
    def __str__(self) -> str:
        return f"INode(id={self.id}, t={self.t}, cost={self.cost})"

    def __call__(self, t: int):
        return self.t_func(t)

    def _copy(self, nodes: dict) -> "INode": 
        self_copy = type(self)(self.id, self.t_func)
        nodes[self_copy] = self_copy
        new_connections = {}
        for node, cost in self._connections.items():
            if node in nodes.keys():
                node_copy = nodes.get(node)
            else:
                node_copy = node._copy(nodes)
                nodes[node_copy] = node_copy
            new_connections[node_copy] = cost
        self_copy.connect(new_connections, False)
        return self_copy
    
def bestpath(startnode: INode, endnode: INode, func: Callable, first_contact: bool = False, queue_type: Union[list, LowComby, HighComby]=list, use_memory: bool = True, args: list = None) -> List[INode]:
    """
    Args:
        startnode: starting point
        endnode: ending point
        func: estimation function
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        queue_type: type used for queueing nodes; LowComby can be faster but consumes more memory
    
    Returns:
        list of nodes, creating a path
    """
    if args is None:
        args = []

    if use_memory:
        was_visited = get_set_visiter()
    else:
        was_visited = get_calc_visiter()
    
    # get costs
    startnode.collector.clear()
    startnode.add(0, 0)
    startnode.probable_cost = 0
    queue: Union[List[INode], LowComby] = queue_type()
    queue.append(startnode)

    use_heappush = get_push(queue)
    use_heappop = get_pop(queue)

    while len(queue) != 0:
        currentnode = use_heappop(queue)
        for node, cost in currentnode._connections.items():
            #node: INode
            highest_cost_pair = node.collector.highest_cost_pair()
            if was_visited(currentnode, node):
                continue
            for t, t_cost in currentnode:
                if node(t+1) is False:
                    continue
                new_cost = t_cost + cost
                if not (t+1 < highest_cost_pair[0] and new_cost > highest_cost_pair[1]):
                    node.add(t+1, new_cost)
                    node.probable_cost = node.cost + func(node, args)
                    if node not in queue:
                        use_heappush(queue, node)
        
        if endnode.cost <= currentnode.cost:
            break

        if first_contact and currentnode is endnode:
            break
    
    return iconstruct(startnode, endnode)
