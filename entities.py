import pygame as pg
import math
from GameSettings import *

vec = pg.math.Vector2

class Entity:
    def __init__(self, game, pos, image_path=None, color=None):
        self.game = game
        self.pos = vec(pos) * TILESIZE
        self.image = pg.Surface((TILESIZE, TILESIZE))
        if image_path: #image file
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        elif color: #meegegeven kleur
            self.image.fill(color)
        else: #standaard
            self.image.fill(WIT)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        self.rect.topleft = self.pos

class Wall(Entity):
    def __init__(self, game, pos):
        super().__init__(game, pos, color=GROEN)

class Trap(Entity):
    pass

class Item(Entity):
    pass

class Player(Entity):
    def __init__(self, game, pos, color):
        super().__init__(game, pos, color=color)
        self.vel = vec(0, 0)
        self.speed = SPELER_SNELHEID

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
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

    def detect_guard(self):
        for entity in self.game.entities:
            if isinstance(entity, Guard):
                if entity.detect_player():
                    entity.state = "chase"
                    entity.last_seen_pos = vec(self.rect.center) #geef eigen positie door naar alle guards die weten waar player is

    def update(self):
        self.get_keys()

        # Eerst X-beweging
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')

        # Dan Y-beweging
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        self.detect_guard()

class BaseGuard(Entity): #Ik zou kiezen tussen of de historiek laten of met branches werken en alles samen voegen. Deze extra class doet niks
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
        return self.pos.distance_to(self.target) < 0.5

    def patrol(self):
        if not self.at_checkpoint():
            move_dir = self.navigate(self.pos, self.target)
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
            self.pos += move_dir * self.speed * self.game.dt
        else:
            self.pos = self.target
            self.checkpoint = (self.checkpoint + 1) % len(self.route)
            self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE
        self.rect.topleft = self.pos

class Guard(BaseGuard):
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.state = "patrol"
        self.last_seen_pos = None
        self.last_seen_time = 0
        
        # Vision instellingen vanuit GameSettings
        self.view_angle_default = VISIE_BREEDTE
        self.view_dist_default = VIEW_DIST
        self.view_resolution = RESOLUTIE
        
        # Tijdens chase: smallere blik maar verder kijken
        self.view_angle_chase = 30
        self.view_dist_chase = self.view_dist_default * 1.5
        
        # Startwaarden
        self.view_angle = self.view_angle_default
        self.view_dist = self.view_dist_default
        
        self.search_time = SEARCH_TIME_MS
        self.rot = 0
        self.rotate_speed = ROTATE_SPEED
        self.vel = vec(0, 0)

    def update(self):
        current_time = pg.time.get_ticks()
        

        # ALTIJD detectie checken, maakt niet uit in welke state
        if self.detect_player():
            if self.state != "chase":
                self.state = "chase"
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.alert_nearby_guards()

        # Smooth rotation (blijft gewoon hetzelfde)
        rot_diff = (self.target_rot - self.rot) % 360
        if rot_diff > 180:
            rot_diff -= 360
        rotation_step = self.rotate_speed * self.game.dt
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360

        # Gedrag gebaseerd op state
        if self.state == "patrol":
            move_dir = self.navigate(self.pos, self.target)
            self.view_angle = self.view_angle_default
            self.view_dist = self.view_dist_default
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
                self.vel = move_dir * self.speed
                self.move_and_collide()

            if self.at_checkpoint():
                self.checkpoint = (self.checkpoint + 1) % len(self.route)
                self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

        elif self.state == "chase" or self.state == "chase_help":
            if self.detect_player():
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.view_angle = self.view_angle_chase
                self.view_dist = self.view_dist_chase

            # Synchroniseer live tijdens achtervolging
            if self.state == "chase":
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
            self.target_rot += 60 * self.game.dt  # rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"

    def detect_player(self):
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
                continue  # te ver weg

            facing = vec(1, 0).rotate(-self.rot)
            angle = facing.angle_to(direction)

            if abs(angle) > self.view_angle:
                continue  # buiten zichtveld

            if self.line_of_sight_clear(vec(self.rect.center), point):
                return True  # speler gedetecteerd!

        return False  # geen enkele hoek voldeed

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
                            entity.state = "chase_help"
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


