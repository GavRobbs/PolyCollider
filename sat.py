from utils.utilbase import *

class SeparatingAxisTest:
    def __init__(self, polyA, polyB):
        self.polygonA = polyA
        self.polygonB = polyB
        
        self.polyAPoints = polyA.getTransformedPoints()[0]
        self.polyBPoints = polyB.getTransformedPoints()[0]

        #Generate a big list made up of all the potential separating axes of both polygons
        self.axes = [edge.getNormal(self.polyAPoints, True) for edge in polyA.getEdgeList().edges] + [edge.getNormal(self.polyBPoints, True) for edge in polyB.getEdgeList().edges]

    def calculate(self):

        leastOverlap = float('inf')
        leastOverlapAxis = self.axes[0]

        #We want our collision normals to point FROM B to A
        #In other words, vector BA, which is generated by the origin of point A - origin of point B
        #We will use this in a bit
        relativeVector = self.polygonA.origin - self.polygonB.origin

        for axis in self.axes:

            a_min, b_min = float('inf'), float('inf')
            a_max, b_max = float('-inf'), float('-inf')

            #Iterate through each axis, finding the Amin, Amax, Bmin and Bmax for each polygon on that axis

            for point in self.polyAPoints:
                projection = point.dot(axis)

                #Note that this is an if statement and not an elif
                #This caused a very subtle bug where my infinities were not being replaced
                #It is entirely possible that in an early iteration through the points, the minimum and maximum points
                #may be the exact same value - this corrects itself in subsequent iterations
                if projection < a_min:
                    a_min = projection
                if projection > a_max:
                    a_max = projection

            for point in self.polyBPoints:
                projection = point.dot(axis)

                if projection < b_min:
                    b_min = projection
                if projection > b_max:
                    b_max = projection

            #Check for overlap - we create an interval. If the interval is positive, we save it and its associated axis as our 
            # newest least overlap values If there is no overlap, we can exit early, since we have found a separating axis, so there
            # can't be any collision

            intervalMax = min(a_max, b_max)
            intervalMin = max(a_min, b_min)
            dist = intervalMax - intervalMin
            if dist < 0:
                #There is no overlap, so we have found a separating axis and can terminate early
                return (False, 0, None)
            
            if dist <= leastOverlap:
                #We found a new overlap interval less than or equal to our current one
                #We want to ensure that our direction vector points from B to A
                #By using the dot product, we compare the new and old overlap vector to our desired target direction BA
                #If the new vector is more in the direction of BA than the old one, then we replace the old vector
                #This is to keep our normals consistent
                newDot = relativeVector.dot(axis)
                oldDot = relativeVector.dot(leastOverlapAxis)

                if newDot > oldDot:
                    leastOverlap = dist
                    leastOverlapAxis = axis

        return (True, leastOverlap, leastOverlapAxis)

if __name__ == '__main__':
    polyA = Polygon(Vector(165.0, 175.0))
    polyA.addPoint(Vector(0.0, -60.0))
    polyA.addPoint(Vector(-60.0, 60.0))
    polyA.addPoint(Vector(60.0, 60.0))

    polyB = Polygon(Vector(320, 225))
    angle = 2.0 * math.pi / 9.0
    for i in range(0, -9, -1):
        newPt = Vector(55 * math.cos(angle * i), 55 * math.sin(angle * i))
        polyB.addPoint(newPt)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Separating Axis Test Demo")

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

        sat = SeparatingAxisTest(polyA, polyB)
        (isColliding, penetrationDepth, normal_vector) = sat.calculate()

        screen.fill((0, 0, 0))
        drawPolygon(screen, polyA, color = (255, 255, 255) if not isColliding else (255, 0, 0))
        drawPolygon(screen, polyB, color = (255, 255, 255) if not isColliding else (255, 0, 0))

        if isColliding:
            font = pygame.font.SysFont(None, 24)
            penDepthText = font.render("Penetration Depth " + str(round(penetrationDepth, 2)), True, (255, 255, 255))
            normDirText = font.render("Normal " + str(normal_vector), True, (255, 255, 255))
            screen.blit(penDepthText, (500, 500))
            screen.blit(normDirText, (500, 550))    

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()