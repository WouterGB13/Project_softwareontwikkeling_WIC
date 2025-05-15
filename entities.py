import pygame as pg  # Importeert de pygame-bibliotheek en geeft het een kortere naam 'pg'
import math          # Voor wiskundige functies zoals sqrt, hypot, enz.
from GameSettings import *  # Importeert spelinstellingen zoals TILESIZE, kleuren, etc.
from pathfinding import *   # Importeert padzoek-algoritmes of gerelateerde functies
import random        # Voor willekeurige getallen, bijv. voor gedrag of positiekeuze

vec = pg.math.Vector2  # Maakt een alias voor Vector2, handig voor posities en snelheidsvectoren

class Entity:
    def __init__(self, game, pos, image_path=None, color=None):
        self.game = game  # Verwijzing naar het Game-object (context en toegang tot gemeenschappelijke info)
        self.pos = vec(pos) * TILESIZE  # Positie in tiles wordt omgerekend naar pixels
        self.image = pg.Surface((TILESIZE, TILESIZE))  # Basisvorm van de entiteit: vierkant van 1 tile groot
        self.color = color  # Opslag van kleur (indien meegegeven)
        if image_path:  # Indien pad naar afbeelding opgegeven, laad afbeelding
            self.image = pg.image.load(image_path).convert_alpha()  # Laad afbeelding met transparantie
            self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))  # Schaal naar grootte van 1 tile

        elif color:  # Als er geen afbeelding is maar wel een kleur, vul oppervlak met kleur
            self.image.fill(color)

        else:  # Als geen kleur of afbeelding opgegeven is, gebruik standaardkleur wit
            self.image.fill(WIT)

        self.rect = self.image.get_rect(topleft=self.pos)  # Bepaal rechthoek voor positionering en botsing

    def update(self):
        self.rect.topleft = self.pos  # Werk rect-positie bij op basis van vectorpositie (bijv. na beweging)

class Wall(Entity):  # Een muur is een statisch object, afgeleid van Entity
    def __init__(self, game, pos):
        super().__init__(game, pos, color=GROEN)  # Groene tegel als muur, geen extra gedrag nodig

class Exit:  # Een uitgang; geen Entity-subklasse want heeft geen gedrag of kleur
    def __init__(self, game, pos):
        self.game = game  # Verwijzing naar het spel-object
        self.x, self.y = pos  # Opslag van positie in tiles (x, y)

        self.image = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)  # Transparant oppervlak
        self.rect = self.image.get_rect()  # Rechthoek voor botsing en positionering
        self.rect.topleft = (self.x * TILESIZE, self.y * TILESIZE)  # Omgerekende positie in pixels

    def update(self):
        pass  # Uitgangen bewegen niet, dus geen update nodig

    def draw(self, screen, camera):
        font = pg.font.SysFont(None, 20)  # Klein lettertype aanmaken
        text = font.render("EXIT", True, ROOD)  # Render tekst in rood
        screen_pos = camera.apply_rect(self.rect)  # Bereken schermpositie via camera offset
        text_rect = text.get_rect(center=screen_pos.center)  # Centreren van de tekst op de tegel
        screen.blit(text, text_rect)  # Tekent 'EXIT' label op het scherm op de juiste positie

class Trap(Entity): #uiteindelijk niet af geraakt
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

