# PolyCollider
A short demo of the GJK, EPA and Sutherland-Hodge algorithms, useful for testing arbitrary convex polygon collisions and getting contact points in a physics engine, written in Python.

## Motivation

I wrote these 3 scripts to help me understand these algorithms better during an attempt to implement a 2d physics engine in C++. Each of these algorithms has a different utility in the collision detection phase of a physics engine.

GJK (Gilbert-Johnson-Keerthi algorithm) - This is used during narrow phase collision detection to determine if two arbitrary polygons are actually colliding. You probably shouldn't use this for simple boxes and circles because there are faster tests for those, such as the separating axis test (SAT).

EPA (Expanding Polytope Algorithm) - This expands on the GJK algorithm to generate a collision normal and penetration depth, useful for linear collision response.

Sutherland-Hodgeman Polygon Clipping Algorithm - This uses the normal and penetration depth obtained from the EPA to determine collision points between two polygons, useful for rotational collision response.

## References

https://cs.brown.edu/courses/csci1950-u/lectures/04_advancedCollisionsAndPhysics.pdf

https://fjinn.github.io/Experiences/Programming/Math/GJKAlgorithm_README.html

https://github.com/kroitor/gjk.c

https://www.youtube.com/watch?v=Qupqu1xe7Io