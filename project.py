# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# Opmerking: te veel geopende tabs kunnen leiden tot performance issues en bugged guard-pathing
# Handige editor-tips:
# - Ctrl+Shift+L = meerdere selecties tegelijk aanpassen
# - Gebruik NIET de ingebouwde pg.sprite.Sprite class (eigen structuur vereist)
# - Sla bestanden op bij het aanmaken van klassen om runtime fouten zoals "not defined" te vermijden

import pygame as pg
from GameSettings import *  # schermgrootte, kleuren etc.
from entities import *       # Wall, Player, Guard, etc.
from map_en_camera import *  # Map en Camera klassen

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = pg.time.Clock()
        self.running = True
        self.gameover = False
        self.playing = False
        self.entitylijst = []
        self.teller = 0
        self.button_rect = None  # Voor herstartknop tijdens Game Over scherm

    def load_data(self):
        self.kaart = Map('Kaart2.txt')
        self.guard_routes = []

        with open("guard_routes.txt", 'r') as Guards:
            for line in Guards:
                temp_route = [list(map(int, pair.split(','))) for pair in line.strip().split(';')]
                self.guard_routes.append(temp_route)

    def new(self):
        self.entitylijst.clear()
        self.walls = []
        self.load_data()

        for row_idx, row in enumerate(self.kaart.data):
            for col_idx, tile in enumerate(row):
                if tile == '1':
                    wall = Wall(self, col_idx, row_idx)
                    self.walls.append(wall)
                    self.entitylijst.append(wall)
                elif tile == 'P':
                    self.player = Player(self, col_idx, row_idx, GEEL)
                    self.entitylijst.append(self.player)

        # Voeg guards toe
        for route in self.guard_routes:
            guard = Guard(self, x=route[0][0], y=route[0][1], route=route)
            self.entitylijst.append(guard)

        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)

    def run(self):
        self.new()
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            if self.gameover:
                self.draw_game_over_screen()
            else:
                self.update()
                self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN and self.gameover and self.button_rect:
                if self.button_rect.collidepoint(event.pos):
                    self.reset_game()

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            pg.quit()
            exit()

    def update(self):
        for entity in self.entitylijst:
            entity.update()

        # Botsingcontrole speler versus guards
        for entity in self.entitylijst:
            if isinstance(entity, Guard):
                if self.player.rect.colliderect(entity.rect):
                    self.gameover = True
                    self.teller += 1
                    print(f"Speler gepakt door guard! GAME OVER. {self.teller}e poging.")

        self.camera.update(self.player)

    def draw(self):
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()

        for entity in self.entitylijst:
            self.screen.blit(entity.image, self.camera.apply(entity))
            if hasattr(entity, 'drawvieuwfield'):
                entity.drawvieuwfield()

        pg.display.flip()

    def teken_grid(self):
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE))
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y))

    def reset_game(self):
        self.gameover = False
        self.new()

    def draw_game_over_screen(self):
        self.screen.fill(ZWART)

        font_large = pg.font.SysFont(None, 72)
        text_surface = font_large.render("GAME OVER", True, ROOD)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))
        self.screen.blit(text_surface, text_rect)

        font_button = pg.font.SysFont(None, 48)
        button_text = font_button.render("Klik om te herstarten", True, WIT)
        self.button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))
        pg.draw.rect(self.screen, ROOD, self.button_rect.inflate(20, 20))
        self.screen.blit(button_text, self.button_rect)

        font_teller = pg.font.SysFont(None, 45)
        teller_text = font_teller.render(f"Aantal pogingen: {self.teller}", True, WIT)
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 150))
        self.screen.blit(teller_text, teller_rect)

        pg.display.flip()

# Startpunt
if __name__ == "__main__":
    game = Game()
    game.toon_startscherm()
    while game.running:
        game.run()
    pg.quit()