import pygame as pg
import math
from GameSettings import *
from pathfinding import *

vec = pg.math.Vector2

class Entity:
    def __init__(self, game, pos, image_path=None, color=None):
        self.game = game
        self.pos = vec(pos) * TILESIZE
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.color = color
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

class Exit:
    def __init__(self, game, pos):
        self.game = game
        self.x, self.y = pos
        self.image = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x * TILESIZE, self.y * TILESIZE)

    def update(self):
        pass  # geen beweging

    def draw(self, screen, camera):
        font = pg.font.SysFont(None, 20)
        text = font.render("EXIT", True, ROOD)
        screen_pos = camera.apply_rect(self.rect)
        text_rect = text.get_rect(center=screen_pos.center)
        screen.blit(text, text_rect)

class Trap(Entity):
    def __init__(self, game, pos):
        super().__init__(game, pos, color=DONKERGRIJS)
        self.activated = False
        self.cooldown_time = cooldown_time
        self.last_triggered = 0

    def trigger_trap(self):
        current_time = pg.time.get_ticks()
        if self.activated and current_time - self.last_triggered < self.cooldown_time:
            return  # Trap zit nog in cooldown

        # 1. Stun de speler
        self.game.player.stunned = True
        self.game.player.stun_start_time = current_time
        self.game.player.stun_duration = 2000  # 2 seconden

        # 2. Waarschuw guards in de buurt
        for entity in self.game.entities:
            if isinstance(entity, Guard):
                distance = self.pos.distance_to(entity.pos)
                if distance < ALERT_DISTANCE:
                    entity.state = "chase_help"
                    entity.last_seen_pos = vec(self.game.player.rect.center)

        # Cooldown instellen
        self.activated = True
        self.last_triggered = current_time

    def update(self):
        # Kijk of speler over de trap loopt
        if self.rect.colliderect(self.game.player.rect):
            self.trigger_trap()

        # Reset cooldown na verloop van tijd
        if self.activated and pg.time.get_ticks() - self.last_triggered >= self.cooldown_time:
            self.activated = False

class Score(Entity):
    def __init__(self, game, pos):
        super().__init__(game, pos, color=BLAUW)
        #self.active = True #als dit false wordt, verwijder uit entitylist

    def update(self):
        if self.rect.colliderect(self.game.player):
            self.game.score +=1
            self.game.entities.remove(self)      
        

class Energie(Entity):
    pass

class Stun(Entity):
    pass

class Caught(Entity):
    pass

class Bag(Entity):
    def __init__(self, game, pos):
        super().__init__(game, pos, color=BRUIN)
        self.content = 1
        self.cooldown = 0
        
    def update(self):
        if self.rect.colliderect(self.game.player):
            Score_text = pg.font.SysFont(None, 48).render("Press P to use", True, WIT)
            Score_rect = Score_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 80))
            self.game.screen.blit(Score_text,Score_rect)
            pg.display.flip()
            keys = pg.key.get_pressed()
            if self.cooldown != 0:
                self.cooldown -=1
            if keys[pg.K_p]:
                if self.content == 0 and self.cooldown == 0:
                    self.content = self.game.score
                    self.game.score = 0
                    self.cooldown = 20
                elif self.cooldown == 0:
                    self.game.score += self.content
                    self.content = 0
                    self.cooldown = 20
        return



class Item(Entity):
    pass

class Player(Entity):
    def __init__(self, game, pos, color):
        super().__init__(game, pos, color=color)
        self.vel = vec(0, 0)
        self.speed = SPELER_SNELHEID
        self.stunned = False
        self.stun_start_time = 0
        self.stun_duration = 0
        self.lives = MAX_LIVES

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

    # def detect_guard(self):
    #     for entity in self.game.entities:
    #         if isinstance(entity, Guard):
    #             if entity.detect_player():
    #                 entity.state = "chase"
    #                 entity.last_seen_pos = vec(self.rect.center) #geef eigen positie door naar alle guards die weten waar player is

    def update(self):
        self.get_keys()
        current_time = pg.time.get_ticks()
        if self.stunned:
            if current_time - self.stun_start_time < self.stun_duration:
                self.vel = vec(0, 0)
                return  # speler kan tijdelijk niks doen
            else:
                self.stunned = False

        # Eerst X-beweging
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')

        # Dan Y-beweging
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        #self.detect_guard()

