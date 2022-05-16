# cython: language_level=3, binding=True
from .ctools cimport CNode

ctypedef bint (*f_type)(CINode, CINode, set)

cdef class Visitor:
    cdef set visited
    cdef f_type func
    cpdef bint call(self, CINode curnode, CINode node)

cdef class Collecter:
    cdef unsigned int size
    cdef public dict collect
    cpdef double get(self, int t)
    cpdef void add(self, int t, double cost)
    cpdef (int, double) highest_cost_pair(self)
    cpdef (int, double) lowest_cost_pair(self)
    cpdef double mincost(self)
    cpdef void clear(self)

cdef class CINode(CNode):
    cdef public object t_func
    cdef int t
    cdef collector
    cdef (int, double) pair
    cpdef CNode _copy(self, dict nodes)
    cpdef double mincost(self)
    cpdef double get(self, int t)
    cpdef void add(self, int t, double cost)
    cpdef bint call(self, int t)

cpdef void set_collectorsize(unsigned int size)
cpdef unsigned int get_collectorsize()

cdef list construct(CINode startnode, CINode endnode)
cpdef list idijkstra_bestpath(CINode startnode, CINode endnode, bint first_contact = *, bint use_memory = *)
cpdef list iastar_bestpath(CINode startnode, CINode endnode, object func,  bint first_contact = *, bint use_memory = *, list args = *)
cpdef tuple copy_graph(CINode start, CINode stop)