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

## Prerequisites

There are a few vector math tricks used here. If you don't know about many of them, you'll be lost, so I decided to list them here:

### The Dot Product

The dot product of two vectors A and B, is defined as:
$$\dot{AB} = A_{x} \cdot B_{x} + A_{y} \cdot B_{y}$$

The significance of the dot product is that it gives a measure of the sameness of two vectors. 

If the two vectors are unit vectors, the dot product gives the cosine of the angle between them. If they are not unit vectors, the dot product gives the relative length of one vector along the other.

The relative length of one vector along the other is known as its *projection*. The projection of a vector A along a vector B is given by the following formula:
$$proj_{AB} = \frac{(A \cdot B)}{A^2} \cdot A $$

TODO: INSERT DIAGRAM HERE

### Vector Cross Product

We're working in 2D here, so we don't dwell too much on the cross product, but it comes in handy in the derivation of the triple product, which we use in the GJK algorithm.

The *cross product* of two vectors results in a third vector, the direction of which is in a plane perpendicular to the other two vectors. The cross product is not defined for 2D vectors, but we can still utilize it by pretending all our vectors have a Z coordinate of 0.

The formula for the cross product of two vectors A and B is 
$$ \vec{A}\times\vec{B} = (A_y * B_z - A_z * B_y, - (A_x * B_z - A_z * B_x), A_x * B_y - A_y * B_x) $$

The Z term (which we've set to be 0 since we're working in 2D) shows up in both the X and Y components, but not the Z component, meaning the cross product of two 2D vectors will produce a 3D vector that points out of (or, depending on the handedness of your coordinate system, into) the page.

While the Z coordinate isn't displayed in an application using 2D graphics, it is important behind the scenes in the physics engine, especially for handling torques.

It is important to note that the cross product is anti-commutative. This means that:
$$ \vec{A}\times\vec{B} = - (\vec{B}\times\vec{A}) $$

In other words, the cross product of A and B is NOT the same as the cross product of B and A. This can be a source of confusion, so you need to watch it carefully.

TODO: Insert diagram here

### Vector Triple Product

The vector triple product requires 3 vectors, $\vec{A}, \vec{B}, \vec{C}$.
 It is given by:
 $$\vec{A}\times(\vec{B}\times\vec{C})$$

 It produces a vector that is coplanar with $\vec{B}$ and $\vec{C}$ and perpendicular to $\vec{A}$. Coplanar means that the vectors lie on the same plane.

 The triple product is a complicated topic, but we are going to specifically use it here to get a vector perpendicular to another vector, pointing towards a specific point. We do this by finding the cross product of the vector of the line segment with a vector from the target point to the start of the line segment, and then we find the cross product of that result with the vector of the line segment again.

 If we have a line segment $\vec{AB}$, and we want to get a perpendicular vector from that line segment in the direction of another point $\vec{C}$, we calculate the resultant vector D as:
 $$\vec{D} = \vec{AB}\times\vec{AC}\times\vec{AB}$$

 $\vec{D}$ is a vector perpendicular to AB in the direction of $\vec{C}$.

 TODO: Insert diagram here so its less confusing

 There is a simplified formula that can be used for the vector triple product:

 $$\vec{A}\times\vec{B}\times\vec{C} = \vec{B}(\vec{A}\cdot\vec{C}) - \vec{C}(\vec{A}\cdot\vec{B})$$

 It is informally known as the BAC-CAB rule, as an aid to memory. The derivation is somewhat complex, so you'll have to take my word for it, or at least look it up. 