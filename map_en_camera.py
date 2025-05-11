# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i 
# Deze file komt overeen met tilemap.py in de tutorials
# Bevat: Map parsing en camera-tracking logica

import pygame as pg
from GameSettings import *  # scherminstellingen, TILESIZE, kleuren etc.

class Map:
    """Laadt een tile-based map vanaf tekstbestand."""
    def __init__(self, filename: str):
        self.data = []

        with open(filename, 'r') as map_file:
            for row_idx, line in enumerate(map_file):
                clean_line = line.strip()
                self.data.append(clean_line) #maak een lijst uit txt file die verwerkt kan worden tot correcte entities

        self.tileBREEDTE = len(self.data[0]) #bepaal breedte map (in tiles)
        self.tileHOOGTE = len(self.data) #idem hoogte
        self.BREEDTE = self.tileBREEDTE * TILESIZE #pixels
        self.HOOGTE = self.tileHOOGTE * TILESIZE

class Camera:
    """Beheert zichtbare gebied dat over de map beweegt."""
    def __init__(self, width: int, height: int):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity) -> pg.Rect:
        """Verschuift entity-positie relatief aan camera."""
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        """Verschuift een willekeurige rect (zoals voor tekst) relatief aan camera."""
        return rect.move(self.camera.topleft)
    
    def return_shift_of_screen(self): #specifiek om grid te laten bewegen (dus de funky shit dat je hier ziet kan door de draw_grid functie deels verklaard worden)
        return int(self.camera.x - BREEDTE/2)%TILESIZE, int(self.camera.y - HOOGTE/2)%TILESIZE #modulo door TILESIZE want we willen ons grid niet uit ons scherm laden en vanaf dat we een tile verder zijn moet deze offset zich reseten


    def update(self, target):
        """Camera volgt het opgegeven target (bv. speler)."""
        x = -target.rect.centerx + BREEDTE // 2
        y = -target.rect.centery + HOOGTE // 2

        # Limiteer camera binnen map-bounds
        x = min(0, x)  # links
        y = min(0, y)  # boven
        x = max(-(self.width - BREEDTE), x)  # rechts
        y = max(-(self.height - HOOGTE), y)  # onder

        self.camera = pg.Rect(x, y, self.width, self.height)