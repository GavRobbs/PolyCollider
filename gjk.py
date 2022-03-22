from utils.utilbase import *
import math
import pygame

class GJKAlgorithm:
    def __init__(self, polyA, polyB):
        self.polygonA = polyA
        self.polygonB = polyB
        self.final_simplex = None

    def calculate(self):
        """ We pick an arbitrary starting direction and put it in our simplex - so we start with a 0-simplex. We then invert the direction of that point to get a second point, directly opposite to our starting point, creating our initial 1-simplex. We then get the vector triple product to give us a perpendicular vector towards the origin to evolve our 2-simplex. In the main loop of the function, we check if the origin lies in either of the Voronoi regions. If the origin lies in the AB Voronoi region, then we create a perpendicular from AB pointing towards the origin, and set that as the new direction, then use it to replace C. If it lies in the AC Voronoi region, we create a perpendicular from AC pointing towards the origin and use that to replace B. If the origin is in neither Voronoi region, then it must be within the triangle formed by ABC, so we return true and terminate. Otherwise, we start the loop over and continue to evolve the simplex until our iteration limit is reached. """
        
        C = support(self.polygonA, self.polygonB, Vector(1.0, 0.0))
        d = C * -1.0
        B = support(self.polygonA, self.polygonB, d)
        if(B.dot(d) < 0):
            return False
        
        BC = C - B
        BO = B * -1.0
        d = getTripleProduct(BC, BO, BC)

        A = support(self.polygonA, self.polygonB, d)
        numIterations = 0

        while True:

            numIterations += 1

            #Stop this from blowing up, return if iteration limit reached
            if numIterations > 30:
                return False

            AB = B - A
            AC = C - A
            AbPerp = getTripleProduct(AC, AB, AB)
            AO = A * -1.0

            if AbPerp.dot(AO) >= 0:
                d = AbPerp
                C = support(self.polygonA, self.polygonB, d)
                continue

            AcPerp = getTripleProduct(AB, AC, AC)
            if AcPerp.dot(AO) >= 0:
                d = AcPerp
                B = support(self.polygonA, self.polygonB, d)
                continue

            self.final_simplex = [C, B, A]
            return True
                

if __name__ == '__main__':
    polyA = Polygon(Vector(215.0, 215.0))
    polyA.addPoint(Vector(0.0, 50.0))
    polyA.addPoint(Vector(-50.0, 0.0))
    polyA.addPoint(Vector(50.0, 0.0))

    polyB = Polygon(Vector(190, 190))
    angle = 2.0 * math.pi / 8.0
    for i in range(0, -8, -1):
        newPt = Vector(40 * math.cos(angle * i), 40.0 * math.sin(angle * i))
        polyB.addPoint(newPt)


    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("GJK Demo")

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


        myGJK = GJKAlgorithm(polyA, polyB)
        isColliding = myGJK.calculate()

        screen.fill((0, 0, 0))
        drawPolygon(screen, polyA, color = (255, 255, 255) if not isColliding else (255, 0, 0))
        drawPolygon(screen, polyB, color = (255, 255, 255) if not isColliding else (255, 0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



