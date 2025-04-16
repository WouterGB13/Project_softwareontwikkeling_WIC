import pygame as pg
from GameSettings import *
import math
vec = pg.math.Vector2

entitylijst = []

# Klasse voor de speler
class Player():
    def __init__(self,game,x,y, kleur): # gebruik relatieve posities zodat de player altijd binnen squares blijft
        self.game = game
        self.image = pg.Surface((TILESIZE,TILESIZE))  # Spelerafbeelding van TILESIZE x TILESIZE
        self.image.fill(kleur)  # Geef de speler een kleur
        self.vx = 0  # horizontale snelheid
        self.vy = 0  # verticale snelheid
        self.rect = self.image.get_rect()  # hitbox rechthoek
        self.x = x * TILESIZE  # zet speler op juiste X-positie in pixels
        self.y = y * TILESIZE  # zet speler op juiste Y-positie in pixels

    # Controleer welke toetsen worden ingedrukt en pas snelheid aan
    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys  = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            pg.quit()
            exit()
        if keys[pg.K_q] or keys[pg.K_LEFT]:  # links bewegen
            self.vx = -SPELER_SNELHEID
        if keys[pg.K_d] or keys[pg.K_RIGHT]:  # rechts bewegen
            self.vx = SPELER_SNELHEID
        if keys[pg.K_z] or keys[pg.K_UP]:  # omhoog bewegen
            self.vy = -SPELER_SNELHEID
        if keys[pg.K_s] or keys[pg.K_DOWN]:  # omlaag bewegen
            self.vy = SPELER_SNELHEID
        # voorkom snellere diagonale beweging door te normaliseren
        if self.vx != 0 and self.vy != 0:
            self.vy *= math.sqrt(2)/2
            self.vx *= math.sqrt(2)/2

    # Check voor botsingen met muren
    def object_collision(self):
        collisionlist = [] #dient om meerdere botsingen tegelijk te kunnen registeren, ander ontstaan clipping problemen
        for wall in self.game.walls: 
            if self.rect.colliderect(wall.rect): #check voor elke muur of hitbox van speler en muur overlappen, zo ja, voeg collision toe aan lijst
                collisionlist.append(wall)
        return collisionlist

    # Corrigeer positie als er een botsing is in een bepaalde richting
    def collide_with_walls(self, dir):
        hits = self.object_collision()
        for wall in hits:
            if dir == 'x': #richtingsgebonden collisions zorgen ervoor dat je niet tot full stop komt als je een muur raakt
                if self.vx > 0:  # beweeg naar rechts
                    self.x = wall.rect.left - self.rect.width
                elif self.vx < 0:  # beweeg naar links
                    self.x = wall.rect.right
                self.vx = 0
                self.rect.x = self.x

            elif dir == 'y':
                if self.vy > 0:  # beweeg naar beneden
                    self.y = wall.rect.top - self.rect.height
                elif self.vy < 0:  # beweeg naar boven
                    self.y = wall.rect.bottom
                self.vy = 0
                self.rect.y = self.y

    # Update spelerpositie en verwerk botsingen
    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt 
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

# Klasse voor muren
class Wall():

    def __init__(self, game, x, y):  # geen kleurargument want alle muren zijn groen
        self.game = game
        self.kleur = GROEN
        self.image = pg.Surface((TILESIZE,TILESIZE))  # Muurafbeelding
        self.image.fill(self.kleur)  # Geef muur kleur
        self.rect = self.image.get_rect()  # hitbox rechthoek
        self.x = x  # relatieve x
        self.y = y  # relatieve y
        self.rect.x = x*TILESIZE  # positie in pixels
        self.rect.y = y*TILESIZE

    # Wordt op dit moment niet gebruikt, maar kan later uitgebreid worden
    def update(self):
        pass

