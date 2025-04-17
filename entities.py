import pygame as pg
from GameSettings import *
import math
vec = pg.math.Vector2  # 2D vectorklasse uit Pygame, handig voor richting/snelheid

entitylijst = []  # Globale lijst met alle entiteiten in de wereld

# Klasse voor de speler
class Player():
    def __init__(self,game,x,y, kleur):
        self.game = game
        self.image = pg.Surface((TILESIZE,TILESIZE))  # Vierkant oppervlak van 1 tile
        self.image.fill(kleur)  # Kleur instellen
        self.vx = 0  # horizontale snelheid
        self.vy = 0  # verticale snelheid
        self.rect = self.image.get_rect()  # Bepaal hitbox
        self.x = x * TILESIZE  # Initiele positie in pixels
        self.y = y * TILESIZE

    def get_keys(self):
        self.vx, self.vy = 0, 0  # Reset snelheid
        keys  = pg.key.get_pressed()  # Lees toetsenbordinput
        if keys[pg.K_ESCAPE]:
            pg.quit()
            exit()
        # Richtingsinput via QZSD en pijltjes
        if keys[pg.K_q] or keys[pg.K_LEFT]:
            self.vx = -SPELER_SNELHEID
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vx = SPELER_SNELHEID
        if keys[pg.K_z] or keys[pg.K_UP]:
            self.vy = -SPELER_SNELHEID
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vy = SPELER_SNELHEID
        # Diagonale snelheid normaliseren
        if self.vx != 0 and self.vy != 0:
            self.vy *= math.sqrt(2)/2
            self.vx *= math.sqrt(2)/2

    def object_collision(self):
        collisionlist = []
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):  # Check overlap speler <-> muur
                collisionlist.append(wall)
        return collisionlist

    def collide_with_walls(self, dir):
        hits = self.object_collision()
        for wall in hits:
            if dir == 'x':
                if self.vx > 0:
                    self.x = wall.rect.left - self.rect.width
                elif self.vx < 0:
                    self.x = wall.rect.right
                self.vx = 0
                self.rect.x = self.x
            elif dir == 'y':
                if self.vy > 0:
                    self.y = wall.rect.top - self.rect.height
                elif self.vy < 0:
                    self.y = wall.rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

# Klasse voor muren
class Wall():
    def __init__(self, game, x, y):
        self.game = game
        self.kleur = GROEN
        self.image = pg.Surface((TILESIZE,TILESIZE))  # Standaard grootte
        self.image.fill(self.kleur)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x*TILESIZE
        self.rect.y = y*TILESIZE

    def update(self):
        pass  # Placeholder voor toekomstige logica

# Eerste guard-klasse
class Guard0():
    def __init__(self,game,x,y,route):
        self.game = game
        self.checkpoint = 0
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(ROOD)
        self.rect = self.image.get_rect()
        self.vx = 0
        self.vy = 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        self.route = route
        self.currentpos = route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = route[self.checkpoint+1]
        self.next_pos = self.next_patrol_pos

    def navigate(self,start,end):
        # Richt snelheid op richting tussen start en eindpunt met goniometrie
        self.vx = GUARD_SNELHEID*((end[0]*TILESIZE - start[0]*TILESIZE)/math.hypot(end[0]*TILESIZE - start[0]*TILESIZE, end[1]*TILESIZE - start[1]*TILESIZE))
        self.vy = GUARD_SNELHEID*((end[1]*TILESIZE - start[1]*TILESIZE)/math.hypot(end[0]*TILESIZE - start[0]*TILESIZE, end[1]*TILESIZE - start[1]*TILESIZE))

    def bot_at_checkpoint(self):
        # Check of guard dicht genoeg bij doel is (marge = 3 pixels)
        return (self.next_pos[0]*TILESIZE - 3 <= self.x <= self.next_pos[0]*TILESIZE + 3) and (self.next_pos[1]*TILESIZE - 3 <= self.y <= self.next_pos[1]*TILESIZE + 3)

    def update(self):
        if not self.bot_at_checkpoint():
            self.navigate(self.current_route_pos,self.next_pos)
        else:
            self.vx = 0
            self.x = self.next_pos[0]*TILESIZE
            self.vy = 0
            self.y = self.next_pos[1]*TILESIZE
            self.checkpoint = (self.checkpoint+1)%len(self.route)
            self.current_route_pos = self.next_pos
            self.next_pos = self.route[(self.checkpoint+1)%len(self.route)]
        self.x += self.vx * self.game.dt
        self.rect.x = self.x
        self.y += self.vy * self.game.dt
        self.rect.y = self.y

