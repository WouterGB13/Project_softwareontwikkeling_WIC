import pygame as pg 
import math
from GameSettings import *

vec = pg.math.Vector2  # Verkorte notatie voor 2D vectoren (handig voor posities en snelheden)

entitylijst = []  # Globale lijst waarin alle actieve entiteiten worden bijgehouden

class Entity:
    # Basisklasse voor alle objecten in de game zoals muren, speler, guards, etc.

    def __init__(self, game, x, y, image_path=None, color=None):
        """
        Initialisatie van een Entity met optioneel een afbeelding of kleur.

        x, y: coördinaten in tiles
        image_path: pad naar een afbeelding (optioneel)
        color: fallback kleur als geen afbeelding is meegegeven (optioneel)
        """
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
    # Klasse voor de speler, erft van Entity

    def __init__(self, game, x, y, kleur):
        super().__init__(game, x, y, color=kleur)  # Gebruik kleur i.p.v. afbeelding
        self.vx = 0  # snelheid op x-as
        self.vy = 0  # snelheid op y-as
        self.speed = SPELER_SNELHEID

    def get_keys(self):
        # Leest toetseninvoer en zet bijhorende snelheden
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()

        if keys[pg.K_ESCAPE]:
            pg.quit()
            exit()

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

    def object_collision(self):
        # Check voor botsing met muren (via rect)
        collisionlist = []
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                collisionlist.append(wall)
        return collisionlist

    def collide_with_walls(self, direction):
        # Corrigeer positie als speler tegen muur loopt (x of y richting)
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

    def update(self):
        # Verwerk input → beweeg → botsingscontrole → check op guards
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

        for entity in entitylijst:
            if isinstance(entity, Guard) and self.rect.colliderect(entity.rect):
                print("Speler gepakt door een guard! GAME OVER.")
                self.game.playing = False
                self.game.gameover = True

class Wall(Entity):
    # Muurobject (botsbaar voor speler en guards)
    def __init__(self, game, x, y):
        super().__init__(game, x, y, color=GROEN)

    def update(self):
        pass  # Muren zijn voorlopig nog statisch

class Guard0(Entity):
    # Eenvoudige guard die route loopt tussen waypoints

    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.speed = GUARD_SNELHEID
        self.set_next_target()

    def set_next_target(self):
        # Bepaal huidig en volgend waypoint
        self.currentpos = self.route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = self.route[(self.checkpoint + 1) % len(self.route)]
        self.next_pos = self.next_patrol_pos

    def navigate(self, start, end):
        # Bepaal snelheid richting volgende waypoint
        distance = math.hypot(end[0] * TILESIZE - start[0] * TILESIZE, end[1] * TILESIZE - start[1] * TILESIZE)
        if distance > 0:
            self.vx = self.speed * ((end[0] * TILESIZE - start[0] * TILESIZE) / distance)
            self.vy = self.speed * ((end[1] * TILESIZE - start[1] * TILESIZE) / distance)
        else:
            self.vx = 0
            self.vy = 0

    def bot_at_checkpoint(self):
        # Check of guard doel bereikt heeft (binnen marge van 3 pixels)
        return (self.next_pos[0] * TILESIZE - 3 <= self.x <= self.next_pos[0] * TILESIZE + 3) and \
               (self.next_pos[1] * TILESIZE - 3 <= self.y <= self.next_pos[1] * TILESIZE + 3)

    def update(self):
        # Navigatie updaten en volgende checkpoint instellen
        if not self.bot_at_checkpoint():
            self.navigate(self.current_route_pos, self.next_pos)
        else:
            self.vx = 0
            self.x = self.next_pos[0] * TILESIZE
            self.vy = 0
            self.y = self.next_pos[1] * TILESIZE
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.set_next_target()

        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.rect.y = self.y

class Guard1(Guard0):
    # Guard met oriëntatie/rotatie en geavanceerdere richtingberekening

    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.rot_to_player = 0

    def locate_player(self):
        # Bereken richting naar de speler in graden
        dx, dy = abs(self.x - self.game.player.x), abs(self.y - self.game.player.y)
        if dx == 0:
            self.rot_to_player = 90
        else:
            self.rot_to_player = math.atan(dy / dx) * 360 / (2 * math.pi)
        if self.x - self.game.player.x > 0:
            self.rot_to_player = 180 - self.rot
        if self.y - self.game.player.y < 0:
            self.rot_to_player *= -1

    def navigate(self, start, end):
        # Navigatie incl. berekening van kijkrichting
        dx, dy = abs(start[0] - end[0]), abs(start[1] - end[1])
        if dx == 0:
            self.rot = 90
        else:
            self.rot = math.atan(dy / dx) * 360 / (2 * math.pi)
        if start[0] - end[0] > 0:
            self.rot = 180 - self.rot
        if start[1] - end[1] < 0:
            self.rot *= -1

    def drawfront(self):
        # Teken een punt aan de voorkant van de guard als visuele indicatie
        self.front_point = self.rect.center + vec(TILESIZE, 0).rotate(-self.rot)
        self.front_point += self.game.camera.camera.topleft
        pg.draw.circle(self.game.screen, ZWART, self.front_point, 3)

    def update(self):
        # Navigatie en rotatie verwerken, positie updaten
        if not self.bot_at_checkpoint():
            self.navigate([self.pos[0] / TILESIZE, self.pos[1] / TILESIZE], self.next_pos)
        else:
            self.vel = vec(0, 0)
            self.pos = vec(self.next_pos[0], self.next_pos[1]) * TILESIZE
            self.x, self.y = self.pos
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.set_next_target()

        self.vel = vec(GUARD_SNELHEID, 0).rotate(-self.rot)
        self.pos += self.vel * self.game.dt
        self.x, self.y = round(self.pos[0]), round(self.pos[1])
        self.rect.x, self.rect.y = self.pos

class Guard(Guard1):
    # Guard met gezichtsveld en AI-fases zoals "patrol", "chase", "retreat"

    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        self.fases = ["patrol", "chase", "retreat"]
        self.fase = self.fases[0]  # Start in patrol modus
        self.vBREEDTE = VIZIE_BREEDTE  # Gezichtsveld breedte (graden)
        self.vdist = VIEW_DIST        # Zichtafstand in pixels

    def drawvieuwfield(self):
        # Visualisatie van wat de guard "ziet" als een zichtkegel
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        mid_angle_rad = math.radians(-self.rot)
        half_angle = math.radians(self.vBREEDTE)
        num_points = 30
        points = [center]

        for i in range(num_points + 1):
            angle = mid_angle_rad - half_angle + (2 * half_angle) * (i / num_points)
            point = center + vec(self.vdist, 0).rotate_rad(angle)
            points.append(point)

        pg.draw.polygon(self.game.screen, ZWART, points)

class Trap(Entity):
    def update(self):
        pass  # Mogelijkheid voor val/logica

class Item(Entity):
    def update(self):
        pass  # Kan gebruikt worden voor pickup-objecten