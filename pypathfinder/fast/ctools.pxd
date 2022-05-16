# cython: language_level=3, , binding=True

cdef class CPathfinderError(Exception):
    pass

cdef class CDublicateError(CPathfinderError):
    pass

cdef class CPathError(CPathfinderError):
    pass

cdef class LowComby:
    cdef list list_
    cdef set set_
    cpdef LowComby copy(self)    
    cpdef append(self, CNode obj)   
    cpdef insert(self, int index, CNode obj)   
    cpdef pop(self, int index)

cdef class CNode:
    cdef public double cost, probable_cost
    cdef readonly dict _connections
    cdef public object id    
    cpdef void connect(self, dict conn, bint reflect = *)
    cpdef CNode _copy(self, dict nodes)

cdef list construct(CNode startCNode, CNode endCNode)
cdef wrappop(LowComby x)
cdef wrappush(LowComby x,CNode n)
cpdef list dijkstra_bestpath(CNode startCNode, CNode endCNode, bint first_contact = *)
cpdef list astar_bestpath(CNode startCNode, CNode endCNode, object func,  bint first_contact = *, list args = *)
cpdef tuple copy_graph(CNode start, CNode stop)