import pygame as pg
import math
from GameSettings import *

vec = pg.math.Vector2

entitylijst = []

class Entity:
    # Basisklasse voor game entities

    def __init__(self, game, x, y, image_path=None, color=None):
        """
        Initialiseer een entity

        Args:
            game: Game object
            x: begin x-coordinaat (tile eenheid)
            y: begin y-coordinaat (tile eenheid)
            image_path: Pad naar het afbeeldingsbestand (optioneel).
            color: Vulkleur voor het oppervlak (optioneel).
        """
        self.game = game
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.pos = vec(self.x, self.y)  # Gebruik Vector2 voor positie

        self.image = pg.Surface((TILESIZE, TILESIZE))
        if image_path:
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))  # schaal afbeelding
        elif color:
            self.image.fill(color) # Vul met opgegeven kleur
        else:
            self.image.fill(WIT)  # Standaard kleur als geen afbeelding of kleur is opgegeven

        self.rect = self.image.get_rect(topleft=(self.x, self.y))  # Initialiseer rect met positie

    def update(self):
        # De status van de entity's bijwerken
        self.rect.topleft = (self.x, self.y)  # De positie van het rect bijwerken op basis van x, y

class Player(Entity):
    # the player character

    def __init__(self, game, x, y, kleur):
        # De speler initialiseren
        super().__init__(game, x, y, color=kleur)  # gebruiken Entity's init
        self.vx = 0
        self.vy = 0
        self.speed = SPELER_SNELHEID

    def get_keys(self):
        # Verwerk toetsenbordinvoer voor spelerbewegingen
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

        if self.vx != 0 and self.vy != 0:
            self.vy *= math.sqrt(2) / 2
            self.vx *= math.sqrt(2) / 2

    def object_collision(self):
        # Controleren op botsingen met muren
        collisionlist = []
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                collisionlist.append(wall)
        return collisionlist

    def collide_with_walls(self, direction):
        # Botsingen met muren afhandelen
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
        # Zorg dat alleen Player deze functie uitvoert
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

        # Game over check bij botsing met guard
        for entity in entitylijst:
            if isinstance(entity, Guard) and self.rect.colliderect(entity.rect):
                print("Speler gepakt door een guard! GAME OVER.")
                self.game.playing = False
                self.game.gameover = True

class Wall(Entity):
    # Muur in het spel
    def __init__(self, game, x, y):
        # De muur initialiseren
        super().__init__(game, x, y, color=GROEN)  # Use Entity's init

    def update(self):
        # De status van de muur bijwerken (doet momenteel niets)
        pass

class Guard0(Entity):
    # Basis bewakingsklasse met eenvoudig patrouillegedrag

    def __init__(self, game, x, y, route):
        # De bewaker initialiseren
        super().__init__(game, x, y, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.speed = GUARD_SNELHEID
        self.set_next_target()

    def set_next_target(self):
        # Stel het volgende patrouilledoel in
        self.currentpos = self.route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = self.route[(self.checkpoint + 1) % len(self.route)]
        self.next_pos = self.next_patrol_pos

    def navigate(self, start, end):
        # Snelheid berekenen om naar het doel te bewegen
        distance = math.hypot(end[0] * TILESIZE - start[0] * TILESIZE, end[1] * TILESIZE - start[1] * TILESIZE)
        if distance > 0:
            self.vx = self.speed * ((end[0] * TILESIZE - start[0] * TILESIZE) / distance)
            self.vy = self.speed * ((end[1] * TILESIZE - start[1] * TILESIZE) / distance)
        else:
            self.vx = 0
            self.vy = 0

    def bot_at_checkpoint(self):
        # Controleer of de bewaker het controlepunt heeft bereikt
        return (self.next_pos[0] * TILESIZE - 3 <= self.x <= self.next_pos[0] * TILESIZE + 3) and \
               (self.next_pos[1] * TILESIZE - 3 <= self.y <= self.next_pos[1] * TILESIZE + 3)

    def update(self):
        # Bijwerken van de bewaker's positie en controleren op botsingen
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
    ## Geavanceerde bewaker met rotatie en richtingsdetectie

    def __init__(self, game, x, y, route):
        # De geavanceerde bewaker initialiseren
        super().__init__(game, x, y, route)
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.rot_to_player = 0

    def locate_player(self):
        # Bereken de hoek naar de speler
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
        # Bereken de rotatie naar het doel
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
        # Teken een cirkel die de voorkant van de guard aangeeft
        self.front_point = self.rect.center + vec(TILESIZE, 0).rotate(-self.rot)
        self.front_point += self.game.camera.camera.topleft
        pg.draw.circle(self.game.screen, ZWART, self.front_point, 3)

    def update(self):
        # Update bewakingspositie en rotatie
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
    # Bewakingsklasse met gezichtsveld en statussyteem

    def __init__(self, game, x, y, route):
        # Initialiseer de bewaker met gezichtsveld
        super().__init__(game, x, y, route)
        self.fases = ["patrol", "chase", "retreat"]
        self.fase = self.fases[0]
        self.vBREEDTE = VIZIE_BREEDTE
        self.vdist = VIEW_DIST

    def drawvieuwfield(self):
        # Teken het gezichtsveld van de bewaker
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
        pass

class Item(Entity):
    def update(self):
        pass