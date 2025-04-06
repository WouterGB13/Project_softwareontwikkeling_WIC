import pygame as pg
from GameSettings import *
import math

entitylijst = []

#maak hier entity classes
class Player():
    def __init__(self,game,x,y, kleur): #gebruik relatieve posities zodat de player altijd binnen squares blijft
        self.game = game
        self.x = x * TILESIZE # *TILESIZE om op juiste plek te spawnen
        self.y = y * TILESIZE
        self.breedte = TILESIZE
        self.hoogte = TILESIZE
        self.vx = 0
        self.vy = 0
        self.kleur = kleur

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys  = pg.key.get_pressed()
        if keys[pg.K_q] or keys[pg.K_LEFT]:
            self.vx = -SPELER_SNELHEID
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vx = SPELER_SNELHEID
        if keys[pg.K_z] or keys[pg.K_UP]:
            self.vy = -SPELER_SNELHEID
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vy = SPELER_SNELHEID
        if self.vx != 0 and self.vy != 0: #normaliseren van diagonale beweging
            self.vy *= math.sqrt(2)/2
            self.vx *= math.sqrt(2)/2
    
    def object_collision(self):
        collisionlist = []
        for wall in self.game.walls:
            if (self.x + self.breedte > wall.rect_x and self.x < wall.rect_x + TILESIZE and self.y + self.hoogte > wall.rect_y and self.y < wall.rect_y + TILESIZE):
                collisionlist.append(wall)
        return collisionlist

    def collide_with_walls(self, dir):
        hits = self.object_collision()
        if dir == 'x':
            for hit in hits:
                if self.vx > 0:
                    self.x = hit.rect_x - self.breedte
                if self.vx < 0:
                    self.x = hit.rect_x + TILESIZE
                self.vx = 0
                self.rect_x = self.x
        if dir == 'y':
            for hit in hits:
                if self.vy > 0:
                    self.y = hit.rect_y - self.hoogte
                if self.vy < 0:
                    self.y = hit.rect_y + TILESIZE
                self.vy = 0
                self.rect_y = self.y

    def update(self):
        self.get_keys()
        self.x_hitbox = (int(self.x), int(self.x + self.breedte)) 
        self.y_hitbox = (int(self.y), int(self.y + self.hoogte))
        self.x += self.vx * self.game.dt
        self.rect_x = self.x
        self.collide_with_walls('x')
        self.y += self.vy * self.game.dt
        self.rect_y = self.y
        self.collide_with_walls('y')
        
    #zelf tekenen is nodig omdat we geen sprite super-class mogen gebruiken    
    def draw(self): #uiteindelijk universeel maken, geraak er momenteel niet aan uit -W
        pg.draw.rect(self.game.screen, self.kleur,(self.rect_x,self.rect_y,self.breedte,self.hoogte)) 

class Wall():
    def __init__(self, game, x, y): #geen kleurargument want alle muren zullen zelfde kleur hebben (in basic versie toch)
        self.game = game
        self.kleur = GROEN
        self.x = x #relatieve waarde pas op
        self.rect_x = x*TILESIZE #absolute waarde
        self.y = y
        self.rect_y = y*TILESIZE
        self.x_hitbox = (self.rect_x,self.rect_x+TILESIZE)
        self.y_hitbox = (self.rect_y,self.rect_y+TILESIZE)

    def update(self):
        pass
    
    def draw(self): #uiteindelijk universeel maken, geraak er momenteel niet aan uit -W
        pg.draw.rect(self.game.screen, self.kleur,(self.rect_x,self.rect_y,TILESIZE,TILESIZE))