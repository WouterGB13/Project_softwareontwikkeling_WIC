# Gevolgde tutorials via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
# Opmerking: te veel geopende tabs kunnen leiden tot performance issues en bugged guard-pathing
# Handige editor-tips:
# - Ctrl+Shift+L = meerdere selecties tegelijk aanpassen
# - Gebruik NIET de ingebouwde pg.sprite.Sprite class (eigen structuur vereist)
# - Sla bestanden op bij het aanmaken van klassen om runtime fouten zoals "not defined" te vermijden

import pygame as pg
from GameSettings import *  # Instellingen zoals schermgrootte, kleuren, etc.
from entities import *  # Spelentiteiten zoals Wall, Player, Guard, etc.
from map_en_camera import *  # Mapgegevens en cameralogica

teller = 1  # Houdt het aantal pogingen bij bij Game Over   

class Game:
    def __init__(self):  # Constructor voor het spelobject
        pg.init()  # Pygame initialiseren
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))  # Spelscherm instellen
        pg.display.set_caption(TITEL)  # Venstertitel
        self.clock = pg.time.Clock()  # Klok voor frameratecontrole
        self.running = True  # Hoofdloop actief
        self.gameover = False  # Flag voor Game Over status

    def load_data(self):  # Laadt mapdata en genereert guards
        self.kaart = Map('Kaart2.txt')  # Map wordt ingeladen vanaf een tekstbestand

        with open("guard_routes.txt", 'r') as Guards:
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


    def new(self):  # Start nieuw spel, reset entiteiten en laadt data
        self.walls = []  # Lijst voor muur-objecten
        entitylijst.clear()  # Alle entiteiten leegmaken (voor een frisse start)
        self.load_data()  # Map en guards laden
        for row_index, row_data in enumerate(self.kaart.data):
            for col_index, tile in enumerate(row_data):
                if tile == '1':  # '1' duidt een muur aan
                    wall = Wall(self, col_index, row_index)
                    self.walls.append(wall)
                    entitylijst.append(wall)
                elif tile == 'P':  # 'P' is de speler spawn-positie
                    self.player = Player(self, col_index, row_index, GEEL)
                    entitylijst.append(self.player)  # Speler toevoegen aan entiteitenlijst

        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)  # Camera initialiseren

    def run(self):  # Main gameloop voor actieve gameplay
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000  # Delta time berekening voor tijdsafhankelijke beweging
            self.events()  # Gebruikersinput verwerken
            self.update()  # Game state updaten
            self.draw()  # Spel tekenen op scherm

    def update(self):  # Logica-updates voor speler, guards, muren en camera
        self.player.update()  # Speler eerst updaten
        for entity in entitylijst:
            if isinstance(entity, Guard):
                entity.update()  # Guard logica zoals patrouille
            elif isinstance(entity, Wall):
                entity.update()  # Muren (indien nodig voor animatie/gedrag)
        self.camera.update(self.player)  # Camera volgt speler

    def events(self):  # Eventhandler voor sluiting of toetsen
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

    def teken_grid(self):  # Optionele raster-overlay voor debug of esthetiek
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE), 1)
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y), 1)

    def draw(self):  # Teken alle entiteiten op het scherm
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()
        for entity in entitylijst:
            self.screen.blit(entity.image, self.camera.apply(entity))  # Camera verschuift view
            if hasattr(entity, "drawvieuwfield"):  # Indien guard zichtveld heeft
                entity.drawvieuwfield()
        pg.display.flip()  # Update scherm (double buffering)

    def toon_startscherm(self):  # Placeholder voor eventueel startscreen
        pass

    def game_over(self):  # Wordt getoond wanneer speler verliest
        G_font = pg.font.SysFont(None, 72)
        text_surface = G_font.render("GAME OVER", True, ROOD)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))

        # Herstart-knop tekenen
        button_font = pg.font.SysFont(None, 48)
        button_text = button_font.render("Klik om te herstarten", True, WIT)
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))

        # Pogingen tellen
        global teller
        print(f"Speler gepakt door een guard! GAME OVER. {teller}e poging.")
        teller_font = pg.font.SysFont(None, 48)
        teller_text = teller_font.render(f"Aantal pogingen: {teller}", True, WIT)
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 150))
        teller += 1

        # Scherm leegmaken en elementen tekenen
        self.screen.fill(ZWART)
        self.screen.blit(text_surface, text_rect)
        pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))  # Button achtergrond
        self.screen.blit(button_text, button_rect)
        self.screen.blit(teller_text, teller_rect)
        pg.display.flip()

        # Wacht op muisklik of ESC om verder te gaan
        waiting = True
        while waiting:
            for event in pg.event.get():
                keys = pg.key.get_pressed()
                if keys[pg.K_ESCAPE]:  # Spel afsluiten via ESC
                    pg.quit()
                    exit()
                elif event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):  # Klik op knop
                        waiting = False

    def start_game(self):  # Start een nieuw spel via .new() en daarna .run()
        self.new()
        self.run()

# Startpunt van het spel
game = Game()
game.toon_startscherm()
while game.running:
    game.start_game()
    if game.gameover:
        game.game_over()
        game.gameover = False
        game = Game() 
pg.quit()