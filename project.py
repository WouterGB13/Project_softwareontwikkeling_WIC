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
        self.button_rect = None  # Voor resetknop na game over
        self.gameover_screen_drawn = False
        self.exit_screen = False  # Voeg een flag toe om te controleren wanneer het exit-scherm zichtbaar is

    def create_clock(self):
        """Maakt de klok aan voor FPS control."""
        return pg.time.Clock()

    def load_data(self):
        """Laad de kaart en de routes van de guards."""
        self.kaart = Map('Kaart2.txt')  # Laad map layout uit tekstbestand
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
        self.load_data()
        self.exits = []  # Voeg toe in __init__ of new()

        # Maak objecten aan volgens de kaartdata
        for row_idx, row in enumerate(self.kaart.data):
            for col_idx, tile in enumerate(row):
                if tile == '1':
                    wall = Wall(self, (col_idx, row_idx))
                    self.walls.append(wall)
                    self.entities.append(wall)
                elif tile == 'P':
                    self.player = Player(self, (col_idx, row_idx), GEEL)
                    self.entities.append(self.player)
                elif tile == "C":
                    print(f"kolom {col_idx}, rij {row_idx}")
                elif tile == "E":
                    exit_tile = Exit(self, (col_idx, row_idx))
                    self.exits.append(exit_tile)
                    self.entities.append(exit_tile)

        # Plaats guards met hun patrouille-routes
        for route in self.dumb_guard_routes:
            guard = Domme_Guard(self, (route[0][0], route[0][1]), route)
            self.entities.append(guard)

        for route in self.smart_guard_routes:
            guard = Slimme_Guard(self, (route[0][0], route[0][1]), route)
            self.entities.append(guard)

        # Installeer de camera om mee te bewegen met de speler
        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)

    def run(self):
        """Hoofdloop: verwerkt input, updates en tekent frames."""
        self.new()
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
            elif event.type == pg.MOUSEBUTTONDOWN and self.gameover and self.button_rect:
                if self.button_rect.collidepoint(event.pos):
                    self.reset_game()
            elif event.type == pg.KEYDOWN:
                if self.exit_screen:
                    self.exit_screen = False  # Reset het exit-scherm
                    self.toon_startscherm()  # Terug naar het startscherm
                elif self.gameover:
                    self.reset_game()

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            pg.quit()
            exit()

    def update(self):
        """Update alle objecten en check botsingen."""
        for entity in self.entities:
            entity.update()
            if isinstance(entity, Guard):
                if self.player.rect.colliderect(entity.rect):
                    self.player.pos = vec(32*16,32*25)
                    for entity in self.entities:
                        if isinstance(entity, Guard):
                            entity.reset()
                    self.player.lives -= 1
                    print(self.player.lives)
                    if self.player.lives == 0:
                        self.gameover = True
                        self.teller += 1
                        print(f"Speler gepakt door guard! GAME OVER. {self.teller}e poging.") #VRAAG 3: doen we print weg?

        # Update camera positie gebaseerd op speler
        self.camera.update(self.player)

    def draw(self):
        """Teken alle game-elementen op het scherm."""
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()

        for entity in self.entities:
            self.screen.blit(entity.image, self.camera.apply(entity))
            if isinstance(entity, Guard):
                entity.draw_view_field()  # Teken zichtveld van guards

            if isinstance(entity, Exit):
                entity.draw(self.screen, self.camera)
        self.draw_lives()
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

        title_text = font_title.render("Welkom bij het WIC Ontsnappingsspel", True, WIT)
        title_rect = title_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))

        # Tekst voor de startknop
        button_text = font_button.render("Klik om te starten", True, WIT)
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))

        # Wacht tot speler op de knop klikt
        wachten = True
        while wachten:
            self.screen.fill(ZWART)
            self.screen.blit(title_text, title_rect)
            pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))  # Knop achtergrond
            self.screen.blit(button_text, button_rect)
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    wachten = False
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        wachten = False
                        self.reset_game()  # Begin een nieuw spel

    def draw_game_over_screen(self):
        """Teken het Game Over scherm met resetknop."""
        self.screen.fill(ZWART)

        # Tekst: "GAME OVER"
        font_large = pg.font.SysFont(None, 72)
        text_surface = font_large.render("GAME OVER", True, ROOD)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))
        self.screen.blit(text_surface, text_rect)

        # Herstart-knop
        font_button = pg.font.SysFont(None, 48)
        button_text = font_button.render("Klik om te herstarten", True, WIT)
        self.button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))
        pg.draw.rect(self.screen, ROOD, self.button_rect.inflate(20, 20))  # Knop achtergrond
        self.screen.blit(button_text, self.button_rect)

        # Pogingenteller
        font_teller = pg.font.SysFont(None, 45)
        teller_text = font_teller.render(f"Aantal pogingen: {self.teller}", True, WIT)
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 150))
        self.screen.blit(teller_text, teller_rect)

        pg.display.flip()

    def draw_exit_screen(self):
        """Teken het Exit scherm na het verlaten van de map via de exit."""
        self.screen.fill(GROEN)  # Aangepaste kleur voor exit-scherm

        # Tekst: "EXIT BEHAALD"
        font_large = pg.font.SysFont(None, 72)
        text_surface = font_large.render("EXIT BEHAALD!", True, WIT)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))
        self.screen.blit(text_surface, text_rect)

        # Weergeven van pogingen
        font_teller = pg.font.SysFont(None, 45)
        teller_text = font_teller.render(f"Aantal pogingen: {self.teller}", True, WIT)
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 100))
        self.screen.blit(teller_text, teller_rect)

        # Tekst voor de terug-knop
        font_button = pg.font.SysFont(None, 48)
        button_text = font_button.render("Klik om terug te keren naar het startscherm", True, WIT)
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 200))

        # Tekenen van de knop
        pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))  # Knop achtergrond
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

    def toon_startscherm(self):
        """(Placeholder) Startscherm tonen."""
        pass

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