class Domme_Guard(Guard): #gegenereerd door een '0' vooraan het pad
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.retreat_path = []

    def checkretreat(self):
        if len(self.retreat_path) != 0:
            return True
        return False
    
    def update(self):
        current_time = pg.time.get_ticks()
        #print(self.pos)

        # ALTIJD detectie checken, maakt niet uit in welke state
        if self.detect_player():
            if self.state != "chase":
                self.state = "chase"
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.alert_nearby_guards()

        # Smooth rotation (blijft gewoon hetzelfde)
        rot_diff = (self.target_rot - self.rot) % 360
        if rot_diff > 180:
            rot_diff -= 360
        rotation_step = self.rotate_speed * self.game.dt
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360

        # Gedrag gebaseerd op state
        if self.state == "patrol":
            if self.checkretreat() == True:
                self.next_cp = self.target
                self.target = self.retreat_path[-1]
            move_dir = self.navigate(self.pos, self.target)
            #print(self.target)
            self.view_angle = self.view_angle_default
            self.view_dist = self.view_dist_default
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
                self.vel = move_dir * self.speed
                self.move_and_collide()

            if self.at_checkpoint():
                self.checkpoint = (self.checkpoint + 1) % len(self.route)
                self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE
                if len(self.retreat_path) != 0:
                    self.retreat_path.pop(-1)
                    if len(self.retreat_path) >= 1: #anders een error "list index out of range"
                        self.target = self.retreat_path[-1]
                    else: 
                        self.target = self.next_cp #resume origineel pad

        elif self.state == "chase" or self.state == "chase_help":
            if self.detect_player():
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.view_angle = self.view_angle_chase
                self.view_dist = self.view_dist_chase

            
            self.retreat_path.append(self.pos.copy())
            print(self.retreat_path)

            # Synchroniseer live tijdens achtervolging
            if self.state == "chase":
                self.alert_nearby_guards()

            if self.last_seen_pos: #if vector? hoe werkt dit?
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
            self.target_rot += 60 * self.game.dt  # rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"

class Slimme_Guard(Guard): #gegenereerd door een '1' vooraan het pad; NOG NIET AF
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.image.fill(PAARS)

    def determine_fastes_route(self): #geeft een lijst terug met punten voor de snelste route op basis van de laatst geziene positie (vooral voor chase-hulp, de gewone chase kunnen een versimpelde versie volgen)
        #stap 1: check of we de speler niet volledig kunnen zien (laatste locatie: vul hitbox aan) => schakel over op rechtstreekse achtervolging
        #stap 2: zo niet, sla de muren op die we kunnen zien (collision bij het kijken): we hebben de coordinaten nodig
        #stap 3: Hou rekening met de breedte van onze hitbox, wijk vervolgens de hoek naar de speler beetje bij beetje af tot je een pad vindt om naast de muur te geraken
        #stap 4: spawn denkbeeldig op die locatie en blijf vorige stappen opnieuw uitvoeren tot we bij de speler zijn.
        #stap 5: ga terug naar begin locatie en pak nu de andere hoek zodat we langs de andere kant rond de muren lopen (max 180° verschil)
        #stap 6: herhaal weeral tot bij de speler
        #stap 7: bekijk de afstanden afgelegd en pak de minst lange route

        muren_in_de_weg = []
        center = self.last_seen_pos
        player_points = [ #MERK OP: als we later de playersize onafhankelijk maken van de TILESIZE dan zal dit hier ook moeten verandert worden. Momenteel zijn hier gewoon geen aparte variabelen voor.
            vec(center) + vec(-TILESIZE, -TILESIZE), #linksboven
            vec(center) + vec(TILESIZE, -TILESIZE), #rechtsboven
            vec(center),
            vec(center) + vec(-TILESIZE, TILESIZE), #linksonder
            vec(center) + vec(TILESIZE, TILESIZE), #rechtsboven
        ]

        vrij_zicht = True
        for point in player_points:
            if not self.line_of_sight_clear(vec(self.rect.center), point) == True: #pas op, kan ook een muur returnen (nieuwe def)
                vrij_zicht = False
                muren_in_de_weg.append(self.line_of_sight_clear(vec(self.rect.center), point))

        to_target = self.last_seen_pos - vec(self.rect.center)
        if vrij_zicht:
            #achtervolg de speler direct: probeer misschien code over te nemen uit super()? lijn 197?
            if to_target.length() > 0:
                    move_dir = to_target.normalize()
                    self.vel = move_dir * GUARD_SNELHEID_CHASE
                    self.target_rot = move_dir.angle_to(vec(1, 0))
                    self.move_and_collide()

            if to_target.length() < 4:
                self.state = "search"
                self.search_start_time = pg.time.get_ticks()
            #deze code wordt waarsch nog wat aangepast
            pass

        else: #we hebben geen vrij zicht op de laatst locatie van de speler
            pass

    def line_of_sight_clear(self, start, end):
        delta = end - start
        steps = int(delta.length() // 4)  # elke 4 pixels een check
        for i in range(1, steps + 1):
            point = start + delta * (i / steps)
            point_rect = pg.Rect(point.x, point.y, 2, 2)
            for wall in self.game.entities:
                if isinstance(wall, Wall) and wall.rect.colliderect(point_rect):
                    return wall
        return True