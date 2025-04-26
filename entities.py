import pygame as pg
import math
from GameSettings import *

vec = pg.math.Vector2

class Entity:
    def __init__(self, game, x, y, image_path=None, color=None):
        self.game = game
        self.pos = vec(x, y) * TILESIZE
        self.image = pg.Surface((TILESIZE, TILESIZE))
        if image_path:
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        elif color:
            self.image.fill(color)
        else:
            self.image.fill(WIT)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        self.rect.topleft = self.pos

class Wall(Entity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, color=GROEN)

class Trap(Entity):
    def update(self):
        pass

class Item(Entity):
    def update(self):
        pass

class Player(Entity):
    def __init__(self, game, x, y, kleur):
        super().__init__(game, x, y, color=kleur)
        self.vel = vec(0, 0)
        self.speed = SPELER_SNELHEID

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()

        if keys[pg.K_ESCAPE]:
            pg.quit()
            exit()
        if keys[pg.K_q] or keys[pg.K_LEFT]:
            self.vel.x = -self.speed
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vel.x = self.speed
        if keys[pg.K_z] or keys[pg.K_UP]:
            self.vel.y = -self.speed
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vel.y = self.speed

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= math.sqrt(2) / 2

    def collide_with_walls(self, direction):
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                if direction == 'x':
                    if self.vel.x > 0:
                        self.pos.x = wall.rect.left - self.rect.width
                    if self.vel.x < 0:
                        self.pos.x = wall.rect.right
                    self.vel.x = 0
                    self.rect.x = self.pos.x
                if direction == 'y':
                    if self.vel.y > 0:
                        self.pos.y = wall.rect.top - self.rect.height
                    if self.vel.y < 0:
                        self.pos.y = wall.rect.bottom
                    self.vel.y = 0
                    self.rect.y = self.pos.y

    def update(self):
        self.get_keys()
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        for entity in self.game.entities:
            if isinstance(entity, Guard) and self.rect.colliderect(entity.rect):
                self.game.playing = False
                self.game.gameover = True

class BaseGuard(Entity):
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.rot = 0
        self.target = vec(self.route[1]) * TILESIZE
        self.speed = GUARD_SNELHEID
        self.vel = vec(0, 0)

    def navigate(self, start, end):
        direction = vec(end) - vec(start)
        if direction.length() != 0:
            self.target_rot = direction.angle_to(vec(1, 0))
            return direction.normalize()
        return vec(0, 0)

    def at_checkpoint(self):
        return self.pos.distance_to(self.target) < 4

    def update(self):
        if not self.at_checkpoint():
            self.vel = self.navigate(self.pos, self.target) * self.speed
            self.pos += self.vel * self.game.dt
        else:
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

        self.rect.topleft = self.pos

class Guard(BaseGuard):
    def __init__(self, game, x, y, route):
        super().__init__(game, x, y, route)
        self.state = "patrol"
        self.last_seen_time = 0
        self.view_angle = VIZIE_BREEDTE
        self.view_dist = VIEW_DIST
        self.search_time = SEARCH_TIME
        self.view_resolution = RESOLUTIE
        self.target_rot = 0
        self.rotate_speed = 180
        self.last_seen_pos = None

    def detect_player(self):
        player_pos = vec(self.game.player.rect.center)
        direction = player_pos - vec(self.rect.center)

        if direction.length() > self.view_dist:
            return False

        facing = vec(1, 0).rotate(-self.rot)  # Gebruik visuele rotatie ipv velocity
        angle = facing.angle_to(direction)

        if abs(angle) < self.view_angle:
            return self.line_of_sight_clear(vec(self.rect.center), player_pos)
        return False

    def line_of_sight_clear(self, start, end):
        delta = end - start
        steps = int(delta.length() // 4)
        for i in range(1, steps + 1):
            point = start + delta * (i / steps)
            rect = pg.Rect(point.x, point.y, 2, 2)
            for wall in self.game.walls:
                if wall.rect.colliderect(rect):
                    return False
        return True

    def update(self):
        rot_diff = (self.target_rot - self.rot) % 360
        if rot_diff > 180:
            rot_diff -= 360
        rotation_step = self.rotate_speed * self.game.dt
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360

        if self.detect_player():
            self.state = "chase"
            self.last_seen_pos = vec(self.game.player.rect.center)
            self.last_seen_time = pg.time.get_ticks()
            self.alert_nearby_guards()

        current_time = pg.time.get_ticks()

        if self.state == "patrol":
            super().update()

        elif self.state == "chase":
            self.alert_nearby_guards()
            if self.last_seen_pos:
                direction_to_last_seen = self.last_seen_pos - vec(self.rect.center)
                if direction_to_last_seen.length() < 4:
                    self.state = "search"
                    self.search_start_time = current_time
                else:
                    self.target_rot = direction_to_last_seen.angle_to(vec(1, 0))
                    move_direction = direction_to_last_seen.normalize()
                    self.pos += move_direction * GUARD_SNELHEID_CHASE * self.game.dt
                    self.rect.topleft = self.pos

        elif self.state == "search":
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"
            self.target_rot += 60 * self.game.dt  # Roteer langzaam tijdens zoekmodus

    def drawvieuwfield(self):
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        points = [center]

        for i in range(self.view_resolution + 1):
            angle = (-self.view_angle + (2 * self.view_angle) * (i / self.view_resolution))
            point = center + vec(self.view_dist, 0).rotate(-(self.rot + angle))
            points.append(point)

        pg.draw.polygon(self.game.screen, LICHTROOD if self.state == "chase" else ZWART, points, 2)

    def alert_nearby_guards(self):
        for entity in self.game.entities:
            if isinstance(entity, Guard) and entity != self:
                distance = self.pos.distance_to(entity.pos)
                if distance < ALERT_DISTANCE and entity.state != "chase":
                    entity.state = "chase"
                    entity.last_seen_pos = vec(self.last_seen_pos)
                    entity.last_seen_time = pg.time.get_ticks()
