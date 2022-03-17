import math
import pygame

class Vector:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    def __rmul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)
    def __str__(self):
        return "X: " + str(round(self.x, 3)) + " Y: " + str(round(self.y, 3))
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def getMagnitudeSquared(self):
        return (self.x * self.x + self.y * self.y)
    def getMagnitude(self):
        return math.sqrt(self.getMagnitudeSquared())
    def normalize(self):
        mylen = self.getMagnitude()
        self.x /= mylen
        self.y /= mylen
    def getNormalized(self):
        temp = Vector(self.x, self.y)
        temp.normalize()
        return temp
    def asList3(self):
        return [self.x, self.y, 0.0]
    def asList2(self):
        return [self.x, self.y]

class Edge:
    def __init__(self, referencePolygon, startIndex, endIndex):
        self.referencePolygon = referencePolygon
        self.startIndex = startIndex
        self.endIndex = endIndex

class Polygon:
    def __init__(self, origin=Vector(0, 0)):
        self.points = []
        self.origin = origin
    def addPoint(self, point):
        """Add a point to the polygon list, its up to you to ensure its counterclockwise"""
        self.points.append(point)
    def getEdgeList(self):
        """Gets a normalized list of the edges in the polygon, note that this is clockwise"""
        i = 0
        numPoints = len(self.points)
        edges = []
        while i < numPoints + 1:
            point1 = self.points[i % numPoints]
            point2 = self.points[(i + 1) % numPoints]
            edgeVector = (point2 - point1).normalize()
            edges.append(edgeVector)
            i += 1
        
        return edges
    def getSupportPoint(self, normal):
        return max(self.points, key=lambda pt: pt.dot(normal)) + self.origin

def getMinkowskiDifference(polyA, polyB, normal):
    return polyA.getSupportPoint(normal) - polyB.getSupportPoint(-1.0 * normal)

def getCrossProduct(p1, p2):
    return [p1[1] * p2[2] - p1[2] * p2[1], -(p1[0] * p2[2] - p1[2] * p2[0]), p1[0] * p2[1] - p1[1] * p2[0]]

def getTripleProduct(a, b, c):
    return b * (a.dot(c)) - c * (a.dot(b))

def isPointInTriangle(p, a, b, c):
    ab = b - a
    bc = c - b
    ca = a - c
    ap = p - a
    bp = p - b
    cp = p - c

    abap = getCrossProduct(ab.asList3(), ap.asList3())[2]
    bcbp = getCrossProduct(bc.asList3(), bp.asList3())[2]
    cacp = getCrossProduct(ca.asList3(), cp.asList3())[2]

    if(abap >= 0 and bcbp >= 0 and cacp >= 0):
        return True
    elif (abap < 0 and bcbp < 0 and cacp < 0):
        return True
    else:
        return False

def drawPolygon(screen, poly, color=(255, 255, 255)):
    points = [((point + poly.origin).x, (point + poly.origin).y) for point in poly.points]
    pygame.draw.polygon(screen, color, points, 3)
    pygame.draw.circle(screen, color, poly.origin.asList2(), 2, 0)

def drawLine(screen, start, end, color=(0, 255, 0)):
    pygame.draw.line(screen, color, start.asList2(), end.asList2(), 2)

def drawCircle(screen, origin, radius):
    pygame.draw.circle(screen, (255, 255, 0), origin.asList2(), radius, 0)