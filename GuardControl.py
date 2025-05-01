import pygame as pg
import math
from GameSettings import *
from entities import Entity, Wall

vec = pg.math.Vector2


class BaseGuard(Entity):
    def __init__(self, game, pos, route):
        super().__init__(game, pos, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.speed = GUARD_SNELHEID
        self.target = vec(self.route[1]) * TILESIZE
        self.target_rot = 0

    def navigate(self, start, end):
        direction = vec(end) - vec(start)
        if direction.length() != 0:
            return direction.normalize()
        return vec(0, 0)

    def at_checkpoint(self):
        return self.pos.distance_to(self.target) < 4

    def patrol(self):
        if not self.at_checkpoint():
            move_dir = self.navigate(self.pos, self.target)
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
            self.pos += move_dir * self.speed * self.game.dt
        else:
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE
        self.rect.topleft = self.pos

class Guard(BaseGuard):
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.state = "patrol"
        self.last_seen_pos = None
        self.last_seen_time = 0
        self.view_angle = VISIE_BREEDTE
        self.view_dist = VIEW_DIST
        self.search_time = SEARCH_TIME_MS
        self.view_resolution = RESOLUTIE
        self.rot = 0
        self.rotate_speed = ROTATE_SPEED
        self.vel = vec(0, 0)

    def update(self):
        current_time = pg.time.get_ticks()

        # Smooth rotation
        rot_diff = (self.target_rot - self.rot) % 360
        if rot_diff > 180:
            rot_diff -= 360
        rotation_step = self.rotate_speed * self.game.dt
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360

        # Gedrag op basis van state
        if self.state == "patrol":
            move_dir = self.navigate(self.pos, self.target)
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
                self.vel = move_dir * self.speed
                self.move_and_collide()

            if self.at_checkpoint():
                self.checkpoint = (self.checkpoint + 1) % len(self.route)
                self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

            if self.detect_player():
                self.state = "chase"
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.alert_nearby_guards()

        elif self.state == "chase":
            if self.detect_player():
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time

            # Synchroniseer live tijdens achtervolging
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

        elif self.state == "search":
            self.vel = vec(0, 0)
            self.target_rot += 60 * self.game.dt  # Rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"

    def detect_player(self):
        player_pos = vec(self.game.player.rect.center)
        direction = player_pos - vec(self.rect.center)
        if direction.length() > self.view_dist:
            return False
        facing = vec(1, 0).rotate(-self.rot)
        angle = facing.angle_to(direction)
        if abs(angle) < self.view_angle:
            return self.line_of_sight_clear(vec(self.rect.center), player_pos)
        return False

    def line_of_sight_clear(self, start, end):
        delta = end - start
        steps = int(delta.length() // 4)  # elke 4 pixels een check
        for i in range(1, steps + 1):
            point = start + delta * (i / steps)
            point_rect = pg.Rect(point.x, point.y, 2, 2)
            for wall in self.game.entities:
                if isinstance(wall, Wall) and wall.rect.colliderect(point_rect):
                    return False
        return True

    def alert_nearby_guards(self):
        for entity in self.game.entities:
            if isinstance(entity, Guard) and entity != self:
                distance = self.pos.distance_to(entity.pos)
                if distance < ALERT_DISTANCE:
                    if self.state == "chase":
                        # Deze guard zit al in chase modus, dus push informatie door
                        if entity.state != "chase":
                            entity.state = "chase"
                            entity.last_seen_pos = vec(self.last_seen_pos)
                        else:
                            # Als beide in chase zijn, synchroniseer de laatst geziene positie
                            entity.last_seen_pos = vec(self.last_seen_pos)


    def move_and_collide(self):
        # Eerst X
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')

        # Dan Y
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

    def collide_with_walls(self, direction):
        for wall in self.game.entities:
            if isinstance(wall, Wall) and self.rect.colliderect(wall.rect):
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

    def draw_view_field(self):
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        points = [center]
        for i in range(self.view_resolution + 1):
            angle = (-self.view_angle + 2 * self.view_angle * (i / self.view_resolution))
            point = center + vec(self.view_dist, 0).rotate(-(self.rot + angle))
            points.append(point)
        kleur = LICHTROOD if self.state == "chase" else ZWART
        pg.draw.polygon(self.game.screen, kleur, points, 2)