from typing import Callable, Dict, Hashable, List, Union
from pypathfinder.Astar import ANode
from pypathfinder.utils import HighComby, LowComby, PathError, get_pop, get_push
from functools import total_ordering

@total_ordering
class INode(ANode):
    def __init__(self, id: Hashable, t_func: Callable = None, connections: Dict["INode", int] = None):
        super().__init__(id, connections)
        self.t = -1
        #self.opencost = 
        #self.closedcost = {}
        if t_func is None:
            t_func = lambda x: True
        self.t_func = t_func
        
    def __str__(self) -> str:
        return f"INode(id={self.id}, t={self.t}, cost={self.cost})"

    def __call__(self, t: int):
        return self.t_func(t)

    def _copy(self, nodes: dict) -> "Node": 
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
    
def bestpath(startnode: INode, endnode: INode, func: Callable, first_contact: bool = False, queue_type: Union[list, LowComby, HighComby]=list, args: list = None) -> List[INode]:
    """
    Args:
        startnode: starting point
        endnode: ending point
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        queue_type: type used for queueing nodes; LowComby can be faster but consumes more memory
    
    Returns:
        list of nodes, creating a path
    """
    if args is None:
        args = []
        
    # get costs
    startnode.cost = 0
    startnode.t = 0
    queue: Union[List[INode], LowComby] = queue_type()
    queue.append(startnode)

    use_heappush = get_push(queue)
    use_heappop = get_pop(queue)

    while len(queue) != 0:
        currentnode = use_heappop(queue)
        for node, cost in currentnode._connections.items():
            if node(currentnode.t+1) is False:
                continue
            new_cost = currentnode.cost + cost
            if new_cost < node.cost:
                node.cost = new_cost
                node.t = currentnode.t + 1
                node.probable_cost = new_cost+ func(node, args)
                if node not in queue:
                    use_heappush(queue, node)
        
        if endnode.cost <= currentnode.probable_cost:
            break
        if first_contact and currentnode is endnode:
            break
    
    # get path
    return construct(startnode, endnode) # TODO: Maybe need time?

def construct(startnode, endnode) -> list:
    # get path
    path = [endnode]
    to_check = endnode
    while to_check != startnode:
        for node in to_check._connections.keys():
            if node.cost + node._connections.get(to_check) == to_check.cost and node.t == to_check.t-1:
                path.append(node)
                to_check = node
                break
        else:
            raise PathError("Coulnd't construct path")
        
    path.reverse()
    return path