# Guard met rotatie en vectorgebaseerde navigatie
class Guard1(Guard0):
    def __init__(self, game, x, y, route):
        self.game = game
        self.checkpoint = 0
        self.route = route
        self.currentpos = route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = route[self.checkpoint+1]
        self.next_pos = self.next_patrol_pos
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(ROOD)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.x = x
        self.y = y
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.rot_to_player = 0

    def locate_player(self):
        dx, dy = abs(self.x - self.game.player.x), abs(self.y - self.game.player.y)
        if dx == 0:
            self.rot_to_player = 90
        else:
            self.rot_to_player = math.atan(dy/dx)*360/(2*math.pi)
        if self.x - self.game.player.x > 0:
            self.rot_to_player = 180 - self.rot
        if self.y - self.game.player.y < 0:
            self.rot_to_player *= -1

    def navigate(self, start, end):
        dx, dy = abs(start[0] - end[0]), abs(start[1] - end[1])
        if dx == 0:
            self.rot = 90
        else:
            self.rot = math.atan(dy/dx)*360/(2*math.pi)
        if start[0]-end[0] > 0:
            self.rot = 180 - self.rot
        if start[1]-end[1] < 0:
            self.rot *= -1

    def drawfront(self):
        self.front_point = self.rect.center + vec(TILESIZE, 0).rotate(-self.rot)
        self.front_point += self.game.camera.camera.topleft
        pg.draw.circle(self.game.screen, ZWART, self.front_point , 3)

    def update(self):
        if not self.bot_at_checkpoint():
            self.navigate([self.pos[0]/TILESIZE, self.pos[1]/TILESIZE], self.next_pos)
        else:
            print("nice :)")
            self.vel = vec(0, 0)
            self.pos = vec(self.next_pos[0], self.next_pos[1])*TILESIZE
            self.x, self.y = self.pos
            self.checkpoint = (self.checkpoint+1)%len(self.route)
            self.current_route_pos = self.next_pos
            self.next_pos = self.route[(self.checkpoint+1)%len(self.route)]
        self.vel = vec(GUARD_SNELHEID, 0).rotate(-self.rot)
        self.pos += self.vel*self.game.dt
        self.x, self.y = round(self.pos[0]), round(self.pos[1])
        self.rect.x, self.rect.y = self.pos

# Guard met gezichtsveld en fasesysteem
class Guard(Guard1):
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        fases = ["patroule", "chase", "retreat"]  # Mogelijke gedragsfases
        self.fase = fases[0]
        self.vwidth = VIZIE_BREEDTE  # Breedte gezichtsveld (halve hoek)
        self.vdist = VIEW_DIST  # Zichtafstand in pixels

    def locate_player(self):
        return super().locate_player()
    
    def navigate(self, start, end):
        return super().navigate(start, end)

    def drawvieuwfield(self):
        # Middenpunt van guard + offset van camera
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
    
        mid_angle_rad = math.radians(-self.rot)
        half_angle = math.radians(self.vwidth)
        num_points = 30  # resolutie van de sector (hoe hoger, hoe gladder)
        points = [center]

        # Bereken punten langs de rand van de sector
        for i in range(num_points + 1):
            angle = mid_angle_rad - half_angle + (2 * half_angle) * (i / num_points)
            point = center + vec(self.vdist, 0).rotate_rad(angle)
            points.append(point)

        # Teken het gezichtsveld
        pg.draw.polygon(self.game.screen, ZWART, points)

    def update(self):
        return super().update()