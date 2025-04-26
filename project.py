# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# Opmerking: te veel geopende tabs kunnen leiden tot performance issues en bugged guard-pathing
# Handige editor-tips:
# - Ctrl+Shift+L = meerdere selecties tegelijk aanpassen
# - Gebruik NIET de ingebouwde pg.sprite.Sprite class (eigen structuur vereist)
# - Sla bestanden op bij het aanmaken van klassen om runtime fouten zoals "not defined" te vermijden

import pygame as pg
import sys
from GameSettings import *
from entities import *
from map_en_camera import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = False
        self.gameover = False
        self.attempts = 1
        self.entities = []

    def load_data(self):
        self.kaart = Map('Kaart2.txt')
        self.load_guards('guard_routes.txt')

    def load_guards(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                route = [list(map(int, coords.split(','))) for coords in line.strip().split(';')]
                guard = Guard(self, x=route[0][0], y=route[0][1], route=route)
                self.entities.append(guard)

    def new(self):
        self.walls = []
        self.entities.clear()
        self.load_data()

        for row_idx, row in enumerate(self.kaart.data):
            for col_idx, tile in enumerate(row):
                if tile == '1':
                    wall = Wall(self, col_idx, row_idx)
                    self.walls.append(wall)
                    self.entities.append(wall)
                elif tile == 'P':
                    self.player = Player(self, col_idx, row_idx, GEEL)
                    self.entities.append(self.player)

        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update()
            self.render()

    def update(self):
        for entity in self.entities:
            entity.update()
        self.camera.update(self.player)

        for entity in self.entities:
            if isinstance(entity, Guard) and self.player.rect.colliderect(entity.rect):
                self.playing = False
                self.gameover = True
                break

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit_game()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.quit_game()

    def render(self):
        self.screen.fill(ACHTERGRONDKLEUR)
        self.draw_grid()
        for entity in self.entities:
            self.screen.blit(entity.image, self.camera.apply(entity))
            if hasattr(entity, 'drawvieuwfield'):
                entity.drawvieuwfield()
        pg.display.flip()

    def draw_grid(self):
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE))
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y))

    def game_over_screen(self):
        font_large = pg.font.SysFont(None, 72)
        font_medium = pg.font.SysFont(None, 48)

        game_over_text = font_large.render("GAME OVER", True, ROOD)
        restart_text = font_medium.render("Klik om te herstarten", True, WIT)
        attempt_text = font_medium.render(f"Aantal pogingen: {self.attempts}", True, WIT)

        game_over_rect = game_over_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))
        restart_rect = restart_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))
        attempt_rect = attempt_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 150))

        print(f"Speler gepakt door een guard! GAME OVER. {self.attempts}e poging.")

        self.screen.fill(ZWART)
        self.screen.blit(game_over_text, game_over_rect)
        pg.draw.rect(self.screen, ROOD, restart_rect.inflate(20, 20))
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(attempt_text, attempt_rect)
        pg.display.flip()

        self.wait_for_restart(restart_rect)
        self.attempts += 1

    def wait_for_restart(self, button_rect):
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()
                elif event.type == pg.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                    waiting = False

    def start_screen(self):
        pass  # Placeholder voor mogelijk startscherm

    def quit_game(self):
        pg.quit()
        sys.exit()

# Main game loop
game = Game()
game.start_screen()
while game.running:
    game.new()
    game.run()
    if game.gameover:
        game.game_over_screen()
        game.gameover = False