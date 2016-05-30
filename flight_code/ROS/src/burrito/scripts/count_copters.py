#!/usr/bin/env python
import rosnode

def count_copters():
    limit = 0
    
    nods = rosnode.get_node_names()
    for n in nods:
        if '/copter' in n and '/mavros' in n:
            limit = limit + 1

    print limit, "COPTERS ACTIVE"

    return limit