class Guard0():
    def __init__(self,game,x,y,route): 
        self.game = game
        self.checkpoint = 0
        self.image = pg.Surface((TILESIZE,TILESIZE))  
        self.image.fill(ROOD)  # Geef de guard een kleur
        self.rect = self.image.get_rect()  # hitbox rechthoek
        self.vx = 0
        self.vy = 0
        self.x = x * TILESIZE  # zet guard op juiste X-positie in pixels
        self.y = y * TILESIZE  # zet guard op juiste Y-positie in pixels
        self.rect.x = self.x
        self.rect.y = self.y
        self.route = route #route is lijst met coordinaten in
        self.currentpos = route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = route[self.checkpoint+1]
        self.next_pos = self.next_patrol_pos #2 variabelen gebruiken om af te kunnen wijken van pad om speler te achtervolgen en toch nog te weten waar in patrouille hij zit

    def navigate(self,start,end): #gebruiken om snelheid juist te oriënteren
        self.vx = GUARD_SNELHEID*(((end[0]*TILESIZE)-(start[0]*TILESIZE))/math.sqrt(((end[0]*TILESIZE-start[0]*TILESIZE)**2)+((end[1]*TILESIZE-start[1]*TILESIZE)**2))) #goniometrie uitgeschreven als bewerking
        self.vy = GUARD_SNELHEID*(((end[1]*TILESIZE)-(start[1]*TILESIZE))/math.sqrt(((end[0]*TILESIZE-start[0]*TILESIZE)**2)+((end[1]*TILESIZE-start[1]*TILESIZE)**2))) #idem maar voor y snelheid
        #print(start, end,self.vx,self.vy) #debugging

    # Wordt op dit moment niet gebruikt, maar kan later uitgebreid worden
    def bot_at_checkpoint(self):
        if (self.next_pos[0]*TILESIZE - 3 <=self.x <= self.next_pos[0]*TILESIZE + 3) and (self.next_pos[1]*TILESIZE - 3 <=self.y <= self.next_pos[1]*TILESIZE + 3): #wanneer niet binnen bepaalde marge van doel, navigeer naar doel
            return True
        else:
            return False
        
    def update(self):
        if not self.bot_at_checkpoint(): #wanneer niet binnen bepaalde marge van doel, navigeer naar doel
            self.navigate(self.current_route_pos,self.next_pos)
            #print(self.x,self.next_pos[0]*TILESIZE,self.y, self.next_pos[1]*TILESIZE) #debugging
        else: #wanneer dicht genoeg bij doel, zet locatie gelijk aan doellokatie (compenseert voor marge in bovenstaande if)
            self.vx = 0 #stop beweging
            self.x = self.next_pos[0]*TILESIZE
            self.vy = 0
            self.y = self.next_pos[1]*TILESIZE
            self.checkpoint = (self.checkpoint+1)%len(self.route) #ga naar volgende checkpoint, modulus dient om terug naar eerste checkpoint te gaan na voltooien van loop
            self.current_route_pos = self.next_pos 
            self.next_pos = self.route[(self.checkpoint+1)%len(self.route)]
        self.x += self.vx * self.game.dt #beweging
        self.rect.x = self.x 
        self.y += self.vy * self.game.dt
        self.rect.y = self.y


