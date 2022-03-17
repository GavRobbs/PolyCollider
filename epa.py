import gjk
from utils.utilbase import *

class ExpandingPolytopeAlgorithm(gjk.GJKAlgorithm):
    def __init__(self, polyA, polyB):
        super().__init__(polyA, polyB)
        self.TOLERANCE = 0.001
    def calculate(self):
        """ We are going to use the simplex left over from a successful run of GJK to calculate the collision normal and penetration depth. A simplex is a regular polytope, so that makes our life a lot easier. If there is no collision from the GJK phase, we return false. """

        result = super().calculate()

        if result == False:
            return (False, 0, Vector(0.0, 0.0))

        #Turn our simplex into a polytope
        polytope = self.final_simplex[:]

        minIndex = 0
        minDistance = float("inf")
        minNormal = None

        #Find the closest edge to the origin
        #Get its normal
        #Get the support point corresponding to that normal
        while minDistance == float('inf'):

            for i in range(len(polytope)):
                j = (i + 1) % len(polytope)

                vertI = Vector(polytope[i].x, polytope[i].y)
                vertJ = Vector(polytope[j].x, polytope[j].y)

                ijvec = vertJ - vertI

                normal = Vector(ijvec.y, -ijvec.x)
                normal.normalize()
                distance = normal.dot(vertI)

                if(distance < 0):
                    distance *= -1.0
                    normal = normal * -1.0

                if(distance < minDistance):
                    minDistance = distance
                    minNormal = normal
                    minIndex = j

            supportPoint = getMinkowskiDifference(self.polygonA, self.polygonB, minNormal)
            supportDistance = minNormal.dot(supportPoint)

            #If the distance of the support point along the normal and the distance of the edge from the normal are within tolerance
            #the algorithm is done. Otherwise, we insert that point into our polytope and go again.
            if(abs(supportDistance - minDistance) > self.TOLERANCE):
                minDistance = float('inf')
                polytope.insert(minIndex, supportPoint)
        
        return (True, minDistance + self.TOLERANCE, minNormal * -1)
 
if __name__ == '__main__':
    polyA = Polygon(Vector(165.0, 175.0))
    polyA.addPoint(Vector(0.0, -60.0))
    polyA.addPoint(Vector(60.0, 60.0))
    polyA.addPoint(Vector(-60.0, 60.0))

    polyB = Polygon(Vector(205, 175))
    angle = 2.0 * math.pi / 9.0
    for i in range(0, -9, -1):
        newPt = Vector(55 * math.cos(angle * i), 55 * math.sin(angle * i))
        polyB.addPoint(newPt)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("EPA Demo")

    running = True

    clock = pygame.time.Clock()

    currentControl = 1
    speed = 6.0
    
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
        else:
            polyB.origin += Vector(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed * 0.1666

        myEPA = ExpandingPolytopeAlgorithm(polyA, polyB)
        (isColliding, penetrationDepth, normal_vector) = myEPA.calculate()

        screen.fill((0, 0, 0))
        drawPolygon(screen, myEPA.polygonA, color = (255, 255, 255) if not isColliding else (255, 0, 0))
        drawPolygon(screen, myEPA.polygonB, color = (255, 255, 255) if not isColliding else (255, 0, 0))

        if isColliding:
            font = pygame.font.SysFont(None, 24)
            penDImg = font.render("Penetration Depth " + str(round(penetrationDepth, 2)), True, (255, 255, 255))
            normImg = font.render("Normal " + str(normal_vector), True, (255, 255, 255))
            screen.blit(penDImg, (500, 500))
            screen.blit(normImg, (500, 550))        

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

