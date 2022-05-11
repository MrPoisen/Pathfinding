
from typing import Dict, Hashable, List, Tuple, Union
from pypathfinder.utils import HighComby, LowComby, PathError, PathfinderError, get_pop, get_push
from heapq import heappop, heappush
from functools import total_ordering

@total_ordering
class Node:
    __slots__ = ("_connections", "id", "cost")
    def __init__(self, id: Hashable, connections: Dict["Node", int] = None):
        self._connections: Dict[Node, int] = {} if connections is None else connections
        self.id = id
        self.cost = float("inf")
    
    def __str__(self) -> str:
        return f"Node(id={self.id}, cost={self.cost})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.cost < other.cost
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False
        return __o.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
    
    def connect(self, conn: Dict["Node", int], reflect: bool = False):
        """
        Args:
            conn: connections
            reflect: if the connections should also be applied to the connected Nodes
        """
        self._connections.update(conn)
        if reflect:
            for node, value in conn.items():
                node.connect({self: value}, False)

    def _copy(self, nodes: dict) -> "Node": 
        self_copy = type(self)(self.id)
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
        #return self_copy

def construct(startnode, endnode) -> list:
    # get path
    path = [endnode]
    to_check = endnode
    while to_check != startnode:
        for node in to_check._connections.keys():
            if node.cost + node._connections.get(to_check) == to_check.cost:
                path.append(node)
                to_check = node
                break
        else:
            raise PathError("Coulnd't construct path")
        
    path.reverse()
    return path

def bestpath(startnode: Node, endnode: Node, first_contact: bool = False, queue_type: Union[list, LowComby, HighComby]=list) -> List[Node]:
    """
    Args:
        startnode: starting point
        endnode: ending point
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        queue_type: type used for queueing nodes; LowComby can be faster but consumes more memory
    
    Returns:
        list of nodes, creating a path
    """
    # get costs
    startnode.cost = 0
    queue: Union[List[Node], LowComby] = queue_type()
    queue.append(startnode)
    use_heappop = get_pop(queue)
    use_heappush = get_push(queue)
    
    while len(queue) != 0:
        currentnode = use_heappop(queue)
        for node, cost in currentnode._connections.items():
                
            new_cost = currentnode.cost + cost
            if new_cost < node.cost:
                node.cost = new_cost
                if node not in queue:
                    use_heappush(queue, node)
        
        if endnode.cost <= currentnode.cost:
            break
        if first_contact and currentnode is endnode:
            break
    
    # get path
    return construct(startnode, endnode)

def copy_graph(start: Node, stop: Node) -> Tuple[Node, Node, Dict[str, Node]]:
    """copies the Nodestructure deleting the found cost values for them"""
    nodes = {}
    new_start = start._copy(nodes)
    return new_start, nodes.get(stop), nodes