class Guard1(Guard0): #toevoegen van werken met vectoren/ een richting
    def __init__(self, game, x, y, route):
        self.game = game
        self.checkpoint = 0
        self.route = route
        self.currentpos = route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = route[self.checkpoint+1]
        self.next_pos = self.next_patrol_pos
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(ROOD)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.x = x
        self.y = y
        self.pos = vec(x, y) * TILESIZE

        self.rot = 0 #in ° dus geen radialen
        self.rot_to_player = 0

    def locate_player(self): #hoek bepalen naar speler (tov van evenwijdige met x-as)
        dx, dy = abs(self.x - self.game.player.x), abs(self.y - self.game.player.y)
        if dx == 0:
            self.rot_to_player = 90
        else:
            self.rot_to_player = math.atan(dy/dx)*360/(2*math.pi)
        if self.x - self.game.player.x > 0:
            self.rot_to_player = 180 - self.rot
        if self.y - self.game.player.y < 0:
            self.rot_to_player *= -1

    def navigate(self, start, end):
        dx, dy = abs(start[0] - end[0]), abs(start[1] - end[1]) #bepaal dx en dy tussen huidige lokatie en doel
        if dx == 0: #vermijd delen door 0: verticaal gaan want x moet niet veranderen
            self.rot = 90 #omhoog
        else:
            self.rot = math.atan(dy/dx)*360/(2*math.pi) #bepaalt de hoek op basis van dx en dy (pas op: beeld is enkel tussen -pi/2 en pi/2; aangezien dx en dy positief zijn is het beeld nu zelfs tussen 0 en pi/2)
        if start[0]-end[0] > 0:
            self.rot = 180 - self.rot #neem de suplementaire hoek aka spiegel rond de y-as als dx eigenlijk kleiner is dan nul zodat we ook terug kunnen
        if start[1]-end[1] < 0:
            self.rot *= -1 #neem de tegengestelde hoek aka spiegel rond de x-as als dy echt groter is dan nul (pas op, de y-as wijst hier naar onder) zodat we ook terug kunnen


    def drawfront(self): #wijst de richting aan van de guard
        self.front_point = self.rect.center + vec(TILESIZE, 0).rotate(-self.rot)
        self.front_point += self.game.camera.camera.topleft
        pg.draw.circle(self.game.screen, ZWART, self.front_point , 3)

    def update(self):
        if not self.bot_at_checkpoint():
            self.navigate([self.pos[0]/TILESIZE, self.pos[1]/TILESIZE], self.next_pos)
        else:
            #print("nice :)")
            self.vel = vec(0, 0)
            self.pos = vec(self.next_pos[0], self.next_pos[1])*TILESIZE
            self.x, self.y = self.pos
            self.checkpoint = (self.checkpoint+1)%len(self.route)
            self.current_route_pos = self.next_pos
            self.next_pos = self.route[(self.checkpoint+1)%len(self.route)]
        self.vel = vec(GUARD_SNELHEID, 0).rotate(-self.rot)
        self.pos += self.vel*self.game.dt
        self.x, self.y = round(self.pos[0]), round(self.pos[1])
        self.rect.x, self.rect.y = self.pos

class Guard(Guard1):
    def __init__(self, game, x, y, route):
        self.game = game
        self.checkpoint = 0
        self.route = route
        self.currentpos = route[self.checkpoint]
        self.current_route_pos = self.currentpos
        self.next_patrol_pos = route[self.checkpoint+1]
        self.next_pos = self.next_patrol_pos
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(ROOD)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.x = x
        self.y = y
        self.pos = vec(x, y) * TILESIZE

        self.rot = 0 #in ° dus geen radialen
        self.rot_to_player = 0

        fases = ["patroule", "chase", "retreat"]
        self.fase = fases[0]
        self.vwidth = VIZIE_BREEDTE
        self.vdist = VIEW_DIST

    def locate_player(self):
        return super().locate_player()
    
    def navigate(self, start, end):
        return super().navigate(start, end)

    def drawvieuwfield(self):
        center = vec(self.rect.center) + vec(self.game.camera.camera.topleft)
        Lline = self.rect.center + vec(self.vdist+TILESIZE/2, 0).rotate(-(self.rot+self.vwidth)) + self.game.camera.camera.topleft
        Rline = self.rect.center + vec(self.vdist+TILESIZE/2, 0).rotate(-(self.rot-self.vwidth)) + self.game.camera.camera.topleft
        #teken de lijntjes:
        pg.draw.line(self.game.screen, ZWART, center, Lline)
        pg.draw.line(self.game.screen, ZWART, center, Rline)

        #teken de arc:
        RECT = (self.x-self.vdist  + self.game.camera.camera.x, self.y-self.vdist  + self.game.camera.camera.y, 2*self.vdist+TILESIZE, 2*self.vdist+TILESIZE) #gebruik pg.draw.rect om deze te visualiseren (hieronder: staat in notitie)
        pg.draw.arc(self.game.screen, ZWART, RECT, (self.rot - self.vwidth)/360*math.pi*2, (self.rot + self.vwidth)/360*math.pi*2, self.vdist)
        #pg.draw.rect(self.game.screen, GROEN, RECT, 1)

    def update(self):
        return super().update()