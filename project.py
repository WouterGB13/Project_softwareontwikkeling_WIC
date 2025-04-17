# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# heb niet te veel tabs open, game lagt hiervan en dit helpt de guard-pathing omzeep
# Tips voor elkaar:
# - Ctrl+Shift+L = meerdere selecties tegelijk bewerken
# - Gebruik NIET de ingebouwde pg.sprite.Sprite klas
# - Sla bestanden op na het aanmaken van klassen om "not defined" errors te vermijden

import pygame as pg
from GameSettings import *  # Importeer alle game instellingen
from entities import *       # Speler en muurklassen
from map_en_camera import *  # Map (tilemap) en camera logica

# Hoofdklasse van het spel
class Game:
    def __init__(self):
        # Initialiseer pygame, scherm, klok, status
        pg.init()
        # pg.mixer.init() is uitgeschakeld want geen geluid in dit project
        self.screen = pg.display.set_mode((BREEDTE,HOOGTE))  # Schermgrootte
        pg.display.set_caption(TITEL)  # Titel van spelvenster
        self.clock = pg.time.Clock()   # Tijdbeheer voor FPS
        self.running = True            # Game actief

    # Laad kaartgegevens (uit tekstbestand)
    def load_data(self):
        self.kaart = Map('Kaart2.txt')  # Laad de kaart uit een .txt-bestand

        with open("Guards.txt", 'r') as Guards:
            for Guard_var in Guards:  # Verwerk elke regel als een guard met route
                temp_route = Guard_var.strip().split(';')  # Split op ; om routepunten te isoleren
                route = []
                for pair in temp_route:
                    pair = pair.split(',')  # Split coördinaten
                    new_pair = []
                    for element in pair:
                        element = int(element)  # Zet string om naar integer
                        new_pair.append(element)
                    route.append(new_pair)  # Voeg x,y-paar toe aan route
                self.guard = Guard(self, x = route[0][0], y = route[0][1], route = route)  # Guard start op eerste punt
                entitylijst.append(self.guard)  # Voeg toe aan globale lijst van entiteiten

    def new(self):
        # Start nieuwe game-ronde, bouw level op basis van kaartdata
        self.walls = []  # Reset muurlijst
        for rij, tiles in enumerate(self.kaart.data):
            for kolom, tile in enumerate(tiles):
                if tile == '1':  # Muur-tegel
                    wall = Wall(self, kolom, rij)
                    self.walls.append(wall)
                    entitylijst.append(wall)  # Voeg toe aan globale entitylijst
                if tile == 'P':  # Spelerpositie
                    self.player = Player(self, kolom, rij, GEEL)
                    entitylijst.append(self.player)
        # Camera volgt speler, ingesteld op mapgrootte
        self.camera = Camera(self.kaart.width, self.kaart.height)

    def run(self):
        # Hoofd gameloop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000  # Delta time (tijd tussen frames)
            self.events()  # Input
            self.update()  # Logica
            self.draw()    # Beeld

    def update(self):
        # Update alle entities en camera
        for entity in entitylijst:
            entity.update()  # Voer entity-specifieke update uit
        self.camera.update(self.player)  # Camerapositie volgen

    def events(self):
        # Verwerk user input (zoals sluiten van venster)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

    def teken_grid(self):
        # Tekent hulplijnen over het scherm (voor debuggen/positionering)
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x,0) , (x,HOOGTE), 1)
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0,y) , (BREEDTE,y), 1)

    def draw(self):
        # Render het scherm
        self.screen.fill(ACHTERGRONDKLEUR)  # Achtergrondkleur
        self.teken_grid()  # Grid tekenen
        for entity in entitylijst:
            # Tekent elke entity op scherm met camera-offset toegepast
            self.screen.blit(entity.image, self.camera.apply(entity))
            if hasattr(entity, "drawvieuwfield"):  # Als entity een zichtveld heeft, teken het
                entity.drawvieuwfield()
        pg.display.flip()  # Vernieuw het scherm

    def toon_startscherm(self):
        # (Placeholder) startscherm logica
        pass

    def game_over(self):
        # (Placeholder) game over logica
        pass

# Start het spel
game = Game()
game.toon_startscherm()
while game.running:
    game.load_data()  # Laad kaart en guards
    game.new()        # Start nieuwe spelronde
    game.run()        # Voer gameloop uit
    game.game_over()  # Afhandeling na afloop game
pg.quit()  # Sluit pygame correct af