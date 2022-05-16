# cython: language_level=3, emit_code_comments=True, embedsignature=True, binding=True
from heapq import heappop, heappush
cimport cython

cdef class CPathfinderError(Exception): pass

cdef class CDublicateError(CPathfinderError): pass

cdef class CPathError(CPathfinderError): pass

cdef double INFINITY = float("inf")

cdef double wrapped_func(object func, CNode node, list arg):
    return func(node, arg)

cdef class LowComby:
    def __init__(self):
        self.list_ = []
        self.set_ = set()
    
    def __getitem__(self, int index):
        return self.list[index]
    
    def __setitem__(self, int index, CNode obj):
        self.list_[index] = obj
        self.set_.add(obj)
    
    def __len__(self):
        return len(self.list_)
    
    def __contains__(self, CNode obj):
        return obj in self.set_
    
    cpdef LowComby copy(self):
        cdef LowComby lc
        lc = LowComby()
        lc.list_ = self.list_.copy()
        lc.set = self.set_.copy()
        return lc
    
    cpdef append(self, CNode obj):
        self.list_.append(obj)
        self.set_.add(obj)
    
    cpdef insert(self, int index, CNode obj):
        self.list_.insert(index, obj)
        self.set_.add(obj)
    
    cpdef pop(self, int index):
        r = self.list_.pop(index)
        self.set_.remove(r)
        return r

class HighComby(LowComby):
    def __getitem__(self, index):
        if index < 0 or index >= len(self.list):
            raise ValueError("index out of bounds")
        return super().__getitem__(index)
    
    def __setitem__(self, index: int, obj):
        if obj in self.set and self.list[index] != obj:
            raise CDublicateError("object already exists")
        if index < 0 or index >= len(self.list):
            raise IndexError("index out of bounds")
        if not hasattr(obj, "__hash__"):
            raise TypeError("object can't be hashed")
        super().__setitem__(index, obj)
    
    def append(self, obj):
        if obj in self.set:
            raise CDublicateError("object already exists")
        if not hasattr(obj, "__hash__"):
            raise TypeError("object can't be hashed")
        super().append(obj)
    
    def insert(self, int index, obj):
        if obj in self.set and self.list[index] != obj:
            raise CDublicateError("object already exists")
        if index < 0 or index >= len(self.list):
            raise IndexError("index out of bounds")
        if not hasattr(obj, "__hash__"):
            raise TypeError("object can't be hashed")
        
        super().insert(index, obj)
    
    def pop(self, int index):
        try:
            r = self.list.pop(index)
            self.set.pop(r)
            return r
        except IndexError as e:
            raise IndexError("out of bounds") from e
        except KeyError as e:
            raise CPathfinderError("set didn't contain item") from e

cdef wrappop(LowComby x):
    return heappop(x.list_)

cdef wrappush(LowComby x, CNode n):
    return heappush(x.list_, n)

cdef class CNode:
    def __cinit__(self, id_, connections = None):
        self._connections = {} if connections is None else connections
        self.id = id_
        self.cost = INFINITY
        self.probable_cost = INFINITY
    
    def __str__(self) -> str:
        return f"CNode(id={self.id}, cost={self.cost})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __lt__(self, CNode other):
        return self.cost < other.cost
    
    def __le__(self, CNode other):
        return self.cost <= other.cost
    
    def __gt__(self, CNode other):
        return self.cost > other.cost

    def __ge__(self, CNode other):
        return self.probable_cost >= other.probable_cost
    
    def __eq__(self, CNode other):
        return other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
    
    cpdef void connect(self, dict conn, bint reflect = False):
        """
        Args:
            conn: connections
            reflect: if the connections should also be applied to the connected CNodes
        """
        cdef double value
        cdef CNode cnode
        self._connections.update(conn)
        if reflect:
            for cnode, value in conn.items():
                cnode.connect({self: value}, False)
    
    cpdef CNode _copy(self, dict nodes): 
        cdef CNode self_copy = CNode(self.id)
        cdef dict new_connections = {}
        cdef CNode node, node_copy
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

cdef list construct(CNode startCNode, CNode endCNode):
    # get path
    cdef list path
    cdef CNode to_check
    cdef CNode cnode

    path = [endCNode]
    to_check = endCNode
    while to_check != startCNode:
        for cnode in to_check._connections.keys():
            if cnode.cost + cnode._connections.get(to_check) == to_check.cost:
                path.append(cnode)
                to_check = cnode
                break
        else:
            raise CPathError("Coulnd't construct path")
        
    path.reverse()
    return path

# DIJKSTRA
@cython.boundscheck(False)
cpdef list dijkstra_bestpath(CNode startCNode, CNode endCNode, bint first_contact = False):
    """
    Args:
        startCNode: starting point
        endCNode: ending point
        first_contact: if True, pathfinding will end as soon as the endCNode has first been discoverd
    
    Returns:
        list of CNodes, creating a path
    """
    cdef LowComby queue
    cdef CNode currentCNode
    cdef CNode cnode
    cdef double cost, new_cost
 
    # get costs
    startCNode.cost = 0
    queue = LowComby()
    queue.append(startCNode)
    
    while len(queue) != 0:
        currentCNode = wrappop(queue)
        for cnode, cost in currentCNode._connections.items():
            new_cost = currentCNode.cost + cost
            if new_cost < cnode.cost:
                cnode.cost = new_cost
                if cnode not in queue:
                    wrappush(queue, cnode)
        
        if endCNode.cost <= currentCNode.cost:
            break
        if first_contact and currentCNode is endCNode:
            break
    
    # get path
    return construct(startCNode, endCNode)
    
@cython.boundscheck(False)
cpdef list astar_bestpath(CNode startCNode, CNode endCNode, object func, bint first_contact = False, list args = []):
    """
    Args:
        startCNode: starting point
        endCNode: ending point
        first_contact: if True, pathfinding will end as soon as the endCNode has first been discoverd
    
    Returns:
        list of CNodes, creating a path
    """
    if len(args) == 0:
        args = []
    cdef LowComby queue
    cdef CNode currentCNode
    cdef CNode cnode
    cdef double cost, new_cost, result
 
    # get costs
    startCNode.cost = 0
    queue = LowComby()
    queue.append(startCNode)
    
    while len(queue) != 0:
        currentCNode = wrappop(queue)
        for cnode, cost in currentCNode._connections.items():
                
            new_cost = currentCNode.cost + cost
            if new_cost < cnode.cost:
                cnode.cost = new_cost
                result = wrapped_func(func, cnode, args)
                cnode.probable_cost = new_cost + result
                if cnode not in queue:
                    wrappush(queue, cnode)
        
        if endCNode.cost <= currentCNode.cost:
            break
        if first_contact and currentCNode is endCNode:
            break
    
    # get path
    return construct(startCNode, endCNode)

cpdef tuple copy_graph(CNode start, CNode stop):
    """copies the Nodestructure deleting the found cost values for them"""
    cdef dict nodes = {}
    cdef CNode new_start = start._copy(nodes)
    return new_start, nodes.get(stop), nodes