class Score(Entity):  # Score-item die kan worden opgepakt
    def __init__(self, game, pos):
        super().__init__(game, pos, color=BLAUW)  # Initialiseer de entity met de kleur blauw

    def update(self):
        if self.rect.colliderect(self.game.player):  # Als de speler het score-item aanraakt
            self.game.score += 1  # Verhoog de score van het spel
            pos = random.choice(self.game.possible_score_pos)  # Kies een willekeurige positie voor het nieuwe score-item
            punt = Score(self.game, pos)  # Maak een nieuw score-item aan
            self.game.possible_score_pos.remove(pos)  # Verwijder de gekozen positie uit de lijst van mogelijke posities
            self.game.entities.append(punt)  # Voeg het nieuwe score-item toe aan de lijst van entities
            self.game.possible_score_pos.append(tuple(self.pos // 32))  # Voeg de oude positie terug in de lijst van mogelijke posities
            self.game.entities.remove(self)  # Verwijder dit score-item van de lijst van entities

class Bag(Entity):  # Een object om punten op te slaan, niet aangetast door de guard
    def __init__(self, game, pos):
        super().__init__(game, pos, color=BRUIN)  # Initialiseer de entity met de kleur bruin
        self.content = 0  # Initialiseer de inhoud (de opgeslagen score)
        self.cooldown = 0  # Stel de cooldown in voor het gebruik van de tas

    def update(self):
        if self.rect.colliderect(self.game.player):  # Als de speler in contact komt met de tas
            self.game.show_bag = True  # Laat texst voor de tas zien
            keys = pg.key.get_pressed()  # Haal de toetsinvoer op
            if self.cooldown != 0:  # Als de cooldown actief is
                self.cooldown -= 1  # Verlaag de cooldown
            if keys[pg.K_p] and self.cooldown == 0:  # Als de speler op P drukt en er geen cooldown is
                if self.content == 0:  # Als de tas leeg is 
                    self.content = self.game.score  # Zet de inhoud van de tas gelijk aan de huidige score
                    self.game.score = 0  # Reset de score van het spel
                else:  # Als er geen cooldown is
                    self.game.score += self.content  # Voeg de inhoud van de tas toe aan de score
                    self.content = 0  # Maak de tas leeg
                self.cooldown = 20  # Zet de cooldown om herhaalde druk op de knop te voorkomen
        else:
            self.game.show_bag = False  # Verberg de tas prompt als de speler niet in contact is met de tas

class Player(Entity):  # De speler als een entity
    def __init__(self, game, pos, color):
        super().__init__(game, pos, color=color)  # Initialiseer de speler met kleur
        self.vel = vec(0, 0)  # Stel de snelheid van de speler in op nul
        self.speed = SPELER_SNELHEID  # Stel de snelheid van de speler in
        self.stunned = False  # Stun-status van de speler
        self.stun_start_time = 0  # Tijd waarop de speler gestund werd
        self.stun_duration = 0  # Duur van de stun
        self.lives = MAX_LIVES  # Het aantal levens van de speler
        self.last_wall_pos = self.pos.copy()  # De laatst bekende muurpositie van de speler
        self.smart_walls = []  # Lijst van muren die dichtbij de speler zijn

    def get_keys(self):
        self.vel = vec(0, 0)  # Reset de snelheid naar nul
        keys = pg.key.get_pressed()  # Haal de toetsinvoer op
        if keys[pg.K_q] or keys[pg.K_LEFT]:  # Als de speler naar links beweegt
            self.vel.x = -self.speed  # Zet de horizontale snelheid naar links
        if keys[pg.K_d] or keys[pg.K_RIGHT]:  # Als de speler naar rechts beweegt
            self.vel.x = self.speed  # Zet de horizontale snelheid naar rechts
        if keys[pg.K_z] or keys[pg.K_UP]:  # Als de speler omhoog beweegt
            self.vel.y = -self.speed  # Zet de verticale snelheid naar boven
        if keys[pg.K_s] or keys[pg.K_DOWN]:  # Als de speler omlaag beweegt
            self.vel.y = self.speed  # Zet de verticale snelheid naar beneden

        if self.vel.x != 0 and self.vel.y != 0:  # Als de speler zowel horizontaal als verticaal beweegt
            self.vel *= math.sqrt(2) / 2  # Normaliseer de snelheid om diagonale beweging soepel te maken

    def load_close_walls(self):  # Laad de muren die dicht bij de speler zijn voor rendering
        self.last_wall_pos = self.pos.copy()  # Sla de huidige positie van de speler op
        self.smart_walls = []  # Maak de lijst van muren leeg
        for wall in self.game.walls:  # Loop door alle muren in het spel
            if (wall.pos - self.last_wall_pos).magnitude_squared() < MAX_WALL_DIST**2:  # Als de muur dichtbij is
                self.smart_walls.append(wall)  # Voeg de muur toe aan de lijst van "dichte" muren

    def collide_with_walls(self, direction):  # Controleer op botsingen met muren
        for wall in self.smart_walls:  # Loop door de dichte muren
            if self.rect.colliderect(wall.rect):  # Als de speler met een muur botst
                if direction == 'x':  # Als de botsing in de x-richting is
                    if self.vel.x > 0:  # Als de speler naar rechts beweegt
                        self.pos.x = wall.rect.left - self.rect.width  # Stop de speler aan de rechterkant van de muur
                    if self.vel.x < 0:  # Als de speler naar links beweegt
                        self.pos.x = wall.rect.right  # Stop de speler aan de linkerkant van de muur
                    self.vel.x = 0  # Zet de snelheid in de x-richting naar nul
                    self.rect.x = self.pos.x  # Werk de rect van de speler bij
                if direction == 'y':  # Als de botsing in de y-richting is
                    if self.vel.y > 0:  # Als de speler naar beneden beweegt
                        self.pos.y = wall.rect.top - self.rect.height  # Stop de speler aan de bovenkant van de muur
                    if self.vel.y < 0:  # Als de speler naar boven beweegt
                        self.pos.y = wall.rect.bottom  # Stop de speler aan de onderkant van de muur
                    self.vel.y = 0  # Zet de snelheid in de y-richting naar nul
                    self.rect.y = self.pos.y  # Werk de rect van de speler bij

    def update(self):
        self.get_keys()  # Verkrijg de toetsinvoer en werk de snelheid bij
        current_time = pg.time.get_ticks()  # Verkrijg de huidige tijd in milliseconden
        if self.stunned:  # Als de speler gestund is
            if current_time - self.stun_start_time < self.stun_duration:  # Als de stun nog actief is
                self.vel = vec(0, 0)  # Zet de snelheid naar nul
                return  # De speler kan niets doen
            else:
                self.stunned = False  # De stun is voorbij

        if (self.pos - self.last_wall_pos).magnitude_squared() > (MAX_PLAYER_MOVE)**2:  # Als de speler zich te ver van de laatst geladen muren heeft bewogen
            self.load_close_walls()  # Laad de muren die dichtbij zijn

        # Verwerk eerst de beweging in de x-richting
        self.pos.x += self.vel.x * self.game.dt  # Werk de positie van de speler bij
        self.rect.x = self.pos.x  # Werk de rect van de speler bij
        self.collide_with_walls('x')  # Controleer op botsingen met muren in de x-richting

        # Verwerk vervolgens de beweging in de y-richting
        self.pos.y += self.vel.y * self.game.dt  # Werk de positie van de speler bij
        self.rect.y = self.pos.y  # Werk de rect van de speler bij
        self.collide_with_walls('y')  # Controleer op botsingen met muren in de y-richting

class BaseGuard(Entity):  # Klasse die een bewaker voorstelt; erft van Entity. Opgesplitst van originele Guard class om versieversies te onderscheiden.
    def __init__(self, game, pos, route):
        super().__init__(game, pos, color=ROOD)  # Roept de constructor van de bovenliggende Entity-klasse aan met spelreferentie, positie en kleur.
        self.route = route  # De route die de guard moet volgen (lijst met coördinaten).
        self.checkpoint = 0  # Start bij het eerste punt op de route.
        self.speed = GUARD_SNELHEID  # Snelheid waarmee de guard beweegt (constante).
        try:
            self.target = vec(self.route[1]) * TILESIZE  # Volgende doelpunt op de route, omgerekend naar pixelpositie.
        except IndexError:
            self.target = vec(self.route[0]) * TILESIZE  # Voor guards met slechts één punt in route — die blijven dan stil staan.
        self.target_rot = 0  # Richtingshoek waarin de guard kijkt (graden vanaf x-as).

    def navigate(self, start, end):
        direction = vec(end) - vec(start)  # Bereken richtingvector van start naar eindpunt.
        if direction.length() != 0:
            return direction.normalize()  # Genormaliseerde (lengte 1) vector zodat beweging consistent is.
        return vec(0, 0)  # Indien er geen richting is (zelfde punt), geef nulvector terug.

    def at_checkpoint(self):
        return self.pos.distance_to(self.target) < 0.5  # Controleert of de guard dicht genoeg bij het doel is (tolerantiemarge 0.5).

    def patrol(self):
        if not self.at_checkpoint():  # Als guard nog niet bij het huidige doelpunt is:
            move_dir = self.navigate(self.pos, self.target)  # Bereken beweegrichting.
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))  # Bepaal rotatiehoek t.o.v. x-as.
            self.pos += move_dir * self.speed * self.game.dt  # Verplaats guard rekening houdend met snelheid en tijdsdelta.
        else:
            self.pos = self.target  # Zorg dat guard exact op het doel komt te staan.
            self.checkpoint = (self.checkpoint + 1) % len(self.route)  # Ga naar volgende checkpoint (loop terug naar begin bij einde).
            self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE  # Bepaal volgend doelpunt in pixels.
        self.rect.topleft = self.pos  # Update de positie van de guard in de rechthoek (voor collision/rendering).

