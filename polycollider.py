import epa
from utils.utilbase import *

class PolyCollider(epa.ExpandingPolytopeAlgorithm):
    def __init__(self, polyA, polyB):
        super().__init__(polyA, polyB)
        self.polyAPoints = polyA.getTransformedPoints()[0]
        self.polyBPoints = polyB.getTransformedPoints()[0]
        self.polyAEdges = polyA.getEdgeList()
        self.polyBEdges = polyB.getEdgeList()
        self.TOLERANCE = 0.0001


    def __calculateIntersectionPoint(self, p1, p2, p3, p4):
        denominator = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        commonA = (p1.x * p2.y - p1.y * p2.x)
        commonB = (p3.x * p4.y - p3.y * p4.x)
        numeratorX = commonA * (p3.x - p4.x) - (p1.x - p2.x) * commonB
        numeratorY = commonA * (p3.y - p4.y) - (p1.y - p2.y) * commonB
        return Vector(numeratorX/denominator, numeratorY/denominator)
            
    def __findSignificantEdges(self, normal):
        #We find the significant faces in the collision (one for each poly)
        #There are two criteria for the significant face:
        # 1) The face must contain the vertex furthest along the collision normal
        # 2) The face must be closest to parallel with the collision normal out
        # of all the faces containing the significant vertex

        polyASignificantVertices = set()
        polyBSignificantVertices = set()

        #This part is a bit clunky, need to rewrite it
        maxADotProduct = max(self.polyAPoints, key=lambda pt: pt.dot(normal *-1.0)).dot(normal *-1.0)
        maxBDotProduct = max(self.polyBPoints, key=lambda pt: pt.dot(normal)).dot(normal)

        for vertex in self.polyAPoints:
            if vertex.dot(normal * -1.0) == maxADotProduct:
                polyASignificantVertices.add(vertex)

        for vertex in self.polyBPoints:
            if vertex.dot(normal) == maxBDotProduct:
                polyBSignificantVertices.add(vertex)

        polyACandidateEdges = set()
        polyBCandidateEdges = set()

        for vertex in polyASignificantVertices:
            ecv = self.polyAEdges.getEdgesContainingVertex(vertex, self.polyAPoints)
            for vert in ecv:
                polyACandidateEdges.add(vert)

        for vertex in polyBSignificantVertices:
            ecv = self.polyBEdges.getEdgesContainingVertex(vertex, self.polyBPoints)
            for vert in ecv:
                polyBCandidateEdges.add(vert)

        #We derive the reference face by looking at the one closest
        #to parallel with the normal
        a_derived_edge = max(polyACandidateEdges, key=lambda edge: edge.getNormal(self.polyAPoints).dot(normal * -1.0))
        b_derived_edge = max(polyBCandidateEdges, key=lambda edge: edge.getNormal(self.polyBPoints).dot(normal))

        a_closeness = abs(a_derived_edge.getNormal(self.polyAPoints).dot(normal * -1.0))
        b_closeness = abs(b_derived_edge.getNormal(self.polyBPoints).dot(normal))

        referenceEdge = None
        incidentEdge = None
        referenceFrom = ""

        if a_closeness > b_closeness:
            referenceEdge = a_derived_edge
            incidentEdge = b_derived_edge
            referenceFrom = 'A'
        else:
            referenceEdge = b_derived_edge
            incidentEdge = a_derived_edge
            referenceFrom = 'B'

        return (referenceEdge, incidentEdge, referenceFrom)

    def __clip(self, to_clip, clipEdge, clipPolygonPoints, invert=False):
        temp_list = [vert for vert in to_clip]
        temp_output = []
        numPoints = len(temp_list)
        edgeNormal = clipEdge.getNormal(clipPolygonPoints)

        if invert is True:
            edgeNormal = edgeNormal * -1.0

        startVertex = clipPolygonPoints[clipEdge.startIndex]
        endVertex = clipPolygonPoints[clipEdge.endIndex]

        for i in range(0, numPoints):
            
            startIndex = i %  numPoints
            endIndex = (i + 1) % numPoints

            firstVertex = temp_list[startIndex]
            secondVertex = temp_list[endIndex]

            firstVertexInside = (firstVertex - startVertex).dot(edgeNormal) < 0
            secondVertexInside = (secondVertex - startVertex).dot(edgeNormal) < 0

            if firstVertexInside and secondVertexInside:
                #If both vertices are inside, we only need the second one
                temp_output.append(secondVertex)
            elif not firstVertexInside and not secondVertexInside:
                #If neither vertex is inside, we discard them
                pass
            elif firstVertexInside and not secondVertexInside:
                #If the first vertex is inside and the second is outside
                #we calculate a new point, the intersection of the
                #line between the two vertices with the clip edge
                new_point = self.__calculateIntersectionPoint(firstVertex, secondVertex, startVertex, endVertex)
                temp_output.append(new_point)
            elif not firstVertexInside and secondVertexInside:
                new_point = self.__calculateIntersectionPoint(firstVertex, secondVertex, startVertex, endVertex)
                temp_output.append(new_point)
                temp_output.append(secondVertex)

        temp_list = [point for point in temp_output]
       
        return temp_list

        
    def calculate(self):

        (hasCollision, penetrationDepth, normal) = super().calculate()

        if hasCollision == False:
            return (False, 0.0, None, [])

        (referenceEdge, incidentEdge, referenceFrom) = self.__findSignificantEdges(normal)
        points_to_clip = []
        clipped = []
        
        if referenceFrom == 'A':
            points_to_clip = [point for point in self.polyBPoints]
            adjacents = self.polyAEdges.getAdjacentEdges(referenceEdge, self.polyAPoints)

            #We clip our incident polygon with the adjacent edges of the reference polygon
            for edge in adjacents:
                points_to_clip = self.__clip(points_to_clip, edge, self.polyAPoints, False)

            #then we only keep the vertices that are inside the reference polygon
            clipped = self.__clip(points_to_clip, referenceEdge, self.polyAPoints, False)


        else:
            points_to_clip = [point for point in self.polyAPoints]
            adjacents = self.polyBEdges.getAdjacentEdges(referenceEdge, self.polyBPoints)

            for edge in adjacents:
                points_to_clip = self.__clip(points_to_clip, edge, self.polyBPoints, False)

            clipped = self.__clip(points_to_clip, referenceEdge, self.polyBPoints, False)

        return (True, penetrationDepth, normal, clipped)

