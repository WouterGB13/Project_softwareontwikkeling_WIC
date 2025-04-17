# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i 
# Deze file komt overeen met tilemap.py in de tutorials

import pygame as pg
from GameSettings import *

class Map:
    # Verwerkt map data en dimensions

    def __init__(self, filename: str):
        """
        Initialiseert het Kaartobject

        Args:
            filename: Het pad naar het tekstbestand van de kaart
        """
        self.data: list[str] = []
        with open(filename, 'r') as map_file:
            for line in map_file:
                self.data.append(line.strip())

        self.tileBREEDTE: int = len(self.data[0])
        self.tileHOOGTE: int = len(self.data)
        self.BREEDTE: int = self.tileBREEDTE * TILESIZE
        self.HOOGTE: int = self.tileHOOGTE * TILESIZE

class Camera:
    # Verwerkt camerabeweging en past offsets toe op entiteiten

    def __init__(self, BREEDTE: int, HOOGTE: int):
        """
        Initialiseert het object Camera

        Args:
            BREEDTE: De breedte van de kaart in pixels.
            HOOGTE: De hoogte van de kaart in pixels.
        """
        self.camera: pg.Rect = pg.Rect(0, 0, BREEDTE, HOOGTE)
        self.BREEDTE: int = BREEDTE
        self.HOOGTE: int = HOOGTE

    def apply(self, entity: pg.sprite.Sprite) -> pg.Rect:
        """
        Past de camera-offset toe op de rechthoek van een entiteit.

        Args:
            entity: De entiteit om de offset op toe te passen.

        Returns:
            Een nieuw Rect object dat de positie van de entiteit op het scherm weergeeft.
        """
        return entity.rect.move(self.camera.topleft)

    def update(self, target: pg.sprite.Sprite):
        """
        Werkt de camerapositie bij om de doelentiteit te volgen.

        Args:
            Doel: De entiteit die gevolgd moet worden (bijv. de speler).
        """
        x: int = -target.rect.x + BREEDTE // 2
        y: int = -target.rect.y + HOOGTE // 2

        # Beperk camerabeweging om binnen de grenzen van de kaart te blijven
        x: int = min(0, x)
        y: int = min(0, y)
        x: int = max(-(self.BREEDTE - BREEDTE), x)
        y: int = max(-(self.HOOGTE - HOOGTE), y)

        self.camera: pg.Rect = pg.Rect(x, y, self.BREEDTE, self.HOOGTE)