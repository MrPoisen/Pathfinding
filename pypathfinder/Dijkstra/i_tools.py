from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, Dict, Hashable, List, Union
from pypathfinder.Dijkstra import Node
from pypathfinder.utils import HighComby, LowComby, PathError, get_pop, get_push
from functools import total_ordering

def get_set_visiter():
    visited = set()
    def was_visited(curnode, node):
        if (curnode, node) not in visited:
            visited.add((curnode, node))
            return False
        return True
    return was_visited

def get_calc_visiter():
    def was_visited(curnode, node):
        visit_cost = node._connections.get(curnode)
        for t, t_cost in node:
            if t+1 in curnode.collector and curnode.get(t+1) == t_cost + visit_cost:
                return True
        return False
    return was_visited

@dataclass
class Collecter:
    size: int
    collect: dict = field(default_factory=dict, init=False)

    def __len__(self):
        return len(self.collect)
    
    def __contains__(self, other):
        return other in self.collect.keys()
    
    def get(self, t: int):
        return self.collect.get(t, float("inf"))
    
    def add(self, t: int, cost: int):
        if t in self.collect.keys() and self.collect[t]<cost:
            return
        if len(self.collect) < self.size or t in self.collect.keys():
            self.collect[t] = cost
            return

        self.collect.pop(self.highest_cost_pair()[0])
        
        self.collect[t] = cost
    
    def highest_cost_pair(self):
        from heapq import heappop, heappush
        highest_cost = max(self.collect.values())
        matching_keys = []
        for key, value in self.collect.items():
            if value == highest_cost:
                heappush(matching_keys, key)
        del highest_cost, key, value
        key = heappop(matching_keys)
        return key, self.collect.get(key)
    
    def lowest_cost_pair(self):
        from heapq import heappop, heappush
        highest_cost = min(self.collect.values())
        matching_keys = []
        for key, value in self.collect.items():
            if value == highest_cost:
                heappush(matching_keys, key)
        del highest_cost, key, value
        key = heappop(matching_keys)
        return key, self.collect.get(key)
    
    def mincost(self):
        return min(self.collect.values())
    
    def clear(self):
        self.collect.clear()

@total_ordering
class INode(Node):
    Default_Collector_Size = 2
    def __init__(self, id: Hashable, t_func: Callable = None, collector_size: int = None, connections: Dict["INode", int] = None):
        super().__init__(id, connections)
        if collector_size is None:
            collector_size = self.Default_Collector_Size
        self.collector = Collecter(collector_size)
        self.collector.add(-1, float("inf"))
        if t_func is None:
            t_func = lambda x: True
        self.t_func = t_func
        
    def __str__(self) -> str:
        return f"Node(id={self.id}, collector={self.collector})"

    def __call__(self, t: int):
        return self.t_func(t)
    
    def __iter__(self):
        for t, cost in self.collector.collect.copy().items():
            yield t, cost
        
    def _copy(self, nodes: dict) -> "Node": 
        self_copy = type(self)(self.id, self.t_func, self.collector.size)
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
    
    def mincost(self):
        return self.collector.mincost()
    
    def get(self, t):
        return self.collector.get(t)
    
    def add(self, t: int, cost: int):
        if -1 in self.collector.collect.keys():
            self.collector.clear()
        self.collector.add(t, cost)
        self.cost = self.collector.mincost()
    
def bestpath(startnode: INode, endnode: INode, first_contact: bool = False, queue_type: Union[list, LowComby, HighComby]=list, use_memory: bool = True) -> List[INode]:
    """
    Args:
        startnode: starting point
        endnode: ending point
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        queue_type: type used for queueing nodes; LowComby can be faster but consumes more memory
    
    Returns:
        list of nodes, creating a path
    """
    
    if use_memory:
        was_visited = get_set_visiter()
    else:
        was_visited = get_calc_visiter()
    
    # get costs
    startnode.collector.clear()
    startnode.add(0, 0)
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
                    if node not in queue:
                        use_heappush(queue, node)
        
        if endnode.cost <= currentnode.cost:
            break

        if first_contact and currentnode is endnode:
            break
    
    return construct(startnode, endnode)

def construct(startnode: INode, endnode: INode) -> list:
    # get path
    path = [endnode]
    endnode.pair = endnode.collector.lowest_cost_pair()
    to_check = endnode
    while to_check is not startnode:
        for node in to_check._connections.keys():
            if to_check.pair[0]-1 in node.collector and node.get(to_check.pair[0]-1) + node._connections.get(to_check) == to_check.pair[1]:
                node.pair = (to_check.pair[0]-1, node.get(to_check.pair[0]-1))
                path.append(node)
                to_check = node
                break
        else:
            raise PathError("Coulnd't construct path")
        
    path.reverse()
    return path

if __name__ == "__main__":
    from pypathfinder.Dijkstra import copy_graph
    point1 = INode(1)
    point2 = INode(2, lambda x: x % 2 == 1)
    point3 = INode(3, lambda x: x % 2 == 0)
    point4 = INode(4)

    point1.connect({point2: 15, point3: 5}, True)
    point4.connect({point2: 15, point3: 10}, True)
    try:
        path = bestpath(point1, point4)
    except PathError:
        print("Error, no path")
    else:
        print(path)
    
    point1, point4, graph = copy_graph(point1, point4)
    graph.get(point2).connect({graph.get(point3): 2}, True)
    try:
        path = bestpath(point1, point4)
    except PathError:
        print("Error, no path")
    else:
        print(path)

