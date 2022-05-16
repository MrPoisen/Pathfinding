# cython: language_level=3, , binding=True
from .ctools cimport CNode, LowComby, wrappop, wrappush, CPathError
cimport cython

cdef double wrapped_func(object func, CINode node, list arg):
    return func(node, arg)

cdef bint _default_t_func(x):
    return True

cdef bint _set_visiter(CINode curnode, CINode node, set visited):
    cdef tuple as_tuple = (curnode, node)
    if as_tuple not in visited:
        visited.add(as_tuple)
        return False
    return True

cdef bint _calc_visiter(CINode curnode, CINode node, set _):
    cdef int t
    cdef double t_cost, visit_cost
    visit_cost = node._connections.get(curnode)
    for t, t_cost in node:
        if t+1 in curnode.collector and curnode.get(t+1) == t_cost + visit_cost:
            return True
    return False

cdef collectorsize = 2

cpdef void set_collectorsize(unsigned int size):
    global collectorsize
    collector_size = size

cpdef unsigned int get_collectorsize():
    return collectorsize

cdef class Visitor:
    def __cinit__(self, bint use_memory = False):
        self.visited = set()
        self.func = _set_visiter if use_memory else _calc_visiter
    
    def __call__(self, CINode curnode, CINode node):
        return self.call(curnode, node)
    
    cpdef bint call(self, CINode curnode, CINode node):
        return self.func(curnode, node, self.visited)

cdef class Collecter:
    def __cinit__(self, unsigned int size):
        self.size = size
        self.collect = dict()
        #print("created collect", self.collect)
    
    def __len__(self):
        return len(self.collect)
    
    def __contains__(self, int other):
        return other in self.collect.keys()
    
    def __str__(self):
        return f"Collecter(size={self.size}, collect={self.collect})"
    
    def __iter__(self):
        cdef int key
        cdef double value
        for key, value in self.collect.copy().items():
            yield key, value
        
    cpdef double get(self, int t):
        return self.collect.get(t, float("inf"))
    
    cpdef void add(self, int t, double cost):
        if t in self.collect.keys() and self.collect[t]<cost:
            return
        if len(self.collect) < self.size or t in self.collect.keys():
            self.collect[t] = cost
            return

        self.collect.pop(self.highest_cost_pair()[0])
        
        self.collect[t] = cost
    
    cpdef (int, double) highest_cost_pair(self):
        from _heapq import heappop, heappush
        cdef double highest_cost, value
        cdef list matching_keys
        cdef int key
        highest_cost = max(self.collect.values())
        matching_keys = []
        for key, value in self.collect.items():
            if value == highest_cost:
                heappush(matching_keys, key)

        key = heappop(matching_keys)
        return key, self.collect.get(key)
    
    cpdef (int, double) lowest_cost_pair(self):
        from _heapq import heappop, heappush
        cdef double lowest_cost, value
        cdef list matching_keys
        cdef int key
        lowest_cost = min(self.collect.values())
        matching_keys = []
        for key, value in self.collect.items():
            if value == lowest_cost:
                heappush(matching_keys, key)

        key = heappop(matching_keys)
        return key, self.collect.get(key)
    
    cpdef double mincost(self):
        return min(self.collect.values())
    
    cpdef void clear(self):
        self.collect.clear()

cdef class CINode(CNode):
    def __cinit__(self, id, object t_func = None, connections = None, int collector_size = -1):
        super().__init__(id, connections)
        if collector_size == -1:
            collector_size = collectorsize
        self.collector = Collecter(collector_size)
        self.collector.add(-1, float("inf"))
        if t_func is None:
            t_func = _default_t_func
        self.t_func = t_func
        self.pair = (-1, -1.0)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __lt__(self, CINode other):
        return self.cost < other.cost
    
    def __le__(self, CINode other):
        return self.cost <= other.cost
    
    def __gt__(self, CINode other):
        return self.cost > other.cost

    def __ge__(self, CINode other):
        return self.probable_cost >= other.probable_cost
    
    def __eq__(self, CINode other):
        return other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        return f"CINode(id={self.id}, t={self.t}, cost={self.cost})"

    def __call__(self, int t):
        return self.call(t)

    def __iter__(self):
        #print("hi", self.collector)
        cdef int t
        cdef double cost
        for t, cost in self.collector:
            yield t, cost
    
    cpdef bint call(self, int t):
        return self.t_func(t)
    
    cpdef void connect(self, dict conn, bint reflect = False):
        """
        Args:
            conn: connections
            reflect: if the connections should also be applied to the connected CNodes
        """
        cdef double value
        cdef CINode cnode
        self._connections.update(conn)
        if reflect:
            for cnode, value in conn.items():
                cnode.connect({self: value}, False)

    cpdef CINode _copy(self, dict nodes): 
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

    cpdef double mincost(self):
        return self.collector.mincost()
    
    cpdef double get(self, int t):
        return self.collector.get(t)
    
    cpdef void add(self, int t, double cost):
        if -1 in self.collector.collect.keys():
            self.collector.clear()
        self.collector.add(t, cost)
        self.cost = self.collector.mincost()

