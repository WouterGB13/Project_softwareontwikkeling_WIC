# --- Algemene Info ---
# Tutorials gevolgd via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# Let op: teveel open tabs kunnen zorgen voor laggy guards en slechte performance.
# Editor tips:
# - Ctrl+Shift+L: Meerdere regels tegelijk selecteren
# - Gebruik GEEN pg.sprite.Sprite (eigen structuur vereist)
# - Save je bestanden na maken van nieuwe klassen!

# --- Imports ---
import pygame as pg
from GameSettings import *  # Instellingen zoals breedte, hoogte, FPS, kleuren
from entities import *      # Klassen zoals Wall, Player, Guard
from map_en_camera import * # Map (levelstructuur) en Camera functionaliteit
import random


class Game:
    """De hoofdklasse die alles beheert: speler, guards, levels en events."""

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = self.create_clock()
        self.running = True
        self.gameover = False
        self.entities = []      # Alle objecten (walls, player, guards)
        self.teller = 0          # Aantal keren dat speler game over ging
        self.score = 0              #aantal punten momenteel in bezit van speler
        self.button_rect = None  # Voor resetknop na game over
        self.gameover_screen_drawn = False
        self.exit_screen = False  # Voeg een flag toe om te controleren wanneer het exit-scherm zichtbaar is
        self.active_points = 0

    def create_clock(self):
        """Maakt de klok aan voor FPS control."""
        return pg.time.Clock()

    def load_data(self):
        """Laad de kaart en de routes van de guards."""
        self.kaart = Map('p_gebouwen.txt')  # Laad map layout uit tekstbestand
        self.dumb_guard_routes = []
        self.smart_guard_routes = []

        with open("guard_routes.txt", 'r') as Guards:
            for line in Guards:
                temp_route = [list(map(int, pair.split(','))) for pair in line.strip().split(';')]
                if temp_route[0][0] == 1:
                    temp_route[0].pop(0)
                    self.smart_guard_routes.append(temp_route)
                if temp_route[0][0] == 0:   
                    temp_route[0].pop(0)
                    self.dumb_guard_routes.append(temp_route)

    def new(self):
        """Start een nieuw spel: reset entiteiten en laad alles."""
        self.entities.clear()
        self.walls = []
        self.possible_score_pos = []
        self.score = 0
        self.load_data()
        self.exits = []  # Voeg toe in __init__ of new()

        # Maak objecten aan volgens de kaartdata
        for row_idx, row in enumerate(self.kaart.data):
            for col_idx, tile in enumerate(row):
                if tile == '1':
                    wall = Wall(self, (col_idx, row_idx))
                    self.walls.append(wall)
                elif tile == 'P':
                    self.player = Player(self, (col_idx, row_idx), GEEL)
                    self.startpos = vec(col_idx*TILESIZE, row_idx*TILESIZE)
                    self.entities.append(self.player)
                elif tile == "C":
                    print(f"kolom {col_idx}, rij {row_idx}")
                elif tile == "E":
                    exit_tile = Exit(self, (col_idx, row_idx))
                    self.exits.append(exit_tile)
                elif tile == "S":
                    self.possible_score_pos.append((col_idx,row_idx))
                elif tile == "B":
                    self.bag = Bag(self,(col_idx,row_idx))
                    self.entities.append(self.bag)

        # Plaats guards met hun patrouille-routes
        for route in self.dumb_guard_routes:
            guard = Domme_Guard(self, (route[0][0], route[0][1]), route)
            self.entities.append(guard)

        for route in self.smart_guard_routes:
            guard = Slimme_Guard(self, (route[0][0], route[0][1]), route)
            self.entities.append(guard)

        for i in range(AANTAL_PUNTEN):
            pos = random.choice(self.possible_score_pos)
            punt = Score(self,pos)
            self.possible_score_pos.remove(pos)
            self.entities.append(punt)
            

        # Installeer de camera om mee te bewegen met de speler
        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)

    def run(self):
        """Hoofdloop: verwerkt input, updates en tekent frames."""
        self.new()
        self.escape()
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000  # Delta time voor vloeiende beweging
            self.handle_events()

            if self.gameover:
                if not self.gameover_screen_drawn:
                    self.draw_game_over_screen()
                    self.gameover_screen_drawn = True
            elif self.exit_screen:
                self.draw_exit_screen()  # Toon het exit-scherm
            else:
                self.update()
                self.draw()

    def handle_events(self):
        """Vangt alle gebruikersinput op: toetsenbord, muis, afsluiten."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
                pg.quit()
                exit()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False
                    self.running = False
                    pg.quit()
                    exit()

                if self.exit_screen:
                    self.exit_screen = False
                    self.toon_startscherm()
                elif self.gameover:
                    self.reset_game()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.gameover and self.button_rect and self.button_rect.collidepoint(event.pos):
                    self.reset_game()

    def escape(self):
        """Verwerkt Escape-toets en sluiten via vensterkruisje (universeel toepasbaar)."""
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                self.playing = False
                pg.quit()
                exit()

    def update(self):
        """Update alle objecten en check botsingen."""
        for entity in self.entities:
            entity.update()
            if isinstance(entity, Guard):
                if self.player.rect.colliderect(entity.rect):
                    self.player.pos = self.startpos
                    self.score = 0
                    for entity in self.entities:
                        if isinstance(entity, Guard):
                            entity.reset()
                    self.player.lives -= 1
                    if self.player.lives == 0:
                        self.gameover = True
                        self.teller += 1
                        print(f"Speler gepakt door guard! GAME OVER. {self.teller}e poging.") #VRAAG 3: doen we print weg?
        
        for exit_tile in self.exits:
            if self.player.rect.colliderect(exit_tile.rect):
                if not self.gameover:
                    print("speler heeft de uitgang bereikt")
                    self.exit_screen = True
                    break

        # Update camera positie gebaseerd op speler
        self.camera.update(self.player)

    def draw_score(self):
        scorefont = pg.font.SysFont(None,32)
        score_display = scorefont.render(f"{self.score}",True,WIT)
        score_rect = score_display.get_rect(center=(BREEDTE - 16, 16))
        self.screen.blit(score_display, score_rect)

    def draw(self):
        """Teken alle game-elementen op het scherm."""
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()

        for entity in self.entities:
            self.screen.blit(entity.image, self.camera.apply(entity))
            if isinstance(entity, Guard):
                entity.draw_view_field()  # Teken zichtveld van guards

        for wall in self.walls:
            self.screen.blit(wall.image, self.camera.apply(wall))

        for exit in self.exits:
            self.screen.blit(exit.image, self.camera.apply(exit))


            if isinstance(entity, Exit):
                entity.draw(self.screen, self.camera)
        self.draw_lives()
        self.draw_score()
        pg.display.flip()

    def teken_grid(self):
        """Teken raster op de achtergrond voor visuele referentie."""
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE))
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y))

    def reset_game(self):
        """Reset het spel na Game Over of Exit en start een volledig nieuw spel."""
        self.gameover = False
        self.gameover_screen_drawn = False
        self.exit_screen = False  # Reset het exit-scherm vlag
        self.new()  # Start een nieuw spel

    def toon_startscherm(self):
        """Toont het startscherm vóór het spel begint met een knop om te starten."""
        font_title = pg.font.SysFont(None, 72)
        font_button = pg.font.SysFont(None, 48)

        # ⛓️ Gesplitste titel
        title_lines = ["METAL GEAR SOLID V(UB):", "THE PHANTOM KATER"]
        title_surfs = [font_title.render(line, True, WIT) for line in title_lines]
        
        # Y-coördinaat startpositie
        start_y = HOOGTE // 2 - 140
        title_rects = [
            surf.get_rect(center=(BREEDTE // 2, start_y + i * 80))
            for i, surf in enumerate(title_surfs)
        ]

        # Startknop
        button_text = font_button.render("Klik om te starten", True, WIT)
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 80))

        wachten = True
        while wachten:
            self.screen.fill(ZWART)

            # Titelregels tekenen
            for surf, rect in zip(title_surfs, title_rects):
                self.screen.blit(surf, rect)

            # Knop
            pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))
            self.screen.blit(button_text, button_rect)
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    wachten = False
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        wachten = False
                        self.reset_game()


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

    def draw_exit_screen(self):
        self.screen.fill(GROEN)

        font_large = pg.font.SysFont(None, 72)
        text_surface = font_large.render("EXIT BEHAALD! ", True, WIT)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))
        self.screen.blit(text_surface, text_rect)

        font_teller = pg.font.SysFont(None, 45)
        teller_text = font_teller.render(f"Aantal pogingen: {self.teller}", True, WIT)
        score_text = font_teller.render(f"Score: s{self.score}",True,WIT)
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 100))
        score_rect = score_text.get_rect(center = (BREEDTE // 2, HOOGTE // 2 + 145))
        self.screen.blit(teller_text, teller_rect)
        self.screen.blit(score_text,score_rect)

        font_button = pg.font.SysFont(None, 48)
        button_text = font_button.render("Klik om terug te keren naar het startscherm", True, WIT)
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 200))
        pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))
        self.screen.blit(button_text, button_rect)

        pg.display.flip()

        wachten = True
        while wachten:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    wachten = False
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        wachten = False
                        self.toon_startscherm()

    def draw_lives(self):
        full_hearts = self.player.lives//2
        half_hearts = self.player.lives%2
        empty_hearts = int(MAX_LIVES/2 - full_hearts - half_hearts)
        heart = pg.image.load("Full_Heart.png").convert_alpha()
        heart = pg.transform.scale(heart,(64,64))
        half_heart = pg.image.load("Half_Heart.png").convert_alpha()
        half_heart = pg.transform.scale(half_heart,(64,64))
        empty_heart = pg.image.load("Empty_Heart.png").convert_alpha()
        empty_heart = pg.transform.scale(empty_heart,(64,64))
        pos_life = [5,5]
        for i in range(full_hearts):
            self.screen.blit(heart,pos_life)
            pos_life[0] += 69
        for i in range(half_hearts):
            self.screen.blit(half_heart,pos_life)
            pos_life[0] += 69
        for i in range(empty_hearts):
            self.screen.blit(empty_heart,pos_life)
            pos_life[0] += 69

# --- Startpunt van het spel ---
game = Game()
game.toon_startscherm()
while game.running:
    game.run()

pg.quit()