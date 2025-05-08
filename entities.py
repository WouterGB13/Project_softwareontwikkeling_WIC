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

class Energie(Entity):
    pass

class Stunn(Entity):
    pass
class Caught(Entity):
    pass

class Bag(Entity):
    pass

class Backpack(Entity):
    pass

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

        self.first_load = True

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
        
        print(self.state)
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

        distance = (vec(player.rect.center) - vec(self.rect.center)).magnitude_squared()
        if distance == HEAR_DIST**2 or distance < HEAR_DIST**2:
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

    def line_of_sight_clear(self, start, end):
        #https://www.pygame.org/docs/ref/rect.html#pygame.Rect.clipline
        for wall in self.game.walls:
            clipline = wall.rect.clipline(start, end)
            if clipline:
                start, end = clipline
                return start
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

            #zie of er geen muren in de weg staan:
            # muur = self.line_of_sight_clear(center, point)
            # if muur != True: #volgende code komt vooral uit line_of_sight_clear():
            #     point = self.get_point_at_wall(center, point, muur, steps)
                #print(point)

            # if not self.first_load:
            #     punt = self.line_of_sight_clear(center, point)
            #     if punt != True: #volgende code komt vooral uit line_of_sight_clear():
            #         point = punt
            # else:
            #     self.first_load = False                            

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
                self.next_cp = self.target
                self.target = self.retreat_path[-1]
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

    def update(self):
        current_time = pg.time.get_ticks()
        # print(self.pos)

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
                #to_target = self.last_seen_pos - vec(self.rect.center)
                to_target = self.move_and_dogde_walls()
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

    def determine_fastes_route(self): #geeft een lijst terug met alle tiles voor de snelste route op basis van de laatst doorgegeven positie (vooral voor chase-hulp, de gewone chase kunnen een versimpelde versie volgen)
        #stap 1: check of we de speler niet volledig kunnen zien (laatste locatie: vul hitbox aan) => schakel over op rechtstreekse achtervolging
        #stap 2: zo niet, sla de muren op die we kunnen zien (collision bij het kijken): we hebben de coordinaten nodig
        #stap 3: Hou rekening met de breedte van onze hitbox, wijk vervolgens de hoek naar de speler beetje bij beetje af tot je een pad vindt om naast de muur te geraken
        #stap 4: spawn denkbeeldig op die locatie en blijf vorige stappen opnieuw uitvoeren tot we bij de speler zijn.
        #stap 5: ga terug naar begin locatie en pak nu de andere hoek zodat we langs de andere kant rond de muren lopen (max 180° verschil)
        #stap 6: herhaal weeral tot bij de speler
        #stap 7: bekijk de afstanden afgelegd en pak de minst lange route
        pass

    def move_and_dogde_walls(self):#buigt het pad naar de speler af wanneer die achter een muur staat om botsing te voorkomen door gewoon een nieuw doel te returnen
        #stap 1: check of we de speler niet volledig kunnen zien (laatste locatie: vul hitbox aan) => schakel over op rechtstreekse achtervolging
        #stap 2: zo niet, sla de muren op die we kunnen zien (collision bij het kijken): we hebben de coordinaten nodig
        #stap 3: Hou rekening met de breedte van onze hitbox, wijk vervolgens de hoek naar de speler beetje bij beetje af tot je een pad vindt om naast de muur te geraken
        #stap 4: volg pad
        vrije_zicht_punten = []
        center = self.last_seen_pos
        player_points = [ #MERK OP: als we later de playersize onafhankelijk maken van de TILESIZE dan zal dit hier ook moeten veranderd worden. Momenteel zijn hier gewoon geen aparte variabelen voor.
            vec(center) + vec(-TILESIZE, -TILESIZE), #linksboven
            vec(center) + vec(TILESIZE, -TILESIZE), #rechtsboven
            vec(center),
            vec(center) + vec(-TILESIZE, TILESIZE), #linksonder
            vec(center) + vec(TILESIZE, TILESIZE), #rechtsonder
        ]

        vrij_zicht = True
        for point in player_points:
            if not self.line_of_sight_clear(vec(self.rect.center), point) == True: #pas op, kan ook een muur returnen (nieuwe def)
                vrij_zicht = False
            else:
                vrije_zicht_punten.append(point)
                #muren_in_de_weg.append(self.line_of_sight_clear(vec(self.rect.center), point))

        to_target = self.last_seen_pos - vec(self.rect.center)
        if vrij_zicht:
           return to_target

        else: #we hebben geen vrij zicht op de laatst locatie van de speler
            #STAP 1: bepaal achter welke muur de spelercenter staat, pak de kant waarlangs we hem kunnen zien en meet hiervan de positie om exact langs de dichtbijzijnde kant van de muur te kunnen
            
            if self.line_of_sight_clear(vec(self.rect.center), vec(center)) != True:
                relevante_muur = self.line_of_sight_clear(vec(self.rect.center), vec(center))
            else:
                for point in player_points:
                    if not self.line_of_sight_clear(vec(self.rect.center), vec(point)) == True:
                        relevante_muur = self.line_of_sight_clear(vec(self.rect.center), point)

            breedte_muur_en_speler = TILESIZE/2 + TILESIZE/2 #NOTE: De eerste TILESIZE/2 staat voor de breedte van de muur, de tweede is die van de speler.
            #om links of rechts te bepalen kijken we naar de hoek tussen de vectoren van de centra:
            naar_muur = vec(relevante_muur.rect.center) - vec(self.rect.center)
            hoekverschil = to_target.angle_to(naar_muur) if abs(to_target.angle_to(naar_muur)) < 180 else (360 - abs(to_target.angle_to(naar_muur)))*to_target.angle_to(naar_muur)/abs(to_target.angle_to(naar_muur))
            #NOTE: angle_to() pakt de hoek tussen 2 vectoren zolang hij niet over het negatieve gedeelte van de x-as moet. Dus als de hoeken zich net wel langs de andere kant bevinden moeten we zien dat we dus toch gewoon de kleine hoek tussen hun 2 pakken (en behoud van teken).
            #Als hoekverschil nu positief is dan moet onze guard naar links, anders naar rechts (vanuit zijn ogen)
            richting = 'L' if hoekverschil > 0 else 'R'
            #afhankelijk van onze positie t.o.v de muur moeten we eerst uitwijken voor zijn hoek of niet.
            mogelijks_uitwijken = abs(self.rect.centerx - relevante_muur.rect.centerx) < breedte_muur_en_speler or abs(self.rect.centery - relevante_muur.rect.centery) < breedte_muur_en_speler

            #dit zijn de punten rond onze muur waarlans we moeten passeren om zo vlot mogelijk met ons dik gat er rond te geraken:
            keypoints_muur = [
                naar_muur - (breedte_muur_en_speler,breedte_muur_en_speler), #linksboven (buiten muur)
                naar_muur + (breedte_muur_en_speler, -breedte_muur_en_speler), #RB
                naar_muur + (-breedte_muur_en_speler, breedte_muur_en_speler), #LO
                naar_muur + (breedte_muur_en_speler, breedte_muur_en_speler) #RO
            ]

            keypoints_muur.sort(key=self.lengte_squared_vector)
            hoek_dichtste_keypoint_en_target = 360 if keypoints_muur[0].magnitude_squared() == 0 else to_target.angle_to(keypoints_muur[0]) if abs(to_target.angle_to(keypoints_muur[0])) < 180 else (360 - abs(to_target.angle_to(keypoints_muur[0])))*to_target.angle_to(keypoints_muur[0])/abs(to_target.angle_to(keypoints_muur[0]))
            #hoek tussen dichtste keypoint en target (perspectief: guard), neem 360 indien we op de keypoint staan (werkt goed voor volgende if statement)
            al_voorbij_eerste_hoek = hoek_dichtste_keypoint_en_target > 90

            #afhankelijk van dus de exacte positie moeten we slechts langs 1 of meerdere van deze punten om zo efficient mogelijk langs onze muur te glijden
            #na wat testen blijkt dat we nog een laatste variabele nodig hebben voor wat uitzonderingen (zie voor jezelf wat er gebeurd als je deze weg haalt):
            hoek_eerste_keypoint_en_center_muur = keypoints_muur[0].angle_to(naar_muur) if abs(keypoints_muur[0].angle_to(naar_muur)) < 180 else (360 - abs(keypoints_muur[0].angle_to(naar_muur)))*keypoints_muur[0].angle_to(naar_muur)/abs(keypoints_muur[0].angle_to(naar_muur))
            eerste_keypoint_richting = 'L' if hoek_eerste_keypoint_en_center_muur > 0 else 'R' if hoek_eerste_keypoint_en_center_muur < 0 else "M"

            if eerste_keypoint_richting != richting and not al_voorbij_eerste_hoek:
                keypoints_muur[0], keypoints_muur[1] = keypoints_muur[1], keypoints_muur[0]

            if mogelijks_uitwijken and not al_voorbij_eerste_hoek:
                return keypoints_muur[0]
            else:
                hoek_tweede_keypoint_en_center_muur = keypoints_muur[1].angle_to(naar_muur) if abs(keypoints_muur[1].angle_to(naar_muur)) < 180 else (360 - abs(keypoints_muur[1].angle_to(naar_muur)))*keypoints_muur[1].angle_to(naar_muur)/abs(keypoints_muur[1].angle_to(naar_muur))
                tweede_hoek_is_links = hoek_tweede_keypoint_en_center_muur > 0
                return keypoints_muur[1] if richting == 'L' and tweede_hoek_is_links or richting == 'R' and not tweede_hoek_is_links else keypoints_muur[2]

    
    def lengte_squared_vector(self, vector): #puur data verwerking, onderande gebruikt in move_and_dogde_walls
        if type(vector) == pg.math.Vector2:
            return vector.magnitude_squared()