class BaseGuard(Entity): #Ik zou kiezen tussen of de historiek laten of met branches werken en alles samen voegen. Deze extra class doet niks
    def __init__(self, game, pos, route):
        super().__init__(game, pos, color=ROOD)
        self.route = route
        self.checkpoint = 0
        self.speed = GUARD_SNELHEID
        try:
            self.target = vec(self.route[1]) * TILESIZE
        except IndexError:
            self.target = vec(self.route[0]) * TILESIZE
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

    def reset(self):
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
            self.target_rot += 20 * self.game.dt  # rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"

    def detect_player(self):
        player = self.game.player

        if self.hear_player():
            return True

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

            if self.line_of_sight_clear(vec(self.rect.center), point) == True:
                return True  # speler gedetecteerd!

        return False  # geen enkele hoek voldeed
    
    def hear_player(self):
        distance = (vec(self.game.player.rect.center) - vec(self.rect.center)).magnitude_squared()
        if distance == HEAR_DIST**2 or distance < HEAR_DIST**2:
            return True
        else:
            return False

    def line_of_sight_clear(self, start, end):
        #https://www.pygame.org/docs/ref/rect.html#pygame.Rect.clipline
        for wall in self.game.walls:
            clipline = wall.rect.clipline(start, end)
            if clipline:
                return wall  # geef het Wall object terug
        return True  # vrije zichtlijn

    

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

    def draw_view_field(self):
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        points = [center]
        for i in range(self.view_resolution + 1):
            angle = (-self.view_angle + 2 * self.view_angle * (i / self.view_resolution))
            point = center + vec(self.view_dist, 0).rotate(-(self.rot + angle))
            if ADAPTIVE_CONES:
                # self.close_walls = [] #idee voor efficientere code
                # for wall in self.game.walls:
                #     if (vec(wall.rect.center) - vec(self.rect.center)).magnitude_squared < (VIEW_DIST+2)*TILESIZE:
                #         self.close_walls.append(wall)
                punt = self.line_of_sight_clear(center, point)
                if punt != True: #volgende code komt vooral uit line_of_sight_clear():
                    point = punt                        

            points.append(point)
        kleur = LICHTROOD if self.state == "chase" else ZWART
        # for point in points: #laat deze code even staan: nodig voor debugging
        #     pg.draw.circle(self.game.screen, ROOD, point, 4)
        pg.draw.polygon(self.game.screen, kleur, points, 2)

class Domme_Guard(Guard): #gegenereerd door een '0' vooraan het pad IS AF, PROBLEEM MET RESUME ROUTE WORDT VEROORZAAKT DOOR ALGEMENE NAVIGATIECODE
    #DO NOT TOUCH ZONDER OVERLEGGEN

    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.retreat_path = []

    def checkretreat(self):
        if len(self.retreat_path) != 0:
            return True
        return False
    
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
            if self.checkretreat() == True:
                self.next_target = self.target.copy()
                self.current_checkpoint = (self.checkpoint)
                self.target = self.retreat_path[-1]
            move_dir = self.navigate(self.pos, self.target)
            self.view_angle = self.view_angle_default
            self.view_dist = self.view_dist_default
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))
                self.vel = move_dir * self.speed
                self.move_and_collide()

            if self.at_checkpoint():
                if len(self.retreat_path) != 0:
                    self.retreat_path.pop(-1)
                    if len(self.retreat_path) >= 1: #anders een error "list index out of range"
                        self.target = self.retreat_path[-1]
                    else: 
                        self.target = self.next_target #resume origineel pad
                        self.checkpoint = self.current_checkpoint - 1 # -1 want anders wordt checkpoint overgeslaan
                else:        
                    self.checkpoint = (self.checkpoint + 1) % len(self.route)
                    self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

        elif self.state == "chase" or self.state == "chase_help":
            if self.detect_player():
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.view_angle = self.view_angle_chase
                self.view_dist = self.view_dist_chase

            self.retreat_path.append(self.pos.copy())

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
            self.target_rot += 20 * self.game.dt  # rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"

