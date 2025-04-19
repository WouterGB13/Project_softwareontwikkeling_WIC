# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i 
# Deze file komt overeen met tilemap.py in de tutorials
# Bevat: Map parsing en camera-tracking logica

import pygame as pg
from GameSettings import *  # Importeert scherminstellingen, TILESIZE, kleuren etc.

class Map:
    # Klasse die een tile-based kaart laadt vanaf een tekstbestand

    def __init__(self, filename: str):
        self.data: list[str] = []  # Alleen nog mapdata (de tegels)

        with open(filename, 'r') as map_file:
            for line in map_file:
                clean_line = line.strip()  # Verwijder witruimte
                self.data.append(clean_line)  # Voeg rij toe aan mapdata

        # Bereken afmetingen van de map in tegels en pixels
        if self.data:
            self.tileBREEDTE: int = len(self.data[0])  # Aantal kolommen
            self.tileHOOGTE: int = len(self.data)      # Aantal rijen
            self.BREEDTE: int = self.tileBREEDTE * TILESIZE  # Pixelbreedte
            self.HOOGTE: int = self.tileHOOGTE * TILESIZE    # Pixelhoogte
        else:
            self.tileBREEDTE = self.tileHOOGTE = self.BREEDTE = self.HOOGTE = 0

class Camera:
    # Klasse die de zichtbare viewport (camera) beheert en beweegt over de kaart

    def __init__(self, BREEDTE: int, HOOGTE: int):
        self.camera: pg.Rect = pg.Rect(0, 0, BREEDTE, HOOGTE)
        # Rechthoek die aangeeft welk deel van de wereld zichtbaar is
        self.BREEDTE: int = BREEDTE
        self.HOOGTE: int = HOOGTE

    def apply(self, entity) -> pg.Rect:
        # Verschuift een entity zodat deze relatief aan de camera getekend wordt
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Volgt het opgegeven target (bv. de speler)
        # Zorgt dat het doel in het midden van het scherm blijft

        x: int = -target.rect.x + BREEDTE // 2
        y: int = -target.rect.y + HOOGTE // 2

        # Zorg dat camera niet buiten de kaart schuift (links/boven)
        x: int = min(0, x)
        y: int = min(0, y)

        # Zorg dat camera niet buiten de kaart schuift (rechts/onder)
        x: int = max(-(self.BREEDTE - BREEDTE), x)
        y: int = max(-(self.HOOGTE - HOOGTE), y)

        # Pas camera-positie aan
        self.camera: pg.Rect = pg.Rect(x, y, self.BREEDTE, self.HOOGTE)