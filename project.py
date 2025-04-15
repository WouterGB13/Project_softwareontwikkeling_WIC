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
        # Start game window, klok, display
        pg.init()
        # pg.mixer.init() is uitgeschakeld want geen geluid in dit project
        self.screen = pg.display.set_mode((BREEDTE,HOOGTE))  # Schermgrootte
        pg.display.set_caption(TITEL)  # Titel van spelvenster
        self.clock = pg.time.Clock()   # Tijdbeheer voor FPS
        self.running = True            # Game actief

    # Laad kaartgegevens (uit tekstbestand)
    def load_data(self):
        self.kaart = Map('Github-shit\Project_softwareontwikkeling_WIC\Kaart2.txt')

        with open("Github-shit\Project_softwareontwikkeling_WIC\Guards.txt", 'r') as Guards:
            for Guard_var in Guards: #guard_var om te onderscheiden van de class maar leesbaarheid te behouden
                temp_route = Guard_var.strip().split(';') #verwijder onzichtbare endline karakters en split in coordinatenparen (strings)
                route = []
                for pair in temp_route: #coordinaten omzetten van string naar x,y-paren
                    pair = pair.split(',') #x en y-coordinaat van elkaar scheiden (nu 2 strings die bestaan uit 1 nummer elk)
                    new_pair = []
                    for element in pair:
                        element = int(element) #string omzetten in integer om samen te voegen als bruikbaar coordinatenpaar
                        new_pair.append(element)
                    route.append(new_pair) #voeg niet-string coordinatenset toe aan route
                self.guard = Guard(self, x = route[0][0], y = route[0][1], route = route) #maak guard aan met gegenereerde route
                entitylijst.append(self.guard) #registreer guard als bestaande entity

    def new(self):
        # Start nieuwe game-ronde
        self.walls = []  # Reset muurlijst
        # Loop door elke rij en tegel in de kaart
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
            entity.update() #inhoud van .update() is niet universeel
        self.camera.update(self.player)  # Camerapositie gelijkstellen aan spelerpositie

    def events(self):
        # Verwerk user input (zoals sluiten van venster)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

    def teken_grid(self):
        # Tekent hulplijnen over het scherm
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
    game.load_data()
    game.new()
    game.run()
    game.game_over()
pg.quit()  # Sluit pygame correct af
