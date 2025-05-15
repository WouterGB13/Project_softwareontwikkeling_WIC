# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i  
# Deze file komt overeen met tilemap.py in de tutorials
# Bevat: Map parsing en camera-tracking logica

import pygame as pg  # Importeer de pygame bibliotheek en geef het de alias pg
from GameSettings import *  # Importeer alle instellingen zoals schermgrootte, TILESIZE, kleuren, etc.

class Map:
    """Laadt een tile-based map vanaf tekstbestand."""
    def __init__(self, filename: str):
        self.data = []  # Maak een lege lijst aan om de kaartdata in op te slaan

        with open(filename, 'r') as map_file:  # Open het bestand met de naam filename in leesmodus
            for row_idx, line in enumerate(map_file):  # Loop door elke regel in het bestand met index
                clean_line = line.strip()  # Verwijder spaties en nieuwe regels aan begin en einde van de lijn
                self.data.append(clean_line)  # Voeg de schone lijn toe aan de data lijst, zo ontstaat een lijst van strings per rij

        self.tileBREEDTE = len(self.data[0])  # Bepaal de breedte van de map in tiles door de lengte van de eerste rij te nemen
        self.tileHOOGTE = len(self.data)  # Bepaal de hoogte van de map in tiles door het aantal regels te tellen
        self.BREEDTE = self.tileBREEDTE * TILESIZE  # Bereken de totale breedte in pixels (tiles * tilegrootte)
        self.HOOGTE = self.tileHOOGTE * TILESIZE  # Bereken de totale hoogte in pixels (tiles * tilegrootte)

class Camera:
    """Beheert zichtbare gebied dat over de map beweegt."""
    def __init__(self, width: int, height: int):
        self.camera = pg.Rect(0, 0, width, height)  # Maak een pygame rechthoek aan die de camera vertegenwoordigt, start op (0,0)
        self.width = width  # Bewaar de breedte van de map (in pixels)
        self.height = height  # Bewaar de hoogte van de map (in pixels)

    def apply(self, entity) -> pg.Rect:
        """Verschuift entity-positie relatief aan camera."""
        return entity.rect.move(self.camera.topleft)  
        # Verplaats de positie van de entity door de camera offset toe te passen en geef de nieuwe rect terug

    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        """Verschuift een willekeurige rect (zoals voor tekst) relatief aan camera."""
        return rect.move(self.camera.topleft)  
        # Zelfde als apply, maar dan voor een losse rect in plaats van een entity

    def return_shift_of_screen(self):  
        # Geeft een tuple terug die laat zien hoe ver het grid relatief is verschoven door de camera (voor grid-tekening)
        return int(self.camera.x - BREEDTE/2) % TILESIZE, int(self.camera.y - HOOGTE/2) % TILESIZE  
        # Bereken de x en y offset van de camera ten opzichte van het midden van het scherm, modulo TILESIZE zodat het binnen een tile blijft

    def update(self, target):
        """Camera volgt het opgegeven target (bv. speler)."""
        x = -target.rect.centerx + BREEDTE // 2  
        # Bereken nieuwe x-positie voor de camera zodat target gecentreerd is (negatief want we verplaatsen wereld t.o.v. camera)
        y = -target.rect.centery + HOOGTE // 2  
        # Bereken nieuwe y-positie voor de camera, idem als hierboven

        # Limiteer camera binnen map-bounds zodat hij niet buiten de kaart beweegt
        x = min(0, x)  # Zorg dat de camera niet voorbij de linkerkant van de map gaat
        y = min(0, y)  # Zorg dat de camera niet voorbij de bovenkant van de map gaat
        x = max(-(self.width - BREEDTE), x)  # Zorg dat de camera niet voorbij de rechterkant van de map gaat
        y = max(-(self.height - HOOGTE), y)  # Zorg dat de camera niet voorbij de onderkant van de map gaat

        self.camera = pg.Rect(x, y, self.width, self.height)  
        # Update de camera rect met de nieuwe positie en behoud de originele grootte