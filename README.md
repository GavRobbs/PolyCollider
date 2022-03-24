# PolyCollider
A short demo of the SAT, GJK, EPA and Sutherland-Hodge algorithms, useful for testing arbitrary convex polygon collisions and getting contact points in a physics engine, written in Python.

## Motivation

I wrote these 4 scripts to help me understand these algorithms better during an attempt to implement a 2d physics engine in C++. Each of these algorithms has a different utility in the collision detection phase of a physics engine.

SAT (Separating Axis Test) - Used during narrow phase collision detection to determine if two polygons are colliding. The test is derived from the Hyperplane Separation Theorem. If the polygons are colliding, the separating axis test can tell you what the axis of least overlap is, and how far along the overlap is, giving a collision normal and penetration depth.

GJK (Gilbert-Johnson-Keerthi algorithm) - This is used during narrow phase collision detection to determine if two arbitrary polygons are actually colliding. It is combined with the EPA (Expanding Polytope Algorithm) to generate a collision normal and penetration depth, useful for linear collision response.

Sutherland-Hodgeman Polygon Clipping Algorithm - This uses the normal and penetration depth obtained from the SAT or EPA to determine collision points between two polygons, useful for rotational collision response.

## References

https://cs.brown.edu/courses/csci1950-u/lectures/04_advancedCollisionsAndPhysics.pdf

https://fjinn.github.io/Experiences/Programming/Math/GJKAlgorithm_README.html

https://github.com/kroitor/gjk.c

https://www.youtube.com/watch?v=Qupqu1xe7Io

https://personal.math.vt.edu/mrlugo/sat.html

## Prerequisites

There are a few vector math tricks used here. If you don't know about many of them, you'll be lost, so I decided to list them here:

### The Dot Product

The dot product of two vectors is a measure of their sameness as a scalar value. For two vectors A and B, it is defined as:
$$\dot{AB} = A_{x} \cdot B_{x} + A_{y} \cdot B_{y}$$

If the two vectors are unit vectors, the dot product gives the cosine of the angle between them. 

If they are not unit vectors, the dot product gives the relative length of one vector along the other:
1. If two vectors have a dot product of 1, they are of the same magnitude and point in the same direction
2. If the two vectors have a dot product of -1, they are of the same magnitude and point in opposite directions
3. Two vectors with a dot product of > 0 means that both vectors point in the same direction, but the lengths are not the same - the magnitude of one of those vectors is a multiple of the magnitude of the other
4. A dot product of < 0 means the same as the previous point as it pertains to magnitude, but the two vectors point in opposite directions
5. A dot product of 0 means that the two vectors are perpendicular to each other

The relative length of one vector along the other is known as its *projection*. The projection of a vector A along a vector B is given by the following formula:
$$proj_{AB} = \frac{(\vec{A}\cdot\vec{B})}{|\vec{A}|^2} \cdot A $$

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
 $$(\vec{A}\times\vec{B})\times\vec{C}$$

It produces a vector that is coplanar with $\vec{B}$ and $\vec{C}$ and perpendicular to $\vec{A}$. Coplanar means that the vectors lie on the same plane.

The triple product is a complicated topic, but we are going to use it here for two things:
 
 1) To get the closest point on a line to an arbitrary point
 2) To get a vector perpendicular to the line, pointing towards the direction of an arbitrary point. 

We do number 1 by finding the cross product of the vector of the line segment with a vector from the start of the line segment to the target point, and then we find the cross product of that result with the vector of the line segment again.

If we have a line segment $\vec{AB}$, and we want to get the closest point on it to another point $\vec{C}$, we calculate the resultant point D as:
$$\vec{D} = \vec{AB}\times\vec{AC}\times\vec{AB}$$

$\vec{D}$ is a point on $\vec{AB}$ in the closest to $\vec{C}$. To calculate the perpendicular vector in the direction of $\vec{C}$, we simply find $\vec{DC} = C - D$

TODO: Insert diagram here so its less confusing

There is a simplified formula that can be used for the vector triple product:

$$(\vec{A}\times\vec{B})\times\vec{C} = \vec{B}(\vec{C}\cdot\vec{A}) -\vec{A}(\vec{C}\cdot\vec{B}) $$

### Edge Normals and Winding Order

The equation you may have learnt for a line in high school is:

$$y = mx + c$$

where y is the y-coordinate of the point on the line with an x-coordinate of x, m is the gradient and c is a constant (technically called the y intercept).

The gradient, m is the measure of the rise over run of the line. When you started dealing with more complex graphs that couldn't be represented with the line equation such as polynomials like $y=x^2$, you may have learnt that they don't have a constant gradient - the gradient changes at every point along the graph.

Before you learnt calculus and differentiation, a primitive method you learnt was constructing a tangent line. A tangent line is a straight line at a point that is generated as an approximation of a straight line between two very close points on the graph. The m coefficient of the tangent line represents the gradient at that point on the graph.

An interesting property of tangent lines was that all tangent lines with the same gradient are parallel to each other.

Sometimes however, it is useful to extend the concept of a tangent line. It can be helpful to find a line perpendicular to the tangent line at a point. This line perpendicular to the tangent line is known as a normal. 

The normal is used extensively in graphics and physics programming. In graphics, it can be used to calculate lighting and visibility, and in physics it can be used to calculate collision detection and response. Before exploring the normal further, I will detour into the winding order.