@cython.boundscheck(False)
cpdef list iastar_bestpath(CINode startnode, CINode endnode, object func, bint first_contact = False, bint use_memory = True, list args = []):
    """
    Args:
        startnode: starting point
        endnode: ending point
        func: functions that estimates the cost needed to get to the endnode
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        use_memory: if rather memory should be used to ensure the right path then checking with for-loops
        args: arguments to pass additionaly to func
    
    Returns:
        list of nodes, creating a path
    """
    cdef CINode currentnode
    cdef CINode node
    cdef double cost, new_cost, t_cost
    cdef int t
    cdef Visitor was_visited = Visitor(use_memory)
    cdef LowComby queue = LowComby()
    cdef (int, double) highest_cost_pair
    
    # get costs
    startnode.collector.clear()
    startnode.add(0, 0)
    startnode.probable_cost = 0
    queue.append(startnode)

    while len(queue) != 0:
        currentnode = wrappop(queue)
        for node, cost in currentnode._connections.items():
            #node: INode
            highest_cost_pair = node.collector.highest_cost_pair()
            if was_visited.call(currentnode, node):
                continue
            for t, t_cost in currentnode:
                if node.call(t+1) is False:
                    continue
                new_cost = t_cost + cost
                if not (t+1 < highest_cost_pair[0] and new_cost > highest_cost_pair[1]):
                    node.add(t+1, new_cost)
                    node.probable_cost = node.cost + wrapped_func(func, node, args)
                    if node not in queue:
                        wrappush(queue, node)
        
        if endnode.cost <= currentnode.cost:
            break

        if first_contact and currentnode is endnode:
            break
    
    return construct(startnode, endnode)

@cython.boundscheck(False)
cpdef list idijkstra_bestpath(CINode startnode, CINode endnode, bint first_contact = False, bint use_memory = True):
    """
    Args:
        startnode: starting point
        endnode: ending point
        first_contact: if True, pathfinding will end as soon as the endnode has first been discoverd
        use_memory: if rather memory should be used to ensure the right path then checking with for-loops
    Returns:
        list of nodes, creating a path
    """
    
    cdef Visitor was_visited = Visitor(use_memory)
    cdef LowComby queue = LowComby()
    cdef CINode node, currentnode
    cdef double cost, t_cost
    cdef (int, double) highest_cost_pair
    cdef int t
    cdef double new_cost

    # get costs
    startnode.collector.clear()
    startnode.add(0, 0)
     
    queue.append(startnode)

    while len(queue) != 0:
        currentnode = wrappop(queue)
        
        for node, cost in currentnode._connections.items():
            highest_cost_pair = node.collector.highest_cost_pair()
            if was_visited.call(currentnode, node):
                continue
            for t, t_cost in currentnode:
                if node.call(t+1) is False:
                    continue
                new_cost = t_cost + cost
                if not (t+1 < highest_cost_pair[0] and new_cost > highest_cost_pair[1]):
                    node.add(t+1, new_cost)
                    if node not in queue:
                        wrappush(queue, node)
        
        if endnode.cost <= currentnode.cost:
            break

        if first_contact and currentnode is endnode:
            break
    
    return construct(startnode, endnode)

cdef list construct(CINode startnode, CINode endnode):
    # get path
    cdef list path = [endnode]
    cdef CINode to_check = endnode
    cdef CINode node
    endnode.pair = endnode.collector.lowest_cost_pair()
    
    while to_check is not startnode:
        for node in to_check._connections.keys():
            if to_check.pair[0]-1 in node.collector and node.get(to_check.pair[0]-1) + node._connections.get(to_check) == to_check.pair[1]:
                node.pair = (to_check.pair[0]-1, node.get(to_check.pair[0]-1))
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
