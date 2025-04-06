import pygame as pg
from GameSettings import *
import math

entitylijst = []

#maak hier entity classes
class Player():
    def __init__(self,game,x,y, kleur): #gebruik relatieve posities zodat de player altijd binnen squares blijft
        self.game = game
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(kleur)
        self.vx = 0
        self.vy = 0
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE # *TILESIZE om op juiste plek te spawnen
        self.y = y * TILESIZE

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
            if (self.x + self.rect.width > wall.rect.x and self.x < wall.rect.x + TILESIZE and self.y + self.rect.height > wall.rect.y and self.y < wall.rect.y + TILESIZE):
                collisionlist.append(wall)
        return collisionlist

    def collide_with_walls(self, dir):
        hits = self.object_collision()
        if dir == 'x':
            for hit in hits:
                if self.vx > 0:
                    self.x = hit.rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hit.rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            for hit in hits:
                if self.vy > 0:
                    self.y = hit.rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hit.rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

class Wall():
    def __init__(self, game, x, y): #geen kleurargument want alle muren zullen zelfde kleur hebben (in basic versie toch)
        self.game = game
        self.kleur = GROEN
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(self.kleur)
        self.rect = self.image.get_rect()
        self.x = x #relatieve waarde pas op
        self.y = y
        self.rect.x = x*TILESIZE
        self.rect.y = y*TILESIZE
        
    def update(self):
        pass