The winding order of a shape is the order in which the points that make it up are specified. This can be clockwise or counterclockwise. It is very important to maintain a consistent winding order, because reversing the winding order flips the normal, and if you're not aware of this, you can get some difficult-to-fix bugs. 

The normal vector is calculated by finding the perpendicular vector of the vector between the start and end points of the line/edge in question. This is where the winding order becomes relevant, because it tells us which vertex should be considered the start vertex, and which vertex should be considered the end. If we are storing our vertices in an array, and we specify a clockwise winding order, vertices with a higher index will be more clockwise than vertices with a lower one. If we specify a counterclockwise winding order, then vertices with a higher index will be more counterclockwise than those with a lower one.

TODO: INSERT DIAGRAM TO SHOW WINDING ORDER AND ARRAYS

There is an additional complication in 2D, namely the fact that every vector has two normals. These are sometimes called *right* and *left* normals or *clockwise* and *counterclockwise* normals.

NB. The $\perp$ symbol means perpendicular.

For a vector $\vec{A}$ between two points, the normals are given as follows:

Clockwise/right:
$$\vec{A}_\perp = (A_y, -A_x)$$

CCW/left:
$$\vec{A}_\perp = (-A_y, A_x)$$

This can get very confusing very fast, especially if you start wondering whether or not Y is up (as in the regular mathematical geometry) or down (a convention which lots of graphics rendering libraries prefer). Interestingly enough, as long as you remain consistent, it shouldn't be a big problem, because the mathematics (generally) abstracts away the problems of geometrical visualization.

TODO: Insert figure with example

An aside on confusing terminology: The normal vector is often (but not always) given as a unit vector. The process of turning any vector into a unit vector is called *normalization*, but the vector itself doesn't have to be a normal vector.

The normal vector is often used to specify what direction an edge of a geometric object is facing. For example, in a coordinate system where X increases to the right and Y increases going up, a normal vector of (1, 1) means the edge it is associated with points up and to the right, and a normal vector of (-1, 0) means that edge faces the left. 

The normal vector can be said to specify a unique edge in 2D or a unique plane in 3D. This creates the concept of points being in front of or behind the plane.

A point is considered in front of an edge when its direction relative to the edge is the same sign as its normal and the magnitude is greater. For example, for an edge with a normal of (-3, 0), which means it faces left, a point at (-5, 0) is considered in front of it, because it is to the left of the edge, while a point at (2, 0) is considered to be behind it, as it is to the right of the normal direction. 

For normals at an angle, visual description becomes a bit more difficult, but its not hard to determine mathematically. For an edge between two points $\vec{A}$ and $\vec{B}$, we can determine if $\vec{C}$ is front of, behind or on the edge as follows:

$$\vec{AB} = B - A$$
$$\vec{AC} = C - A$$
$$\vec{AB_\perp}\cdot\vec{AC}=d$$

If d is less than 0, the point is behind the edge. If d is greater than 0, the point is in front of the edge. If d is equal to 0, the point is on the edge (good luck getting that one while battling with floating point precision).

### Intersections and Collision Manifolds

An intersection between two polygons is defined by one or more of the vertices of one polygon touching or being inside the boundaries of another polygon.

During the narrow-phase collision detection of a physics engine, one polygon is tested with all the other polygons in its proximity for an intersection (polygons not in proximity would have already been filtered out by broad phase collision detection). The least efficient implementation of this main loop excludes broad-phase collision detection, and is an $O(n^2)$ nested iteration between the polygon and every other polygon in the world.

By convention, the polygon being tested against every other polygon in the world is called A and each of the other polygons in the world that are being iterated through is called B during its turn. This is the convention I'll use for the rest of the document.

A collision is an intersection that gives a physical response. The bare minimum needed (from the collision detector) to calculate a collision are the two polygons involved, the collision normal and the penetration depth. This gives us enough data for a linear collision response. This is not enough data for a rotational collision response, which I will get to in a minute.

The collision normal is the direction the collision takes place in. The convention I use here is that the direction of the vector is from polygon B to polygon A - but other people might use different conventions, so keep that in mind. In other words, in these examples, collisions are given relative to polygon A.

The penetration depth tells us how far in the direction of the collision normal object B interpenetrates object A.

Using these two pieces of data, we can calculate how much to push objects A and B away from each other when they interpenetrate, to resolve (get rid of) the intersection. This is of course an approximation, as in real life, rigid objects don't interpenetrate each other, but this happens in discrete time simulations, so we have to resolve it to give believable behaviour.

The collision is the response ie. change in linear and/or angular velocity etc. that resolves the intersection. To calculate a full collision response, we need other things from the physics engine that don't fall under the purview of the collision detector, such as the object's masses, their coefficients of restitution, moments of inertia, closing velocities etc. This document is concerned with intersection testing, not collision response, so those won't be covered here.

While we can derive linear collision response using only the penetration depth and collision normal, we need more data to derive an angular collision response (eg. a pool ball spinning after it gets hit by a cue stick). The additional data we need from the collision detector to generate an angular collision response is in the form of the contact points, ie. at which points did the two polygons touch. 

These contact points form a collision manifold, which is defined as a "collection of contact points that form all of the necessary constraints that allow the object to properly resolve all penetrations" (Game Technology Group, 2017).

We use these contact points to calculate impulsive torques, to rotate the object during collisions as necessary. These are generated by the Sutherland-Hodge polygon clipping algorithm.

