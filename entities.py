import pygame as pg
from GameSettings import *
import math

entitylijst = []

def returnfirstelement(lijst):
        return lijst[0]

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

class Player1(Player): #nieuwe class om het collisionprobleem op te lossen
    def __init__(self,game,x,y, kleur):
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

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.inforce_collision()
        self.rect.x = self.x
        self.rect.y = self.y


    def inforce_collision(self): #uitgebreide versie
        for wall in self.game.walls:
            player_center = (self.x + self.rect.width/2, self.y + self.rect.height/2)
            muur_center = (wall.rect.x + TILESIZE/2, wall.rect.y + TILESIZE/2)
            if self.x + self.rect.width > wall.rect.x and self.x < wall.rect.x + TILESIZE and self.y + self.rect.height > wall.rect.y and self.y < wall.rect.y + TILESIZE:
                dx = (player_center[0] - muur_center[0])
                dy = (player_center[1] - muur_center[1])
                if abs(dx) < abs(dy): #de botsing gebeurt via boven/onder
                    if dy > 0: #botsing via onder
                        self.y = wall.rect.bottom
                    else:
                        self.y = wall.rect.top - self.rect.height
                else:
                    if dx > 0: #player.x > wall.x => via rechts
                        self.x = wall.rect.right
                    else:
                        self.x = wall.rect.left - self.rect.width
    


#Door de manier waarop de game de muren afgaat bij het checken van collisions kan het zijn dat bij gebruik van Player1, je blokje stopt met het
#langs-een-muur-glijden wanneer je naar de pixel op (0,0) beweegt. Dit is omdat die blokjes eerst worden ingeladen en op sommige momenten bij
#een collision de game denkt dat je recht op de hoek van een muur zit. (De game weet niet dat we langs een muur aan het glijden zijn)
#Hierdoor wordt het blokje gewoon tegengehouden (soort van) en stopt de vlotte beweging.

#Player2 lost dit op door eerst te gaan kijken naar de collision met de dichtsbijzijnde muur.
class Player2(Player1):
    def __init__(self,game,x,y, kleur):
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

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.inforce_collision()
        self.rect.x = self.x
        self.rect.y = self.y

    def inforce_collision(self):
        prioritized_collisions = self.priority_collisions()
        for wall in prioritized_collisions:
            if self.x + self.rect.width > wall.rect.x and self.x < wall.rect.x + TILESIZE and self.y + self.rect.height > wall.rect.y and self.y < wall.rect.y + TILESIZE:
                player_center = (self.x + self.rect.width/2, self.y + self.rect.height/2)
                muur_center = (wall.rect.x + TILESIZE/2, wall.rect.y + TILESIZE/2)
                dx = (player_center[0] - muur_center[0])
                dy = (player_center[1] - muur_center[1])
                if abs(dx) < abs(dy): #de botsing gebeurt via boven/onder
                    if dy > 0: #botsing via onder
                        self.y = wall.rect.bottom
                    else:
                        self.y = wall.rect.top - self.rect.height
                else:
                    if dx > 0: #player.x > wall.x => via rechts
                        self.x = wall.rect.right
                    else:
                        self.x = wall.rect.left - self.rect.width

    def object_collision(self):
        collisionlist = []
        for wall in self.game.walls:
            if self.x + self.rect.width > wall.rect.x and self.x < wall.rect.x + TILESIZE and self.y + self.rect.height > wall.rect.y and self.y < wall.rect.y + TILESIZE:
                collisionlist.append(wall)
        return collisionlist

    def priority_collisions(self):
        collisions_list = self.object_collision()
        collisions_distances = []
        for wall in collisions_list:
            player_center = (self.x + self.rect.width/2, self.y + self.rect.height/2)
            muur_center = (wall.rect.x + TILESIZE/2, wall.rect.y + TILESIZE/2)
            afstand = math.sqrt((player_center[0] - muur_center[0])**2 + (player_center[1] - muur_center[1])**2)
            collisions_distances.append([afstand, wall])
        collisions_distances.sort(key=returnfirstelement) #sorteert de lijst (van laag naar hoog) op basis van het eerste element van elke sublijst (=de afstand tot de muur waarmee de player botst)
        
        return [x[1] for x in collisions_distances]

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