if __name__ == '__main__':
    polyA = Polygon(Vector(165.0, 175.0))
    polyA.addPoint(Vector(-60.0, -60.0))
    polyA.addPoint(Vector(-60.0, 60.0))
    polyA.addPoint(Vector(60.0, 60.0))
    polyA.addPoint(Vector(60.0, -60.0))


    polyB = Polygon(Vector(405, 255))
    polyB.addPoint(Vector(-160.0, -160.0))
    polyB.addPoint(Vector(-160.0, 160.0))
    polyB.addPoint(Vector(160.0, 160.0))
    polyB.addPoint(Vector(160.0, -160.0))
    #angle = 2.0 * math.pi / 16.0
    #for i in range(0, -16, -1):
    #    newPt = Vector(120 * math.cos(angle * i), 120 * math.sin(angle * i))
    #    polyB.addPoint(newPt)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sutherland-Hodge Algorithm Demo")

    running = True

    clock = pygame.time.Clock()

    currentControl = 1
    speed = 6.0
    rot_speed = 0.15
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    currentControl = 1
                elif event.key == pygame.K_2:
                    currentControl = 2

        keys = pygame.key.get_pressed()
        if currentControl == 1:
            polyA.origin += Vector(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed * 0.1666
            polyA.rotation += keys[pygame.K_r] * rot_speed * 0.1666

        else:
            polyB.origin += Vector(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed * 0.1666
            polyB.rotation += keys[pygame.K_r] * rot_speed * 0.1666

        myPC = PolyCollider(polyA, polyB)
        (isColliding, penetrationDepth, normal_vector, collisionPoints) = myPC.calculate()

        screen.fill((0, 0, 0))
        drawPolygon(screen, myPC.polygonA, color = (255, 255, 255) if not isColliding else (255, 0, 0))
        drawPolygon(screen, myPC.polygonB, color = (255, 255, 255) if not isColliding else (255, 0, 0))

        if isColliding:
            font = pygame.font.SysFont(None, 24)
            penDepthText = font.render("Penetration Depth " + str(round(penetrationDepth, 2)), True, (255, 255, 255))
            normDirText = font.render("Normal " + str(normal_vector), True, (255, 255, 255))
            screen.blit(penDepthText, (500, 500))
            screen.blit(normDirText, (500, 550))

            for point in collisionPoints:
                print(str(point))
                drawCircle(screen, point, 3.0, color=(0, 0, 255))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

        


