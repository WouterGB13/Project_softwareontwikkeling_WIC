# --- IMPORTS ---
import pygame as pg
import math
from GameSettings import *  # Instellingen zoals kleuren, snelheden, tilegrootte, etc.

# Vector2 voor posities en richtingen
vec = pg.math.Vector2


# --- BASIS ENTITY KLASSE ---
class Entity:
    """Basisklasse voor alle objecten in het spel (walls, speler, guards)."""

    def __init__(self, game, pos, image_path=None, color=None):
        self.game = game
        self.pos = vec(pos) * TILESIZE  # omzetten naar pixels
        self.image = pg.Surface((TILESIZE, TILESIZE))  # standaard witte tile

        # Als er een afbeelding is opgegeven, laad deze
        if image_path:
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        # Of gebruik kleur
        elif color:
            self.image.fill(color)
        else:
            self.image.fill(WIT)  # fallback kleur

        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        """Synchroniseert de rect met de positie."""
        self.rect.topleft = self.pos


# --- SPECIFIEKE ENTITEITEN ---
class Wall(Entity):
    """Muur die botsingen blokkeert."""
    def __init__(self, game, pos):
        super().__init__(game, pos, color=GROEN)


class Trap(Entity):
    """Val die later kan worden uitgebreid."""
    pass


class Item(Entity):
    """Pickup objecten (bijvoorbeeld sleutels)."""
    pass


# --- SPELER ---
class Player(Entity):
    """Bestuurbare speler."""

    def __init__(self, game, pos, color):
        super().__init__(game, pos, color=color)
        self.vel = vec(0, 0)
        self.speed = SPELER_SNELHEID

    def get_keys(self):
        """Check ingedrukte toetsen en pas snelheid aan."""
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()

        # Links/rechts
        if keys[pg.K_q] or keys[pg.K_LEFT]:
            self.vel.x = -self.speed
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vel.x = self.speed
        # Omhoog/omlaag
        if keys[pg.K_z] or keys[pg.K_UP]:
            self.vel.y = -self.speed
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vel.y = self.speed

        # Bij diagonale beweging snelheid corrigeren
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= math.sqrt(2) / 2

    def collide_with_walls(self, direction):
        """Voorkomt dat speler door muren beweegt."""
        for wall in self.game.entities:
            if isinstance(wall, Wall) and self.rect.colliderect(wall.rect):
                if direction == 'x':
                    if self.vel.x > 0:
                        self.pos.x = wall.rect.left - self.rect.width
                    if self.vel.x < 0:
                        self.pos.x = wall.rect.right
                    self.vel.x = 0
                    self.rect.x = self.pos.x
                elif direction == 'y':
                    if self.vel.y > 0:
                        self.pos.y = wall.rect.top - self.rect.height
                    if self.vel.y < 0:
                        self.pos.y = wall.rect.bottom
                    self.vel.y = 0
                    self.rect.y = self.pos.y

    def detect_guard(self):
        """Detecteer als speler zichtbaar is voor een guard."""
        for entity in self.game.entities:
            if isinstance(entity, Guard):
                if entity.detect_player():
                    entity.state = "chase"
                    entity.last_seen_pos = vec(self.rect.center)

    def update(self):
        """Update speler beweging en interactie."""
        self.get_keys()

        # Eerst bewegen op de x-as
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')

        # Dan bewegen op de y-as
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        self.detect_guard()