class Guard(BaseGuard):  # Definieert een Guard-klasse die uitbreidt van BaseGuard
    def __init__(self, game, pos, route):  # Constructor: initialiseert een Guard object
        super().__init__(game, pos, route)  # Roept constructor van de superklasse aan met game, positie en route
        self.state = "patrol"  # Beginstatus van de guard is 'patrouille'
        self.last_seen_pos = None  # Laatst geziene positie van de speler
        self.last_seen_time = 0  # Tijdstip waarop speler laatst gezien is

        # Vision instellingen vanuit GameSettings
        self.player_in_sight = False  # Houdt bij of speler in zicht is
        self.can_hear_player = False  # Houdt bij of speler hoorbaar is
        self.view_angle_default = VISIE_BREEDTE  # Standaard gezichtsveldhoek
        self.view_dist_default = VIEW_DIST  # Standaard gezichtsafstand
        self.view_resolution = RESOLUTIE  # Resolutie van het zichtveld (aantal lijnen)

        # Tijdens chase: smallere blik maar verder kijken
        self.view_angle_chase = 30  # Vernauwde blik tijdens achtervolging
        self.view_dist_chase = self.view_dist_default * 1.5  # Grotere afstand tijdens chase

        # Startwaarden
        self.view_angle = self.view_angle_default  # Initieel gezichtsveldhoek
        self.view_dist = self.view_dist_default  # Initieel gezichtsafstand
        
        self.search_time = SEARCH_TIME_MS  # Hoelang de guard zoekt na verlies van zicht
        self.rot = 0  # Huidige rotatiehoek
        self.rotate_speed = ROTATE_SPEED  # Snelheid waarmee guard draait
        self.vel = vec(0, 0)  # Beginsnelheid (geen beweging)

    def reset(self):  # Reset de guard naar beginstatus (bijv. als speler gepakt is)
        self.state = "patrol"  # Terug naar patrouille
        self.last_seen_pos = None  # Verlies informatie over speler
        self.last_seen_time = 0

        # Herinitialiseer zichtinstellingen
        self.view_angle_default = VISIE_BREEDTE
        self.view_dist_default = VIEW_DIST
        self.view_resolution = RESOLUTIE

        # Herinitialiseer chase-zichtinstellingen
        self.view_angle_chase = 30
        self.view_dist_chase = self.view_dist_default * 1.5

        # Herinitialiseer zichtwaarden
        self.view_angle = self.view_angle_default
        self.view_dist = self.view_dist_default
        self.search_time = SEARCH_TIME_MS
        self.rot = 0
        self.rotate_speed = ROTATE_SPEED
        self.vel = vec(0, 0)

    def update(self):  # Wordt elke frame aangeroepen om guard gedrag te updaten
        current_time = pg.time.get_ticks()  # Huidige tijd in ms sinds game start

        # Altijd speler detecteren, ongeacht status
        if self.detect_player():
            if self.state != "chase":  # Enkel van status veranderen als nog niet in achtervolging
                self.state = "chase"
                self.last_seen_pos = vec(self.game.player.rect.center)  # Spelerpositie opslaan
                self.last_seen_time = current_time
                self.alert_nearby_guards()  # Nabijgelegen guards waarschuwen

        # Soepele rotatie naar target_rot
        rot_diff = (self.target_rot - self.rot) % 360  # Bereken verschil in graden
        if rot_diff > 180:
            rot_diff -= 360  # Kies kortste draai richting
        rotation_step = self.rotate_speed * self.game.dt  # Hoeveel graden draaien per frame
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot  # Direct instellen als klein verschil
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360  # Zorg dat rotatie tussen 0-359 blijft

        # Gedrag gebaseerd op status
        if self.state == "patrol":
            move_dir = self.navigate(self.pos, self.target)  # Bereken richting naar volgend punt
            self.view_angle = self.view_angle_default  # Normale kijkhoek
            self.view_dist = self.view_dist_default  # Normale kijkafstand
            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))  # Richting om naartoe te kijken
                self.vel = move_dir * self.speed  # Snelheid instellen
                self.move_and_collide()  # Beweeg en check botsingen

            if self.at_checkpoint():  # Als guard doel bereikt heeft
                self.checkpoint = (self.checkpoint + 1) % len(self.route)  # Volgende punt kiezen
                self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

        elif self.state == "chase" or self.state == "chase_help":
            if self.detect_player():  # Als speler nog steeds gezien wordt
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.view_angle = self.view_angle_chase  # Vernauw gezichtsveld
                self.view_dist = self.view_dist_chase  # Verhoog gezichtsafstand

            if self.state == "chase":  # Enkel als hoofdachtervolger
                self.alert_nearby_guards()  # Andere guards waarschuwen

            if self.last_seen_pos:  # Als laatst geziene positie bekend is
                to_target = self.last_seen_pos - vec(self.rect.center)  # Vector naar doel
                if to_target.length() > 0:
                    move_dir = to_target.normalize()  # Richting naar doel
                    self.vel = move_dir * GUARD_SNELHEID_CHASE  # Chase snelheid
                    self.target_rot = move_dir.angle_to(vec(1, 0))  # Richting instellen
                    self.move_and_collide()

                if to_target.length() < 4:  # Aangekomen op laatst geziene positie
                    self.state = "search"  # Wissel naar zoekmodus
                    self.search_start_time = current_time

        elif self.state == "search":
            self.vel = vec(0, 0)  # Blijf staan
            self.target_rot += 20 * self.game.dt  # Kijk langzaam rond
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"  # Na zoektijd weer patrouilleren

    def detect_player(self):  # Check of speler gezien of gehoord wordt
        return self.see_player() or self.hear_player()

    def see_player(self):  # Visuele detectie van speler
        player = self.game.player

        player_points = [  # Mogelijke zichtbare punten van speler
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
                continue  # Te ver weg

            facing = vec(1, 0).rotate(-self.rot)  # Richting waarin guard kijkt
            angle = facing.angle_to(direction)  # Hoek tussen zicht en speler

            if abs(angle) > self.view_angle:
                continue  # Buiten gezichtsveld

            if self.line_of_sight_clear(vec(self.rect.center), point, self.game.player.smart_walls) == True:
                self.player_in_sight = True
                return True  # Speler gedetecteerd
        self.player_in_sight = False
        return False  # Geen van de punten gezien

    def hear_player(self):  # Akoestische detectie van speler
        distance = (vec(self.game.player.rect.center) - vec(self.rect.center)).magnitude_squared()
        if distance == HEAR_DIST**2 or distance < HEAR_DIST**2:  # Binnen hoorafstand
            self.can_hear_player = True
            return True
        else:
            self.can_hear_player = False
            return False

    def line_of_sight_clear(self, start, end, walls):  # Check of zicht niet geblokkeerd is
        for wall in walls:
            if wall.rect.clipline(start, end):  # Check of lijn doorsneden wordt
                return wall  # Zicht geblokkeerd door muur
        return True  # Vrij zicht

    def alert_nearby_guards(self):  # Waarschuw guards in de buurt
        for entity in self.game.entities:
            if isinstance(entity, Guard) and entity != self:
                distance = self.pos.distance_to(entity.pos)
                if distance < ALERT_DISTANCE:
                    if self.state == "chase":
                        if entity.state != "chase":
                            entity.state = "chase_help"  # Andere guard helpt met achtervolging
                            entity.last_seen_pos = vec(self.last_seen_pos)
                        else:
                            entity.last_seen_pos = vec(self.last_seen_pos)  # Synchroniseer

    def move_and_collide(self):  # Beweeg de guard en check op botsingen
        self.pos.x += self.vel.x * self.game.dt  # Update x-positie
        self.rect.x = self.pos.x
        self.collide_with_walls('x')  # Check botsing in x-richting

        self.pos.y += self.vel.y * self.game.dt  # Update y-positie
        self.rect.y = self.pos.y
        self.collide_with_walls('y')  # Check botsing in y-richting

    def collide_with_walls(self, direction):  # Botsingsafhandeling
        for wall in self.game.player.smart_walls:
            if self.rect.colliderect(wall.rect):  # Als guard botst met muur
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

    def draw_view_field(self):  # Teken het gezichtsveld van de guard
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        points = [center]
        for i in range(self.view_resolution + 1):
            angle = (-self.view_angle + 2 * self.view_angle * (i / self.view_resolution))  # Bereken hoek
            point = center + vec(self.view_dist, 0).rotate(-(self.rot + angle))  # Bereken eindpunt lijn
            if ADAPTIVE_CONES:  # Check op zichtonderbrekingen
                punt = self.line_of_sight_clear(center, point, self.game.player.smart_walls)
                if punt != True:
                    point = punt  # Corrigeer met botsingspunt

            points.append(point)
        kleur = LICHTROOD if self.state == "chase" else ZWART  # Zichtkleur afhankelijk van status
        # for point in points:  # Debugcircles, tijdelijk uitgeschakeld
        #     pg.draw.circle(self.game.screen, ROOD, point, 4)
        pg.draw.polygon(self.game.screen, kleur, points, 2)  # Teken zichtveld als polygon

class Domme_Guard(Guard):  # Subklasse van Guard; speciale domme variant die terugkeert naar originele route
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)  # Roep constructor van Guard aan
        self.retreat_path = []  # Pad waarlangs guard kan terugkeren naar originele route

    def checkretreat(self):  # Check of retreat path niet leeg is
        if len(self.retreat_path) != 0:
            return True  # Guard is aan het terugkeren
        return False  # Geen retreat actief
    
    def update(self):  # Wordt elke frame aangeroepen
        current_time = pg.time.get_ticks()  # Huidige tijd in ms

        # ALTIJD speler detecteren, ongeacht status
        if self.detect_player():
            if self.state != "chase":  # Alleen als niet al in achtervolging
                self.state = "chase"
                self.last_seen_pos = vec(self.game.player.rect.center)  # Spelerpositie onthouden
                self.last_seen_time = current_time
                self.alert_nearby_guards()  # Andere guards waarschuwen

        # Soepele rotatie
        rot_diff = (self.target_rot - self.rot) % 360  # Bepaal verschil in rotatie
        if rot_diff > 180:
            rot_diff -= 360  # Kies kortste draairichting
        rotation_step = self.rotate_speed * self.game.dt  # Hoeveel graden draaien deze frame
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot  # Direct corrigeren als verschil klein is
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360  # Zorg dat rotatie binnen 0–359 blijft

        # Gedrag afhankelijk van status
        if self.state == "patrol":
            if self.checkretreat() == True:  # Als terugkeer bezig is
                self.next_target = self.target.copy()  # Onthoud waar we onderbroken werden
                self.current_checkpoint = (self.checkpoint)  # Onthoud huidige checkpoint
                self.target = self.retreat_path[-1]  # Volg terugpad

            move_dir = self.navigate(self.pos, self.target)  # Navigatie richting target
            self.view_angle = self.view_angle_default  # Normaal gezichtsveld
            self.view_dist = self.view_dist_default  # Normale kijkafstand

            if move_dir.length() > 0:
                self.target_rot = move_dir.angle_to(vec(1, 0))  # Draai richting doel
                self.vel = move_dir * self.speed  # Stel snelheid in
                self.move_and_collide()  # Beweeg en bots

            if self.at_checkpoint():  # Als target bereikt
                if len(self.retreat_path) != 0:
                    self.retreat_path.pop(-1)  # Verwijder laatste punt
                    if len(self.retreat_path) >= 1:  # Nog punten over
                        self.target = self.retreat_path[-1]  # Volgende in terugpad
                    else: 
                        self.target = self.next_target  # Hervat originele pad
                        self.checkpoint = self.current_checkpoint - 1  # Zet terug om verder te gaan
                else:        
                    self.checkpoint = (self.checkpoint + 1) % len(self.route)  # Normaal volgende punt
                    # print(self.checkpoint)  # Debug: huidige index
                    self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE
                    # print(self.target.x/TILESIZE,self.target.y/TILESIZE)  # Debug: doelpositie

        elif self.state == "chase" or self.state == "chase_help":
            if self.detect_player():  # Speler nog steeds zichtbaar
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.view_angle = self.view_angle_chase  # Chase zichtveld
                self.view_dist = self.view_dist_chase

            self.retreat_path.append(self.pos.copy())  # Voeg huidige positie toe aan terugpad

            if current_time - self.last_seen_time > STUCK_TIME_LIMIT:  # Speler te lang kwijt
                self.state = "search"  # Ga zoeken
                self.search_start_time = current_time

            # Synchroniseer met andere guards als hoofdachtervolger
            if self.state == "chase":
                self.alert_nearby_guards()

            if self.last_seen_pos:  # Als we een laatste positie kennen
                to_target = self.last_seen_pos - vec(self.rect.center)  # Richting naar laatst geziene
                if to_target.length() > 0:
                    move_dir = to_target.normalize()  # Genormaliseerde richting
                    self.vel = move_dir * GUARD_SNELHEID_CHASE  # Chase snelheid
                    self.target_rot = move_dir.angle_to(vec(1, 0))  # Richting hoofd
                    self.move_and_collide()

                if to_target.length() < 4:  # Bijna aangekomen bij laatst geziene locatie
                    self.state = "search"
                    self.search_start_time = current_time

        elif self.state == "search":
            self.vel = vec(0, 0)  # Blijf staan
            self.target_rot += ROTATE_SPEED / 5 * self.game.dt  # Kijk langzaam rond
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"  # Keer terug naar patrouille

