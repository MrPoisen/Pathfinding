# cython: language_level=3
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

cdef list construct(CNode startCNode, CNode endCNode)
cdef wrappop(LowComby x)
cdef wrappush(LowComby x,CNode n)
cpdef list djikstra_bestpath(CNode startCNode, CNode endCNode, bint first_contact = *)
cpdef list astar_bestpath(CNode startCNode, CNode endCNode, object func,  bint first_contact = *, list args = *)