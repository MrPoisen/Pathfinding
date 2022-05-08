
from typing import Callable


def speedcheck(iterations, setup_func: Callable = None, print_: bool = False):
    from statistics import median
    from time import perf_counter
    def decorater(func):
        def wrapper(*args, **kwargs):
            times = []
            args = list(args)
            given_args = args.copy()
            given_kwargs = kwargs.copy()
            if setup_func is not None and len(args) == 0:
                args = setup_func()
            elif setup_func is not None:
                r = setup_func()
                for value in reversed(r):
                    args.insert(0, value)
                
            for _ in range(iterations):
                t1 = perf_counter()
                func(*args, **kwargs)
                t2 = perf_counter()-t1
                times.append(t2)
                args = given_args.copy()
                kwargs = given_kwargs.copy()
                if setup_func is not None and len(args) == 0:
                    args = setup_func()
                elif setup_func is not None:
                    r = setup_func()
                    for value in reversed(r):
                        args.insert(0, value)
                
            
            maxtime = max(times)
            mintime = min(times)
            average = sum(times)/len(times)
            median_ = median(times)
            if print_:
                print(f"iterations: {iterations}, max time: {maxtime}, min time: {mintime}, average time: {average}, median time: {median_}") 

            return  maxtime, mintime, average, median_
        return wrapper
    return decorater

def load_matrix(file, node_type):
    nodes = []
    costs = []
    
    # create nodes with id: Tuple[x, y]
    for index_y, line in enumerate(file.readlines()):
        l = []
        lcost = []
        for index_x, i in enumerate(line.strip("\n")):
            l.append(node_type((index_x, index_y)))
            lcost.append(i)
        nodes.append(l)
        costs.append(lcost)

    # get nodes connection
    len_nodes = len(nodes)
    for i, row in enumerate(nodes):
        for ii, node in enumerate(row):
            # up
            if i-1 >= 0:
                node.connect({nodes[i-1][ii]: int(costs[i-1][ii])})

            # right
            if ii+1 < len(row):
                node.connect({nodes[i][ii+1]: int(costs[i][ii+1])})

            # down
            if i+1 < len_nodes:
                node.connect({nodes[i+1][ii]: int(costs[i+1][ii])})

            # left
            if ii-1 >= 0:
                node.connect({nodes[i][ii-1]: int(costs[i][ii-1])})

    return nodes

def example1(node_type) -> tuple:
    # https://de.wikipedia.org/wiki/Dijkstra-Algorithmus#Beispiel_mit_bekanntem_Zielknoten
    frankfurt = node_type("Frankfurt")
    mannheim = node_type("Mannheim")
    kassel = node_type("Kassel")
    wuerzburg = node_type("Würzburg")
    frankfurt.connect({mannheim: 85, wuerzburg: 217, kassel: 173}, True)

    karlsruhe = node_type("Karlsruhe")
    mannheim.connect({karlsruhe:80}, True)

    erfurt = node_type("Erfurt")
    nuernberg = node_type("Nürnberg")
    wuerzburg.connect({erfurt: 186, nuernberg: 103}, True)

    stuttgart = node_type("Stuttgart")
    nuernberg.connect({stuttgart: 183}, True)

    augsburg = node_type("Augsburg")
    karlsruhe.connect({augsburg: 250}, True)

    muenchen = node_type("München")
    muenchen.connect({augsburg: 84, nuernberg: 167, kassel: 502}, True)
    return frankfurt, muenchen

def example2(node_type, file: int):
    fnames = {0: ("aocsmall.txt", 40), 1: ("aocmid.txt", 315), 2: ("aoclarge.txt", 696)}
    fname = fnames.get(file)
    with open(f"mazes/{fname[0]}") as file:
        matrix = load_matrix(file, node_type)
    return matrix[0][0], matrix[-1][-1], matrix, fname[1]

