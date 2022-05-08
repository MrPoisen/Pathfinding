# cython: language_level=3,emit_code_comments=True, embedsignature=True
from typing import Dict, Hashable
from heapq import heappop, heappush
cimport cython

class PathfinderError(Exception): pass

class DublicateError(PathfinderError): pass

class PathError(PathfinderError): pass
   
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
            raise DublicateError("object already exists")
        if index < 0 or index >= len(self.list):
            raise IndexError("index out of bounds")
        if not hasattr(obj, "__hash__"):
            raise TypeError("object can't be hashed")
        super().__setitem__(index, obj)
    
    def append(self, obj):
        if obj in self.set:
            raise DublicateError("object already exists")
        if not hasattr(obj, "__hash__"):
            raise TypeError("object can't be hashed")
        super().append(obj)
    
    def insert(self, int index, obj):
        if obj in self.set and self.list[index] != obj:
            raise DublicateError("object already exists")
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
            raise PathfinderError("set didn't contain item") from e

cdef wrappop(LowComby x):
    return heappop(x.list_)

cdef wrappush(LowComby x,CNode n):
    return heappush(x.list_, n)

cdef class CNode:
    def __init__(self, id: Hashable, connections: Dict["CNode", int] = None):
        self._connections: Dict[CNode, int] = {} if connections is None else connections
        self.id = id
        self.cost = float("inf")
        self.probable_cost = float("inf")
    
    def __str__(self) -> str:
        return f"CNode(id={self.id}, cost={self.cost})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.cost < other.cost
    
    def __le__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.cost <= other.cost
    
    def __gt__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.cost > other.cost

    def __ge__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.probable_cost >= other.probable_cost
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False
        return __o.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
    
    cpdef void connect(self, dict conn, bint reflect = False):
        """
        Args:
            conn: connections
            reflect: if the connections should also be applied to the connected CNodes
        """
        cdef double value
        cdef CNode CNode
        self._connections.update(conn)
        if reflect:
            for CNode, value in conn.items():
                CNode.connect({self: value}, False)

cdef list construct(CNode startCNode, CNode endCNode):
    # get path
    cdef list path
    cdef CNode to_check
    cdef CNode CNode

    path = [endCNode]
    to_check = endCNode
    while to_check != startCNode:
        for CNode in to_check._connections.keys():
            if CNode.cost + CNode._connections.get(to_check) == to_check.cost:
                path.append(CNode)
                to_check = CNode
                break
        else:
            raise PathError("Coulnd't construct path")
        
    path.reverse()
    return path

# DJIKSTRA
@cython.boundscheck(False)
cpdef list djikstra_bestpath(CNode startCNode, CNode endCNode, bint first_contact = False):
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
    cdef CNode Cnode
    cdef double cost, new_cost
 
    # get costs
    startCNode.cost = 0
    queue = LowComby()
    queue.append(startCNode)
    
    while len(queue) != 0:
        currentCNode = wrappop(queue)
        for Cnode, cost in currentCNode._connections.items():
            new_cost = currentCNode.cost + cost
            if new_cost < Cnode.cost:
                Cnode.cost = new_cost
                if Cnode not in queue:
                    wrappush(queue, Cnode)
        
        if endCNode.cost <= currentCNode.cost:
            break
        if first_contact and currentCNode is endCNode:
            break
    
    # get path
    return construct(startCNode, endCNode)
    
@cython.boundscheck(False)
cpdef list astar_bestpath(CNode startCNode, CNode endCNode, object func,  bint first_contact = False, list args = []):
    """
    Args:
        startCNode: starting point
        endCNode: ending point
        first_contact: if True, pathfinding will end as soon as the endCNode has first been discoverd
    
    Returns:
        list of CNodes, creating a path
    """
    if args == []:
        args = []
    cdef LowComby queue
    cdef CNode currentCNode
    cdef CNode CNode
    cdef double cost, new_cost, result
 
    # get costs
    startCNode.cost = 0
    queue = LowComby()
    queue.append(startCNode)
    
    while len(queue) != 0:
        currentCNode = wrappop(queue)
        for CNode, cost in currentCNode._connections.items():
                
            new_cost = currentCNode.cost + cost
            if new_cost < CNode.cost:
                CNode.cost = new_cost
                result = func(CNode, args)
                CNode.probable_cost = new_cost + result
                if CNode not in queue:
                    wrappush(queue, CNode)
        
        if endCNode.cost <= currentCNode.cost:
            break
        if first_contact and currentCNode is endCNode:
            break
    
    # get path
    return construct(startCNode, endCNode)