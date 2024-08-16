# TODOs

1. Need to detect if a given method depends on any non-recalculating methods of the class; what to do then?
   1. always recalculate? would only be relevant if client explicitly calls the method, since otherwise the dependent methods would never invoke it.
   2. Another choice is to ignore the decorator, and make all methods/properties part of the calc graph