# --- BASIS GUARD ---
class BaseGuard(Entity):
    """Basisguard die simpel patrouilleert."""

    def __init__(self, game, pos, route):
        super().__init__(game, pos, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.speed = GUARD_SNELHEID
        self.target = vec(self.route[1]) * TILESIZE  # Eerste doel
        self.target_rot = 0

    def navigate(self, start, end):
        """Bereken genormaliseerde richting naar target."""
        direction = vec(end) - vec(start)
        if direction.length() != 0:
            return direction.normalize()
        return vec(0, 0)

    def at_checkpoint(self):
        """Check of guard bij volgende checkpoint is."""
        return self.pos.distance_to(self.target) < 4

    def patrol(self):
        """Patrouilleer naar volgende checkpoint."""
        if not self.at_checkpoint():
            move_dir = self.navigate(self.pos, self.target)
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
            self.pos += move_dir * self.speed * self.game.dt
        else:
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE
        self.rect.topleft = self.pos


# --- GUARD MET DETECTIE ---
class Guard(BaseGuard):
    """Guard die kan patrouilleren, jagen en zoeken."""

    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.state = "patrol"
        self.last_seen_pos = None
        self.last_seen_time = 0

        # Zichtinstellingen
        self.view_angle_default = VISIE_BREEDTE
        self.view_dist_default = VIEW_DIST
        self.view_resolution = RESOLUTIE
        self.view_angle_chase = 30  # kleinere hoek bij jagen
        self.view_dist_chase = self.view_dist_default * 1.5

        self.view_angle = self.view_angle_default
        self.view_dist = self.view_dist_default

        self.search_time = SEARCH_TIME_MS
        self.rot = 0
        self.rotate_speed = ROTATE_SPEED
        self.vel = vec(0, 0)

    def update(self):
        """Update gedrag afhankelijk van de huidige state."""
        current_time = pg.time.get_ticks()

        if self.detect_player():
            if self.state != "chase":
                self.state = "chase"
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.alert_nearby_guards()

        # Rotatie soepel bijwerken
        rot_diff = (self.target_rot - self.rot) % 360
        if rot_diff > 180:
            rot_diff -= 360

        rotation_step = self.rotate_speed * self.game.dt
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360

        # Gedrag uitvoeren afhankelijk van state
        if self.state == "patrol":
            self.patrol_behavior()
        elif self.state == "chase":
            self.chase_behavior(current_time)
        elif self.state == "search":
            self.search_behavior(current_time)

    def patrol_behavior(self):
        """Normale patrouille gedrag."""
        move_dir = self.navigate(self.pos, self.target)
        if move_dir.length() > 0:
            self.target_rot = move_dir.angle_to(vec(1, 0))
            self.vel = move_dir * self.speed
            self.move_and_collide()

        if self.at_checkpoint():
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

    def chase_behavior(self, current_time):
        """Gedrag tijdens achtervolgen van speler."""
        if self.detect_player():
            self.last_seen_pos = vec(self.game.player.rect.center)
            self.last_seen_time = current_time

        self.alert_nearby_guards()

        if self.last_seen_pos:
            to_target = self.last_seen_pos - vec(self.rect.center)
            if to_target.length() > 0:
                move_dir = to_target.normalize()
                self.vel = move_dir * GUARD_SNELHEID_CHASE
                self.target_rot = move_dir.angle_to(vec(1, 0))
                self.move_and_collide()

            if to_target.length() < 4:
                self.state = "search"
                self.search_start_time = current_time

    def search_behavior(self, current_time):
        """Zoekgedrag na kwijt raken van speler."""
        self.vel = vec(0, 0)
        self.target_rot += 60 * self.game.dt
        if current_time - self.search_start_time > self.search_time:
            self.state = "patrol"

    def detect_player(self):
        """Check of speler zichtbaar is."""
        player = self.game.player
        player_points = [
            vec(player.rect.topleft),
            vec(player.rect.topright),
            vec(player.rect.bottomleft),
            vec(player.rect.bottomright),
            vec(player.rect.center)
        ]

        for point in player_points:
            direction = point - vec(self.rect.center)
            distance = direction.length()

            if distance > self.view_dist:
                continue

            facing = vec(1, 0).rotate(-self.rot)
            angle = facing.angle_to(direction)

            if abs(angle) > self.view_angle:
                continue

            if self.line_of_sight_clear(vec(self.rect.center), point):
                return True

        return False

    def line_of_sight_clear(self, start, end):
        """Check of zichtlijn tussen twee punten niet geblokkeerd is door een muur."""
        delta = end - start
        steps = int(delta.length() // 4)
        for i in range(1, steps + 1):
            point = start + delta * (i / steps)
            point_rect = pg.Rect(point.x, point.y, 2, 2)
            for wall in self.game.entities:
                if isinstance(wall, Wall) and wall.rect.colliderect(point_rect):
                    return False
        return True

    def alert_nearby_guards(self):
        """Waarschuw guards binnen bereik tijdens achtervolging."""
        for entity in self.game.entities:
            if isinstance(entity, Guard) and entity != self:
                if self.pos.distance_to(entity.pos) < ALERT_DISTANCE:
                    if self.state == "chase" and entity.state != "chase":
                        entity.state = "chase"
                        entity.last_seen_pos = vec(self.last_seen_pos)

    def move_and_collide(self):
        """Beweeg de guard en behandel botsingen."""
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')

        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

    def collide_with_walls(self, direction):
        """Voorkom dat guards door muren bewegen."""
        for wall in self.game.entities:
            if isinstance(wall, Wall) and self.rect.colliderect(wall.rect):
                if direction == 'x':
                    if self.vel.x > 0:
                        self.pos.x = wall.rect.left - self.rect.width
                    elif self.vel.x < 0:
                        self.pos.x = wall.rect.right
                    self.vel.x = 0
                    self.rect.x = self.pos.x
                elif direction == 'y':
                    if self.vel.y > 0:
                        self.pos.y = wall.rect.top - self.rect.height
                    elif self.vel.y < 0:
                        self.pos.y = wall.rect.bottom
                    self.vel.y = 0
                    self.rect.y = self.pos.y

    def draw_view_field(self):
        """Teken het zichtveld van de guard."""
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        points = [center]

        for i in range(self.view_resolution + 1):
            angle = (-self.view_angle + 2 * self.view_angle * (i / self.view_resolution))
            point = center + vec(self.view_dist, 0).rotate(-(self.rot + angle))
            points.append(point)

        kleur = LICHTROOD if self.state == "chase" else ZWART
        pg.draw.polygon(self.game.screen, kleur, points, 2)