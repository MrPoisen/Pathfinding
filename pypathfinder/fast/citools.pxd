# cython: language_level=3
from .ctools cimport CNode

cdef class CINode(CNode):
    cdef public object t_func
    cdef long long t
    cpdef CNode _copy(self, dict nodes)

cdef list construct(CINode startnode, CINode endnode)
cpdef list idijkstra_bestpath(CINode startnode, CINode endnode, bint first_contact = *)
cpdef list iastar_bestpath(CINode startnode, CINode endnode, object func,  bint first_contact = *, list args = *)
cpdef tuple copy_graph(CINode start, CINode stop)