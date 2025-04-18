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

teller = 1

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = pg.time.Clock()
        self.running = True
        self.gameover = False


    def load_data(self):
        self.kaart = Map('Kaart2.txt')
        self.generate_guards_from_map()

    def generate_guards_from_map(self):
        for symbool, route in self.kaart.guard_waypoints_map.items():
            if len(route) < 2:
                print(f"Guard {symbool} heeft te weinig waypoints, wordt overgeslagen.")
                continue
            start_x, start_y = route[0]
            guard = Guard(self, x=start_x, y=start_y, route=route)
            entitylijst.append(guard)
            print(f"Guard '{symbool}' toegevoegd met route: {route}")

    def new(self):
        
        self.walls = []
        entitylijst.clear()
        self.load_data()
        for row_index, row_data in enumerate(self.kaart.data):
            for col_index, tile in enumerate(row_data):
                if tile == '1':
                    wall = Wall(self, col_index, row_index)
                    self.walls.append(wall)
                    entitylijst.append(wall)
                elif tile == 'P':
                    self.player = Player(self, col_index, row_index, GEEL)
                    entitylijst.append(self.player)  # ← OK als je hem maar 1x update!


        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Eerst: speler krijgt zijn eigen update (met get_keys)
        self.player.update()

        # Vervolgens: guards en andere entiteiten
        for entity in entitylijst:
            if isinstance(entity, Guard):
                entity.update()
            elif isinstance(entity, Wall):
                entity.update()

        # Camera volgt speler
        self.camera.update(self.player)



    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

    def teken_grid(self):
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE), 1)
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y), 1)

    def draw(self):
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()
        for entity in entitylijst:
            self.screen.blit(entity.image, self.camera.apply(entity))
            if hasattr(entity, "drawvieuwfield"):
                entity.drawvieuwfield()
        pg.display.flip()

    def toon_startscherm(self):
        pass

    def game_over(self):
        G_font = pg.font.SysFont(None, 72)
        text_surface = G_font.render("GAME OVER", True, ROOD)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))

        # Restart-knop
        button_font = pg.font.SysFont(None, 48)
        button_text = button_font.render("Klik om te herstarten", True, WIT)
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))

        # Aantal pogingen weergeven
        global teller
        teller_font = pg.font.SysFont(None, 48)
        teller_text = teller_font.render(f"Aantal pogingen: {teller}", True, WIT)
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 150))
        teller += 1

        self.screen.fill(ZWART)
        self.screen.blit(text_surface, text_rect)
        pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))  # achtergrond rechthoek
        self.screen.blit(button_text, button_rect)
        self.screen.blit(teller_text, teller_rect)
        pg.display.flip()

        waiting = True
        while waiting:
            
            for event in pg.event.get():
                keys = pg.key.get_pressed()
                if keys[pg.K_ESCAPE]:
                    pg.quit()
                    exit()
                elif event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        waiting = False  # Klik op knop → herstart
                
                

    def start_game(self):
        self.new()
        self.run()


if __name__ == "__main__":
    game = Game()
    game.toon_startscherm()
    while game.running:
        game.start_game()
        if game.gameover:
            game.game_over()
            game.gameover = False
    pg.quit()