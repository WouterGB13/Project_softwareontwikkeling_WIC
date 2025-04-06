#gevolgde tutotials via https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
#deze file komt overeen met tilemap.py in de tutorials

import pygame as pg
from GameSettings import *

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename,'r') as kaart: #text file met map-data (muren etc)
            for line in kaart:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0]) #aantal rijen
        self.tileheight = len(self.data) #aantal kolommen
        self.width = self.tilewidth * TILESIZE #absolute afmetingen
        self.height = self.tileheight * TILESIZE

class Camera:
    def __init__(self, breedte, hoogte): #afmetingen van camera
        self.camera = pg.Rect(0,0, breedte, hoogte)
        self.breedte = breedte
        self.hoogte = hoogte

    def apply(self, entity): # in theorie can camera ook vastgemaakt worden aan eender welke andere entity buiten de speler
        return entity.rect.move(self.camera.topleft)
    
    def update(self, target): #bepaalde sprite laten volgen
        x = -target.rect.x + int(BREEDTE/2) #speler gecentreerd houden op scherm
        y = -target.rect.y + int(HOOGTE/2)

        x = min(0,x)
        y = min(0,y)
        x = max(-(self.breedte - BREEDTE),x)
        y = max(-(self.hoogte-HOOGTE),y)

        self.camera = pg.Rect(x,y, self.breedte, self.hoogte)