class Slimme_Guard(Guard):  # Subklasse van Guard; deze variant gebruikt slimme pathfinding
    def __init__(self, game, pos, route):
        super().__init__(game, pos, route)  # Roep constructor van Guard aan
        self.image.fill(PAARS)  # Kleur deze guard paars voor visueel onderscheid
        self.prev_pos = vec(self.pos)  # Houd vorige positie bij (voor vastloopdetectie)
        self.stuck_timer = 0  # Timer die bijhoudt hoelang guard vastzit
        self.chase_path = []  # Slim pad richting speler (berekend met A*)
        self.retreat_path = []  # Slim pad terug naar originele route
        self.chase_start_pos = None  # Locatie waar chase begon (om retreat te starten)
        self.last_pos_for_smart_path = vec(0,0)  # Laatst berekende spelerpositie voor pathfinding

    def checkretreat(self):  # Check of guard in terugkeermodus is
        if len(self.retreat_path) != 0:
            return True
        return False

    def update(self):  # Wordt elke frame aangeroepen
        current_time = pg.time.get_ticks()  # Huidige tijd in ms

        # Speler detecteren
        if self.detect_player():
            if self.state != "chase":  # Alleen als nog niet in achtervolging
                self.state = "chase"
                if self.chase_start_pos == None:
                    self.chase_start_pos = (int(self.pos.x/TILESIZE), int(self.pos.y/TILESIZE))  # Zet begin chase-positie
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.alert_nearby_guards()

        # Soepele rotatie naar target_rot
        rot_diff = (self.target_rot - self.rot) % 360
        if rot_diff > 180:
            rot_diff -= 360
        rotation_step = self.rotate_speed * self.game.dt
        if abs(rot_diff) < rotation_step:
            self.rot = self.target_rot
        else:
            self.rot += rotation_step if rot_diff > 0 else -rotation_step
        self.rot %= 360

        # Gedragspatronen per toestand
        if self.state == "patrol":
            if self.checkretreat() == True:
                self.next_target = self.target  # Sla huidige target tijdelijk op
                self.current_checkpoint = (self.checkpoint)  # Sla huidige routepositie op
                self.target = self.retreat_path[-1][0]*TILESIZE,self.retreat_path[-1][1]*TILESIZE  # Volgende stap in retreat path

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
                    if len(self.retreat_path) >= 1:
                        self.retreat_path = reverse_cut_path(self, self.retreat_path, self.view_dist//TILESIZE*4)  # Optimaliseer terugpad
                        self.target = self.retreat_path[-1]
                    else:
                        self.target = self.next_target  # Keer terug naar originele target
                        self.checkpoint = self.current_checkpoint - 1  # Corrigeer checkpoint-offset
                else:
                    self.checkpoint = (self.checkpoint + 1) % len(self.route)
                    self.target = vec(self.route[(self.checkpoint + 1) % len(self.route)]) * TILESIZE

        elif self.state == "chase" or self.state == "chase_help":
            if self.detect_player():
                self.last_seen_pos = vec(self.game.player.rect.center)
                self.last_seen_time = current_time
                self.view_angle = self.view_angle_chase
                self.view_dist = self.view_dist_chase

            if self.state == "chase":
                self.alert_nearby_guards()

            if self.player_in_sight:  # Speler direct in zicht
                self.last_pos_for_smart_path = vec(0,0)  # Reset path-memo
                to_target = vec(self.game.player.rect.center) - vec(self.rect.center)
                if to_target.length() > 0:
                    move_dir = to_target.normalize()
                    self.vel = move_dir * GUARD_SNELHEID_CHASE
                    self.target_rot = move_dir.angle_to(vec(1, 0))
                    self.move_and_collide()

            # Speler niet in zicht, maar laatst bekende positie gebruiken voor pad
            elif self.last_seen_pos and (self.last_pos_for_smart_path == vec(0,0) or (self.last_pos_for_smart_path - self.last_seen_pos).magnitude_squared() > HEAR_DIST**2 or self.can_hear_player):
                self.last_pos_for_smart_path = self.last_seen_pos  # Update laatst bekende
                pos_on_map = (int(self.rect.centerx/TILESIZE), int(self.rect.centery/TILESIZE))
                player_pos_on_map = (int(self.last_seen_pos[0]/TILESIZE), int(self.last_seen_pos[1]/TILESIZE))
                self.chase_path = cut_path(self, simplefy_path(find_path(self.game, pos_on_map, player_pos_on_map)), self.view_dist//TILESIZE)  # Slim pad via A*

                try:
                    to_target = vec(self.chase_path[1])*TILESIZE - vec(self.rect.center) +(TILESIZE/2, TILESIZE/2)  # Corrigeer grid naar pixelpositie
                    if to_target.length() > 0:
                        move_dir = to_target.normalize()
                        self.vel = move_dir * GUARD_SNELHEID_CHASE
                        self.target_rot = move_dir.angle_to(vec(1, 0))
                        self.move_and_collide()
                except: pass  # Fallback als pad te kort is

            else:  # Volg bestaand chase pad verder
                try:
                    to_target = vec(self.chase_path[1])*TILESIZE - vec(self.rect.center) +(TILESIZE/2, TILESIZE/2)
                    if to_target.length() > 0:
                        move_dir = to_target.normalize()
                        self.vel = move_dir * GUARD_SNELHEID_CHASE
                        self.target_rot = move_dir.angle_to(vec(1, 0))
                        self.move_and_collide()
                    if to_target.length() < 4 and len(self.chase_path) > 2:  # Stap afgerond, volgende
                        self.chase_path.pop(1)
                except: pass

            # Als guard laatste punt bereikt (spelerpositie)
            if (len(self.chase_path) > 0 and (vec(self.chase_path[-1])*TILESIZE - vec(self.rect.center) +(TILESIZE/2, TILESIZE/2)).length() < 4):
                self.state = "search"  # Overschakelen naar zoekmodus
                pos_on_map = (int(self.rect.x/TILESIZE), int(self.rect.y/TILESIZE))
                self.retreat_path = cut_path(self, simplefy_path(find_path(self.game,pos_on_map,self.chase_start_pos)), self.view_dist//TILESIZE*4)  # Pad terug genereren
                self.retreat_path.reverse()
                self.search_start_time = current_time
                self.chase_start_pos == None  # Reset startpositie voor volgende chase

            elif len(self.chase_path) == 1:  # Speciale case: slechts 1 padpunt
                to_target = vec(self.chase_path[0])*TILESIZE - vec(self.rect.center) +(TILESIZE/2, TILESIZE/2)
                if to_target.length() > 0:
                    move_dir = to_target.normalize()
                    self.vel = move_dir * GUARD_SNELHEID_CHASE
                    self.target_rot = move_dir.angle_to(vec(1, 0))
                    self.move_and_collide()

        elif self.state == "search":
            self.vel = vec(0, 0)  # Geen beweging
            self.target_rot += ROTATE_SPEED/5 * self.game.dt  # Rustig rondkijken
            if current_time - self.search_start_time > self.search_time:
                self.state = "patrol"  # Terug naar patrouillemodus