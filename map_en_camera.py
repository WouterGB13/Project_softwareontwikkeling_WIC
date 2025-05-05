# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i 
# Deze file komt overeen met tilemap.py in de tutorials
# Bevat: Map parsing en camera-tracking logica

import pygame as pg
from GameSettings import *  # scherminstellingen, TILESIZE, kleuren etc.

class Map:
    """Laadt een tile-based map vanaf tekstbestand."""
    def __init__(self, filename: str):
        self.data: list[str] = []
        self.guard_waypoints_map: dict[str, list[tuple[int, int]]] = {}

        with open(filename, 'r') as map_file:
            for row_idx, line in enumerate(map_file):
                clean_line = line.strip()
                self.data.append(clean_line)

        if self.data:
            self.tileBREEDTE: int = len(self.data[0])
            self.tileHOOGTE: int = len(self.data)
            self.BREEDTE: int = self.tileBREEDTE * TILESIZE
            self.HOOGTE: int = self.tileHOOGTE * TILESIZE
        else:
            self.tileBREEDTE = self.tileHOOGTE = self.BREEDTE = self.HOOGTE = 0

class Camera:
    """Beheert zichtbare viewport die over de map beweegt."""
    def __init__(self, width: int, height: int):
        self.camera: pg.Rect = pg.Rect(0, 0, width, height)
        self.width: int = width
        self.height: int = height

    def apply(self, entity) -> pg.Rect:
        """Verschuift entity-positie relatief aan camera."""
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        """Camera volgt het opgegeven target (bv. speler)."""
        x: int = -target.rect.centerx + BREEDTE // 2
        y: int = -target.rect.centery + HOOGTE // 2

        # Limiteer camera binnen map-bounds
        x = min(0, x)  # links
        y = min(0, y)  # boven
        x = max(-(self.width - BREEDTE), x)  # rechts
        y = max(-(self.height - HOOGTE), y)  # onder

        self.camera = pg.Rect(x, y, self.width, self.height)