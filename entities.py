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

class Guard0(Entity): #1e versie van guards
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.speed = GUARD_SNELHEID
        self.set_next_target()

    def set_next_target(self):
        self.current_route_pos = self.route[self.checkpoint]
        next_index = (self.checkpoint + 1) % len(self.route)
        self.next_pos = self.route[next_index]

    def navigate(self, start, end):
        start_px = vec(start) * TILESIZE
        end_px = vec(end) * TILESIZE
        delta = end_px - start_px
        distance = delta.length()

        if distance > 0:
            velocity = delta.normalize() * self.speed
            self.vx, self.vy = velocity.x, velocity.y
        else:
            self.vx = self.vy = 0

    def bot_at_checkpoint(self):
        target_px = vec(self.next_pos) * TILESIZE
        return target_px.distance_to(vec(self.x, self.y)) <= 3

    def update(self):
        if not self.bot_at_checkpoint():
            self.navigate(self.current_route_pos, self.next_pos)
        else:
            self.vx = self.vy = 0
            self.x, self.y = vec(self.next_pos) * TILESIZE
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.set_next_target()

        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x, self.rect.y = self.x, self.y

class Guard1(Guard0):
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.rot_to_player = 0

    def locate_player(self):
        player_pos = vec(self.game.player.x, self.game.player.y)
        guard_pos = vec(self.x, self.y)
        delta = player_pos - guard_pos

        if delta.x == 0:
            self.rot_to_player = 90
        else:
            angle_rad = math.atan(abs(delta.y) / abs(delta.x))
            self.rot_to_player = math.degrees(angle_rad)

        if delta.x < 0:
            self.rot_to_player = 180 - self.rot_to_player
        if delta.y > 0:
            self.rot_to_player *= -1

    def navigate(self, start, end):
        delta = vec(end) - vec(start)
        if delta.x == 0:
            self.rot = 90
        else:
            angle_rad = math.atan(abs(delta.y) / abs(delta.x))
            self.rot = math.degrees(angle_rad)

        if delta.x < 0:
            self.rot = 180 - self.rot
        if delta.y > 0:
            self.rot *= -1

    def drawfront(self):
        offset = vec(TILESIZE, 0).rotate(-self.rot)
        self.front_point = self.rect.center + offset + self.game.camera.camera.topleft
        pg.draw.circle(self.game.screen, ZWART, self.front_point, 3)

    def update(self):
        if not self.bot_at_checkpoint():
            self.navigate(self.current_route_pos, self.next_pos)
        else:
            self.vel = vec(0, 0)
            self.pos = vec(self.next_pos) * TILESIZE
            self.x, self.y = self.pos
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.set_next_target()

        self.vel = vec(GUARD_SNELHEID, 0).rotate(-self.rot)
        self.pos += self.vel * self.game.dt
        self.x, self.y = round(self.pos.x), round(self.pos.y)
        self.rect.x, self.rect.y = self.pos

class Guard(Guard1):
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        self.fases = ["patrol", "chase", "retreat"]
        self.fase = "patrol"
        self.vBREEDTE = VIZIE_BREEDTE
        self.vdist = VIEW_DIST
        self.speeds = {
            "patrol": GUARD_SNELHEID,
            "chase": GUARD_SNELHEID * 2,
            "retreat": GUARD_SNELHEID
        }
        self.laatste_zichttijd = 0
        self.retreat_target = None

        self.search_start_time = 0
        self.search_duration = SEARCH_TIME  # 3 seconden zoeken
        self.searching = False


    def detecteert_speler(self):
        if self.heeft_zicht_op_speler():
            self.laatste_zichttijd = pg.time.get_ticks()
            self.last_known_player_pos = vec(self.game.player.rect.center)
            return True
        return False
    
    def heeft_zicht_op_speler(self):
        # Check visuele afstand en kijkhoek
        speler_pos = vec(self.game.player.rect.center)
        guard_pos = vec(self.rect.center)
        richting = speler_pos - guard_pos
        afstand = richting.length()

        if afstand > self.vdist:
            return False

        hoek_tov_front = richting.angle_to(vec(1, 0).rotate(-self.rot))
        if abs(hoek_tov_front) > self.vBREEDTE:
            return False

        return self.line_of_sight_clear(guard_pos, speler_pos)

    def line_of_sight_clear(self, start, end):
        delta = end - start
        steps = int(delta.length() // 4)
        for i in range(1, steps + 1):
            point = start + delta * (i / steps)
            point_rect = pg.Rect(point.x, point.y, 2, 2)  # klein vakje
            for wall in self.game.walls:
                if wall.rect.colliderect(point_rect):
                    return False
        return True


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


    def update(self):
        tijd_nu = pg.time.get_ticks()

        # ONGEACHT DE HUIDIGE FASE → detecteer speler live
        if self.detecteert_speler():
            self.fase = "chase"
        
        # Fase-afhandeling
        if self.fase == "patrol":
            super().update()

        elif self.fase == "chase":
            speler_pos = vec(self.game.player.rect.center)
            richting = speler_pos - self.pos
            if richting.length() > 0:
                self.vel = richting.normalize() * self.speeds["chase"]
                self.pos += self.vel * self.game.dt
                self.x, self.y = round(self.pos.x), round(self.pos.y)
                self.rect.x, self.rect.y = self.pos
                self.collide_with_walls()
            if tijd_nu - self.laatste_zichttijd > CHASE_TIME:
                self.fase = "search"
                self.searching = False  # reset

        elif self.fase == "search":
            self.search_behavior()

        elif self.fase == "retreat":
            retreat_vec = vec(self.retreat_target) * TILESIZE
            richting = retreat_vec - self.pos
            if richting.length() > 3:
                self.vel = richting.normalize() * self.speeds["retreat"]
                self.pos += self.vel * self.game.dt
                self.x, self.y = round(self.pos.x), round(self.pos.y)
                self.rect.x, self.rect.y = self.pos
                self.collide_with_walls()
            else:
                self.pos = retreat_vec
                self.x, self.y = self.pos
                self.rect.x, self.rect.y = self.pos
                self.fase = "patrol"

        # Richting bijwerken voor front-view rotatie
        if self.vel.length_squared() > 0:
            self.rot = self.vel.angle_to(vec(1, 0))


    def search_behavior(self):
        if not self.searching:
            # Net aangekomen op laatst gekende locatie
            richting = self.last_known_player_pos - self.pos
            if richting.length() > 3:
                self.vel = richting.normalize() * self.speeds["retreat"]
                self.pos += self.vel * self.game.dt
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
            tijd_nu = pg.time.get_ticks()
            tijd_verstreken = tijd_nu - self.search_start_time
            self.rot += ROT_SPEED * self.game.dt  # Langzaam ronddraaien

            if tijd_verstreken >= self.search_duration:
                self.fase = "retreat"
                self.searching = False
                self.bepaal_retreat_punt()


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

    def drawvieuwfield(self):
        if self.fase == "chase":
            kleur = LICHTROOD
        else:
            kleur = ZWART
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        mid_angle_rad = math.radians(-self.rot)
        half_angle = math.radians(self.vBREEDTE)
        points = [center]
        for i in range(31):
            angle = mid_angle_rad - half_angle + (2 * half_angle) * (i / 30)
            point = center + vec(self.vdist, 0).rotate_rad(angle)
            points.append(point)
        pg.draw.polygon(self.game.screen, kleur, points, 2)

class Trap(Entity):
    def update(self):
        pass  # Mogelijkheid voor val/logica

class Item(Entity):
    def update(self):
        pass  # Kan gebruikt worden voor pickup-objecten