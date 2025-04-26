import pygame as pg 
import math
from GameSettings import *

vec = pg.math.Vector2  # Verkorte notatie voor 2D vectoren (handig voor posities en snelheden)
entitylijst = []  # Globale lijst waarin alle actieve entiteiten worden bijgehouden


class Entity:
    # Basisklasse voor alle objecten in de game zoals muren, speler, guards, etc.

    def __init__(self, game, x, y, image_path=None, color=None):
        self.game = game
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.pos = vec(self.x, self.y)  # Vectorpositie in pixels

        self.image = pg.Surface((TILESIZE, TILESIZE))  # Maak standaardoppervlak aan

        if image_path:
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))  # Schaal naar tilegrootte
        elif color:
            self.image.fill(color)  # Kleur het vlak
        else:
            self.image.fill(WIT)  # Fallback kleur

        self.rect = self.image.get_rect(topleft=(self.x, self.y))  # Bepaal de plek op het scherm

    def update(self):
        # Update logica voor het object; enkel positie herberekenen
        self.rect.topleft = (self.x, self.y)



class Player(Entity):
    def __init__(self, game, x, y, kleur):
        super().__init__(game, x, y, color=kleur)
        self.vx = 0  # snelheid x
        self.vy = 0  # snelheid y
        self.speed = SPELER_SNELHEID

    def update(self):
        # Verwerk input → beweeg → botsingscontrole → check op guards
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

    def get_keys(self):
        # Leest toetseninvoer en zet bijhorende snelheden
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_q] or keys[pg.K_LEFT]:
            self.vx = -self.speed
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vx = self.speed
        if keys[pg.K_z] or keys[pg.K_UP]:
            self.vy = -self.speed
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vy = self.speed

        # Beweging diagonaal? → compenseren voor constante snelheid
        if self.vx != 0 and self.vy != 0:
            self.vy *= math.sqrt(2) / 2
            self.vx *= math.sqrt(2) / 2

#BOTSINGEN MET MUREN:---
    def collide_with_walls(self, direction): #corrigeert botsingen
        hits = self.object_collision()
        for wall in hits:
            if direction == 'x':
                if self.vx > 0:
                    self.x = wall.rect.left - self.rect.width
                elif self.vx < 0:
                    self.x = wall.rect.right
                self.vx = 0
                self.rect.x = self.x
            elif direction == 'y':
                if self.vy > 0:
                    self.y = wall.rect.top - self.rect.height
                elif self.vy < 0:
                    self.y = wall.rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def object_collision(self): #checkt voor botsingen
        collisionlist = []
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                collisionlist.append(wall)
        return collisionlist
#---


class Wall(Entity):
    # Muurobject (botsbaar voor speler en guards)
    def __init__(self, game, x, y):
        super().__init__(game, x, y, color=GROEN)

    def update(self):
        pass  # Muren zijn voorlopig nog statisch



class Guard0(Entity): #aller eerste versie van de guards NIET MEER AANPASSEN
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

class Guard1(Guard0): #guards met vectorgebaseerde movement NIET MEER AANPASSEN
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

