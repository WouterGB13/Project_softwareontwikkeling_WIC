import pygame as pg
from GameSettings import *
import math

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
        collisionlist = []
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                collisionlist.append(wall)
        return collisionlist

    # Corrigeer positie als er een botsing is in een bepaalde richting
    def collide_with_walls(self, dir):
        hits = self.object_collision()
        for wall in hits:
            if dir == 'x':
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

class Guard():
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
        print(start, end,self.vx,self.vy)

    # Wordt op dit moment niet gebruikt, maar kan later uitgebreid worden
    def update(self):
        if not ((self.next_pos[0]*TILESIZE - 3 <=self.x <= self.next_pos[0]*TILESIZE + 3) and (self.next_pos[1]*TILESIZE - 3 <=self.y <= self.next_pos[1]*TILESIZE + 3)): #wanneer niet binnen bepaalde marge van doel, navigeer naar doel
            self.navigate(self.current_route_pos,self.next_pos)
            print(self.x,self.next_pos[0]*TILESIZE,self.y, self.next_pos[1]*TILESIZE )
        else:
            self.vx = 0
            self.x = self.next_pos[0]*TILESIZE
            self.vy = 0
            self.y = self.next_pos[1]*TILESIZE
        self.x += self.vx * self.game.dt
        self.rect.x = self.x
        self.y += self.vy * self.game.dt
        self.rect.y = self.y