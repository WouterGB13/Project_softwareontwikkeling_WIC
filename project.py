# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# heb niet te veel tabs open, game lagt hiervan en dit helpt de guard-pathing omzeep
# Tips voor elkaar:
# - Ctrl+Shift+L = meerdere selecties tegelijk bewerken
# - Gebruik NIET de ingebouwde pg.sprite.Sprite klas
# - Sla bestanden op na het aanmaken van klassen om "not defined" errors te vermijden

import pygame as pg
from GameSettings import *
from entities import *
from map_en_camera import *

class Game:
    # Hoofdklasse voor het spel.  Handelt initialisatie, spel-lus en het laden van gegevens af

    def __init__(self):
        # Pygame, scherm, klok en game-status initialiseren
        pg.init()
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = pg.time.Clock()
        self.running = True

    def load_data(self):
        # Kaartgegevens en guard-paths uit bestanden laden
        self.kaart = Map('Kaart2.txt')
        self.load_guard_paths("Guards.txt")

    def load_guard_paths(self, filename):
        # guard-paths laden uit het opgegeven bestand
        with open(filename, 'r') as guards_file:
            for guard_data in guards_file:
                route = self.parse_guard_route(guard_data)
                guard = Guard(self, x=route[0][0], y=route[0][1], route=route)
                entitylijst.append(guard)

    def parse_guard_route(self, guard_data):
        # Omzetting van een guard routestring in een lijst van coördinaatparen
        route = []
        temp_route = guard_data.strip().split(';')
        for pair_str in temp_route:
            coords = pair_str.split(',')
            try:
                x, y = int(coords[0]), int(coords[1])
                route.append([x, y])
            except (ValueError, IndexError) as e:
                print(f"Error parsing coordinates: {pair_str}.  Skipping. Error: {e}")
                continue  # Skip foute coordinatenparen
        return route

    def new(self):
        # Start een nieuwe spelronde
        self.walls = []
        entitylijst.clear()  # Verwijder de entity list aan het begin van een nieuw spel
        for row_index, row_data in enumerate(self.kaart.data):
            for col_index, tile in enumerate(row_data):
                if tile == '1':
                    wall = Wall(self, col_index, row_index)
                    self.walls.append(wall)
                    entitylijst.append(wall)
                elif tile == 'P':
                    self.player = Player(self, col_index, row_index, GEEL)
                    entitylijst.append(self.player)

        # Laad guards na clearing de entity list
        self.load_data()

        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)

    def run(self):
        # Main game loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Update alle entities en de camera
        for entity in entitylijst:
            entity.update()
        self.camera.update(self.player)

    def events(self):
        # User input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

    def teken_grid(self):
        # Teken een grid (voor debugging)
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE), 1)
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y), 1)

    def draw(self):
        # Render het scherm
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()
        for entity in entitylijst:
            self.screen.blit(entity.image, self.camera.apply(entity))
            if hasattr(entity, "drawvieuwfield"):
                entity.drawvieuwfield()
        pg.display.flip()

    def toon_startscherm(self):
        # startschermlogica
        pass

    def game_over(self):
        # game-over
        pass

    def start_game(self):
        # hoofdlus van het spel starten
        self.load_data()
        self.new()
        self.run()

# Entry point of the game
if __name__ == "__main__":
    game = Game()
    game.toon_startscherm()
    while game.running:
        game.start_game()
        game.game_over()
    pg.quit()