class Guard(Guard1):#guards kunnen spelers detecteren en varieren tussen verschillende fases zoals patrol, chase, retreat, ... NIET MEER AANPASSEN
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        self.fases = ["patrol", "chase", "search", "retreat"]
        self.fase = "patrol"
        self.vBREEDTE = VIZIE_BREEDTE
        self.vdist = VIEW_DIST
        self.speeds = {
            "patrol": GUARD_SNELHEID,
            "chase": GUARD_SNELHEID_CHASE,
            "search": GUARD_SNELHEID*2,
            "retreat": GUARD_SNELHEID*2
        }
        self.laatste_zichttijd = 0
        self.retreat_target = None
        self.vRESOLUTIE = RESOLUTIE

        self.search_start_time = 0
        self.search_duration = SEARCH_TIME  # 3 seconden zoeken
        self.searching = False


    def update(self):
        tijd_nu = pg.time.get_ticks()
        self.get_fase(tijd_nu) #Bepaal huidige fase

        # Fase-afhandeling
        if self.fase == "patrol": #Gebruik de gewone update() van de vorige guard class: patrouilleer tussen de checkpoints
            super().update()

        elif self.fase == "chase":
            speler_pos = vec(self.game.player.rect.center)
            richting = speler_pos - self.pos
            if richting.length() > 0:
                self.rot = richting.angle_to(vec(1, 0))
                self.move()
                self.x, self.y = round(self.pos.x), round(self.pos.y)
                self.rect.x, self.rect.y = self.pos
                self.collide_with_walls()

        elif self.fase == "search":
            if not self.searching:
            # Net aangekomen op laatst gekende locatie
                richting = self.last_known_player_pos - self.pos
                if richting.length() > 3:
                    self.rot = richting.angle_to(vec(1, 0))
                    self.move()
                    self.x, self.y = round(self.pos.x), round(self.pos.y)
                    self.rect.x, self.rect.y = self.pos
                    self.collide_with_walls()
                else:
                    # Aangekomen, start zoekfase
                    self.vel = vec(0, 0)
                    self.pos = self.last_known_player_pos
                    self.x, self.y = self.pos
                    self.rect.x, self.rect.y = self.pos
                    self.search_start_time = pg.time.get_ticks()
                    self.searching = True
            else:
                # Zoekanimatie: 360° draaien
                self.rot += ROT_SPEED * self.game.dt  # Langzaam ronddraaien

        elif self.fase == "retreat":
            retreat_vec = vec(self.retreat_target) * TILESIZE
            richting = retreat_vec - self.pos
            if richting.length() > 3:
                self.rot = richting.angle_to(vec(1, 0))
                self.move()
                self.x, self.y = round(self.pos.x), round(self.pos.y)
                self.rect.x, self.rect.y = self.pos
                self.collide_with_walls()


    def get_fase(self, tijd_nu): #Bepaald de eventuele nieuwe fase van de guard. Merk op dat van search naar retreat automatisch gebeurd en gewoon in de search_behavior() zit.
        if self.heeft_zicht_op_speler():
            self.fase = "chase"

        elif self.fase == "chase":
            if tijd_nu - self.laatste_zichttijd > CHASE_TIME:
                self.fase = "search"
                self.searching = False

        elif self.fase == "retreat":
            richting = vec(self.retreat_target) * TILESIZE - self.pos
            if richting.length() < 3:
                self.pos = vec(self.retreat_target) * TILESIZE
                self.x, self.y = self.pos
                self.rect.x, self.rect.y = self.pos
                self.fase = "patrol"

        elif self.fase == "search" and self.searching and tijd_nu - self.search_start_time >= self.search_duration: #als de guard in ze zoekfase echt aan het zoeken is dit al langer dan de search_duration time: 
            self.fase = "retreat"
            self.searching = False
            self.bepaal_retreat_punt()
    

    def heeft_zicht_op_speler(self):
        # Controleer meerdere zichtpunten van de speler
        zichtpunten = [vec(self.game.player.rect.topleft), vec(self.game.player.rect.topright),
                                        vec(self.game.player.rect.center), 
                       vec(self.game.player.rect.bottomleft), vec(self.game.player.rect.bottomright)]

        guard_pos = vec(self.rect.center)
        facing = vec(1, 0).rotate(-self.rot)

        for punt in zichtpunten:
            richting = punt - guard_pos
            afstand = richting.length()

            if afstand > self.vdist:
                continue  # Te ver weg

            hoek_tov_front = richting.angle_to(facing)
            if abs(hoek_tov_front) > self.vBREEDTE:
                continue  # Buiten gezichtsveld

            if self.line_of_sight_clear(guard_pos, punt):
                self.laatste_zichttijd = pg.time.get_ticks()
                self.last_known_player_pos = vec(self.game.player.rect.center)
                return True  # Zichtlijn naar minstens één punt is vrij
        return False


    def line_of_sight_clear(self, start, end): #zie of er geen muur in de weg staat
        delta = end - start
        steps = int(delta.length() // 4)
        for i in range(1, steps + 1):
            point = start + delta * (i / steps)
            point_rect = pg.Rect(point.x, point.y, 2, 2)  # klein vakje
            for wall in self.game.walls:
                if wall.rect.colliderect(point_rect):
                    return False
        return True
    

    def move(self): #gebruikt in update(), afhankelijk van de fase want soms moet men niet bewegen, maar zo is het korter
        self.vel = vec(self.speeds[self.fase],0).rotate(-self.rot)
        self.pos += self.vel * self.game.dt


    def bepaal_retreat_punt(self):
        # Zoek dichtstbijzijnde waypoint in route
        min_afstand = float("inf")
        dichtstbij = None
        for punt in self.route:
            punt_px = vec(punt) * TILESIZE
            afstand = (self.pos - punt_px).length_squared()
            if afstand < min_afstand:
                min_afstand = afstand
                dichtstbij = punt
        self.retreat_target = dichtstbij


    def collide_with_walls(self):
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                if self.vel.x > 0:
                    self.x = wall.rect.left - self.rect.width
                elif self.vel.x < 0:
                    self.x = wall.rect.right
                if self.vel.y > 0:
                    self.y = wall.rect.top - self.rect.height
                elif self.vel.y < 0:
                    self.y = wall.rect.bottom
                self.vel = vec(0, 0)
                self.rect.x = self.x
                self.rect.y = self.y


    def drawvieuwfield(self):
        if self.fase == "chase":
            kleur = LICHTROOD
            self.vdist = 2*VIEW_DIST
            self.vBREEDTE = VIZIE_BREEDTE/2
        else:
            kleur = ZWART
            self.vdist = VIEW_DIST
            self.vBREEDTE = VIZIE_BREEDTE

        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        mid_angle_rad = math.radians(-self.rot)
        half_angle = math.radians(self.vBREEDTE)
        points = [center]

        for i in range(self.vRESOLUTIE + 1):  # +1 zodat laatste punt exact op de randhoek ligt
            angle = mid_angle_rad - half_angle + (2 * half_angle) * (i / self.vRESOLUTIE)
            point = center + vec(self.vdist, 0).rotate_rad(angle)
            points.append(point)

        pg.draw.polygon(self.game.screen, kleur, points, 2)


class Trap(Entity):
    def update(self):
        pass  # Mogelijkheid voor val/logica

class Item(Entity):
    def update(self):
        pass  # Kan gebruikt worden voor pickup-objecten