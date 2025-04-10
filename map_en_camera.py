# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# Deze file komt overeen met tilemap.py in de tutorials

import pygame as pg
from GameSettings import *

# Klasse voor het inladen van een tilemap uit een tekstbestand
class Map:
    def __init__(self, filename):
        self.data = []
        # Lees de kaartregels (bijv. muren/spelerposities) uit een tekstbestand
        with open(filename,'r') as kaart:
            for line in kaart:
                self.data.append(line.strip())  # verwijder \n aan het einde van elke regel

        # Breedte van de kaart in tegels
        self.tilewidth = len(self.data[0])
        # Hoogte van de kaart in tegels
        self.tileheight = len(self.data)
        # Totale breedte en hoogte van de map in pixels
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

# Klasse voor het volgen van een entity met de camera
class Camera:
    def __init__(self, breedte, hoogte):  # camera wordt even groot als de wereld
        self.camera = pg.Rect(0,0, breedte, hoogte)  # rechthoek die bepaalt welk deel zichtbaar is
        self.breedte = breedte
        self.hoogte = hoogte

    # Past de positie van een entity aan zodat deze correct weergegeven wordt op het scherm
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)  # verschuif entity relatief aan camera-offset

    # Update de camera om een target (zoals de speler) te volgen
    def update(self, target):
        # Houd de target gecentreerd op het scherm
        x = -target.rect.x + int(BREEDTE/2)
        y = -target.rect.y + int(HOOGTE/2)

        # Beperk camera zodat deze niet buiten de wereld beweegt
        x = min(0,x)  # links
        y = min(0,y)  # boven
        x = max(-(self.breedte - BREEDTE),x)  # rechts
        y = max(-(self.hoogte - HOOGTE),y)    # onder

        # Zet de nieuwe camera-positie
        self.camera = pg.Rect(x,y, self.breedte, self.hoogte)