# cython: language_level=3
from .ctools cimport CNode, LowComby, wrappop, wrappush, CPathError

cdef default_t_func(x):
    return True

cdef class CINode(CNode):
    def __init__(self, id, t_func = None, connections = None):
        super().__init__(id, connections)
        self.t = -1
        #self.opencost = 
        #self.closedcost = {}
        if t_func is None:
            t_func = default_t_func
        self.t_func = t_func
        
    def __str__(self) -> str:
        return f"CINode(id={self.id}, t={self.t}, cost={self.cost})"

    def __call__(self, long long t):
        return self.t_func(t)

    cpdef CNode _copy(self, dict nodes): 
        cdef CINode self_copy = CINode(self.id, self.t_func)
        cdef dict new_connections = {}
        cdef CINode node, node_copy
        cdef double cost
        nodes[self_copy] = self_copy

        for node, cost in self._connections.items():
            if node in nodes.keys():
                node_copy = nodes.get(node)
            else:
                node_copy = node._copy(nodes)
                nodes[node_copy] = node_copy
            new_connections[node_copy] = cost
        self_copy.connect(new_connections, False)
        return self_copy

cpdef list iastar_bestpath(CINode startnode, CINode endnode, object func, bint first_contact = False, list args = []):
    """
    Args:
        startnode: starting point
        endnode: ending point
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        queue_type: type used for queueing nodes; LowComby can be faster but consumes more memory
    
    Returns:
        list of nodes, creating a path
    """
    cdef LowComby queue
    cdef CINode currentnode
    cdef CINode node
    cdef double cost, new_cost, result
    if args is None:
        args = []
        
    # get costs
    startnode.cost = 0
    startnode.t = 0
    queue = LowComby()
    queue.append(startnode)

    while len(queue) != 0:
        currentnode = wrappop(queue)
        for node, cost in currentnode._connections.items():
            if node(currentnode.t+1) is False:
                continue
            new_cost = currentnode.cost + cost
            if new_cost < node.cost:
                node.cost = new_cost
                node.t = currentnode.t + 1
                node.probable_cost = new_cost+ func(node, args)
                if node not in queue:
                    wrappush(queue, node)
        
        if endnode.cost <= currentnode.probable_cost:
            break
        if first_contact and currentnode is endnode:
            break
    
    # get path
    return construct(startnode, endnode)

cpdef list idijkstra_bestpath(CINode startnode, CINode endnode, bint first_contact = False):
    """
    Args:
        startnode: starting point
        endnode: ending point
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        queue_type: type used for queueing nodes; LowComby can be faster but consumes more memory
    
    Returns:
        list of nodes, creating a path
    """
    cdef LowComby queue
    cdef CINode currentnode
    cdef CINode node
    cdef double cost, new_cost

    # get costs
    startnode.cost = 0
    startnode.t = 0
    queue = LowComby()
    queue.append(startnode)

    while len(queue) != 0:
        currentnode = wrappop(queue)
        for node, cost in currentnode._connections.items():
            if node(currentnode.t+1) is False:
                continue
            new_cost = currentnode.cost + cost
            if new_cost < node.cost:
                node.cost = new_cost
                node.t = currentnode.t + 1
                if node not in queue:
                    wrappush(queue, node)
        
        if endnode.cost <= currentnode.cost:
            break
        if first_contact and currentnode is endnode:
            break
    
    # get path
    return construct(startnode, endnode)

cdef list construct(CINode startnode, CINode endnode):
    # get path
    cdef list path
    cdef CINode to_check
    cdef CINode cnode

    path = [endnode]
    to_check = endnode
    while to_check != startnode:
        for node in to_check._connections.keys():
            if node.cost + node._connections.get(to_check) == to_check.cost and node.t == to_check.t-1:
                path.append(node)
                to_check = node
                break
        else:
            raise CPathError("Coulnd't construct path")
        
    path.reverse()
    return path

cpdef tuple copy_graph(CINode start, CINode stop):
    """copies the Nodestructure deleting the found cost values for them"""
    cdef dict nodes = {}
    cdef CINode new_start = start._copy(nodes)
    return new_start, nodes.get(stop), nodes
