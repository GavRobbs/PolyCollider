from utils.utilbase import *
import math
import pygame

class GJKAlgorithm:
    def __init__(self, polyA, polyB):
        self.polygonA = polyA
        self.polygonB = polyB
        self.final_simplex = None

    def __doSimplex(self, simplex):

        """ This function evolves the simplex in GJK speak - it first checks if the simplex has 2 or 3 points. If it has 2 points, it uses a trick with barycentric coordinates to calculate the direction of the closest point to the origin - see Erin Catto's slides.
        
        If the simplex already has 3 points, then we check to see if the origin is contained in it, and return True, otherwise we remove the non-contributing first point and get the direction of the closest point P on the remaining 1-simplex to the origin """
        direction = Vector(0.0, 0.0)

        if len(simplex) == 2:

            #This finds the direction of the nearest point to the origin using
            #the triple product, but this could also be calculated using
            #barycentric coordinates - see Erin Catto's GDC presentation

            simplex_vector = simplex[1] - simplex[0]
            to_origin = simplex[0] * -1
            direction = getTripleProduct(simplex_vector, to_origin, simplex_vector)
            return (simplex, direction, False)
        elif len(simplex) == 3:

            if(isPointInTriangle(Vector(0.0, 0.0), simplex[0], simplex[1], simplex[2])):
                return (simplex, direction, True)
            else:
                #Drop the first coordinate of the simplex generated
                #Find a new direction towards the origin, so you can get another
                #point to try
                simplex.pop(0)
                simplex_vector = simplex[1] - simplex[0]
                to_origin = simplex[0] * -1.0
                direction = getTripleProduct(simplex_vector, to_origin, simplex_vector)
                return (simplex, direction, False)

    def calculate(self):
        """ This main loop is taken from wikipedia. We pick an arbitrary starting direction and put it in our simplex - so we start with a 0-simplex. We then invert the direction of that point to get a second point, directly opposite to our starting point, creating our initial 1-simplex. The doSimplex function evolves the simplex, both returning the new direction that the simplex should check in for new support points to add, or any modifications to the simplex"""
        a = support(self.polygonA, self.polygonB, Vector(1.0, 0.0))
        simplex = [a]
        d = a * -1.0

        numIterations = 0

        while True:

            numIterations += 1

            #Stop this from blowing up
            if numIterations > 20:
                return False

            b = support(self.polygonA, self.polygonB, d)
            if(b.dot(d) < 0):
                return False
            else:
                simplex.append(b)
                simplex, d, contains_origin = self.__doSimplex(simplex)

                if contains_origin:
                    self.final_simplex = simplex
                    return True
                

if __name__ == '__main__':
    polyA = Polygon(Vector(215.0, 215.0))
    polyA.addPoint(Vector(0.0, 50.0))
    polyA.addPoint(Vector(50.0, 0.0))
    polyA.addPoint(Vector(-50.0, 0.0))

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



