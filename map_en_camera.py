# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# Deze file komt overeen met tilemap.py in de tutorials

import pygame as pg
from GameSettings import *

class Map:
    def __init__(self, filename: str):
        self.data: list[str] = []
        self.guard_waypoints_map: dict[str, list[tuple[int, int]]] = {}

        with open(filename, 'r') as map_file:
            for row_idx, line in enumerate(map_file):
                clean_line = line.strip()
                self.data.append(clean_line)
                for col_idx, char in enumerate(clean_line):
                    if char.isalpha() and char.upper() != 'P':
                        if char not in self.guard_waypoints_map:
                            self.guard_waypoints_map[char] = []
                        self.guard_waypoints_map[char].append((col_idx, row_idx))
        if self.data:
            self.tileBREEDTE: int = len(self.data[0])
            self.tileHOOGTE: int = len(self.data)
            self.BREEDTE: int = self.tileBREEDTE * TILESIZE
            self.HOOGTE: int = self.tileHOOGTE * TILESIZE
        else:
            self.tileBREEDTE = self.tileHOOGTE = self.BREEDTE = self.HOOGTE = 0

class Camera:
    def __init__(self, BREEDTE: int, HOOGTE: int):
        self.camera: pg.Rect = pg.Rect(0, 0, BREEDTE, HOOGTE)
        self.BREEDTE: int = BREEDTE
        self.HOOGTE: int = HOOGTE

    def apply(self, entity) -> pg.Rect:
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x: int = -target.rect.x + BREEDTE // 2
        y: int = -target.rect.y + HOOGTE // 2
        x: int = min(0, x)
        y: int = min(0, y)
        x: int = max(-(self.BREEDTE - BREEDTE), x)
        y: int = max(-(self.HOOGTE - HOOGTE), y)
        self.camera: pg.Rect = pg.Rect(x, y, self.BREEDTE, self.HOOGTE)