class Slimme_Guard(Guard):
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)
        self.image.fill(PAARS)
        self.prev_pos = vec(self.pos)
        self.stuck_timer = 0

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
                pos_on_map = (int(self.rect.x/TILESIZE), int(self.rect.y/TILESIZE))
                player_pos_on_map = (int(self.game.player.rect.x/TILESIZE), int(self.game.player.rect.y/TILESIZE))
                a_star_path = simplefy_path(find_path(self.game, pos_on_map, player_pos_on_map))
                print(a_star_path)
                to_target = vec(a_star_path[1])*TILESIZE - vec(self.rect.center) +(TILESIZE/2, TILESIZE/2) #laatste term is omdat de map werkt met ander soort coordinaten
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
            self.target_rot += 20 * self.game.dt  # rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"
        
    def DEZE_SHIT_WERKT_NIET_STOP_MET_HET_TE_PROBEREN_FIXEN(self): #jawel laat het staan want ik heb de code nog nodig, doe gwn deze def toe
    # def update(self):
    #     current_time = pg.time.get_ticks()

    #     if self.detect_player():
    #         if self.state != "chase":
    #             self.state = "chase"
    #             self.last_seen_pos = vec(self.game.player.rect.center)
    #             self.last_seen_time = current_time
    #             self.alert_nearby_guards()

    #     # Rotatie zoals bij gewone guard
    #     rot_diff = (self.target_rot - self.rot) % 360
    #     if rot_diff > 180:
    #         rot_diff -= 360
    #     rotation_step = self.rotate_speed * self.game.dt
    #     self.rot += rotation_step if rot_diff > 0 else -rotation_step if abs(rot_diff) >= rotation_step else 0
    #     self.rot %= 360

    #     if self.state == "patrol":
    #         self.view_angle = self.view_angle_default
    #         self.view_dist = self.view_dist_default
    #         move_dir = self.navigate(self.pos, self.target)
    #         if move_dir.length() > 0:
    #             self.target_rot = move_dir.angle_to(vec(1, 0))
    #             self.vel = move_dir * self.speed
    #             self.move_and_collide()

    #         if self.at_checkpoint():
    #             self.checkpoint = (self.checkpoint + 1) % len(self.route)
    #             self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

    #     elif self.state in ["chase", "chase_help"]:
    #         self.view_angle = self.view_angle_chase
    #         self.view_dist = self.view_dist_chase

    #         if self.detect_player():
    #             self.last_seen_pos = vec(self.game.player.rect.center)
    #             self.last_seen_time = current_time
    #             if self.state == "chase":
    #                 self.alert_nearby_guards()

    #         time_since_seen = current_time - self.last_seen_time
    #         if time_since_seen > CHASE_TIMEOUT:
    #             self.state = "search"
    #             self.search_start_time = current_time
    #             self.can_signal = True
    #             self.stuck_timer = 0
    #             return

    #         to_target = self.move_and_dodge_wall()

    #         if to_target.length() > 0:
    #             move_dir = to_target.normalize()
    #             self.vel = move_dir * GUARD_SNELHEID_CHASE
    #             self.target_rot = move_dir.angle_to(vec(1, 0))
    #             self.move_and_collide()

    #             if self.pos.distance_to(self.prev_pos) < STUCK_DISTANCE_THRESHOLD:
    #                 self.stuck_timer += self.game.dt * 1000
    #             else:
    #                 self.stuck_timer = 0
    #             self.prev_pos = vec(self.pos)

    #             if self.stuck_timer > STUCK_TIME_LIMIT or to_target.length() < 4:
    #                 self.state = "search"
    #                 self.search_start_time = current_time
    #                 self.can_signal = True
    #                 self.stuck_timer = 0

    #     elif self.state == "search":
    #         self.vel = vec(0, 0)
    #         self.target_rot += 20 * self.game.dt
    #         if current_time - self.search_start_time > self.search_time:
    #             self.state = "patrol"

    # def move_and_dodge_wall(self):
    #     if not self.last_seen_pos:
    #         return vec(0, 0)

    #     start = vec(self.rect.center)
    #     end = self.last_seen_pos
    #     to_target = end - start

    #     if self.line_of_sight_clear(start, end):
    #         return to_target

    #     blocking_wall = self.line_of_sight_clear(start, end)
    #     if isinstance(blocking_wall, Wall):
    #         wall_center = vec(blocking_wall.rect.center)
    #         wall_size = vec(blocking_wall.rect.size)
    #         offsets = [
    #             vec(-1, -1), vec(1, -1),
    #             vec(-1, 1), vec(1, 1)
    #         ]

    #         closest_point = None
    #         min_distance = float('inf')

    #         for offset in offsets:
    #             corner = wall_center + (offset * wall_size / 2) + (offset * TILESIZE / 2)
    #             if self.line_of_sight_clear(start, corner):
    #                 dist = (corner - start).length_squared()
    #                 if dist < min_distance:
    #                     min_distance = dist
    #                     closest_point = corner

    #         if closest_point:
    #             return closest_point - start

    #     return to_target  # fallback
        pass
