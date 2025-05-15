# Tutorials gevolgd via: https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i (tot video 4: camera)
# Let op: teveel open tabs kunnen zorgen voor laggy guards en slechte performance.
# Editor tips:
# - Ctrl+Shift+L: Meerdere regels tegelijk selecteren
# - Gebruik GEEN pg.sprcite.Sprite (eigen structuur vereist)
# - Save je bestanden na maken van nieuwe klassen!

import pygame as pg  # Laadt de pygame-bibliotheek, handig voor graphics, geluid en inputverwerking
from GameSettings import *  # Importeert instellingen zoals resolutie, kleuren, FPS enz.
from entities import *  # Importeert klassen voor game-objecten zoals Player, Guard, Wall enz.
from map_en_camera import *  # Importeert functies voor level layout (kaart) en camera positionering
import random  # Voor willekeurige elementen zoals score-objectplaatsing

class Game:
    """De hoofdklasse die alles beheert: speler, guards, levels en events."""
    def __init__(self):
        pg.init()  # Initialiseer pygame modules
        self.screen = pg.display.set_mode((BREEDTE, HOOGTE))  # Maak venster met breedte/hoogte uit settings
        pg.display.set_caption(TITEL)  # Zet venstertitel
        self.clock = self.create_clock()  # Maak een klokobject voor framerate-controle
        self.running = True  # Houdt bij of het spel actief moet blijven draaien
        self.entities = []  # Lijst met alle actieve entiteiten zoals spelers, guards, score-objecten
        self.button_rect = None  # Rechthoek voor Game Over knop (voor interactie)
        self.active_points = 0  # Aantal actieve punten (kan gebruikt worden om dynamisch score-items bij te houden)
        self.show_bag = False  # Vlag om aan te geven of het rugzak commando zichtbaar is

    def create_clock(self):
        """Maakt de klok aan voor FPS control."""
        return pg.time.Clock()  # Retourneert een Clock-object dat FPS reguleert

    def load_data(self):
        """Laad de kaart en de routes van de guards."""
        self.kaart = Map('p_gebouwen.txt')  # Laad kaartgegevens (walls, startposities, enz.)
        self.dumb_guard_routes = []  # Patrouilleroutes voor simpele guards
        self.smart_guard_routes = []  # Patrouilleroutes voor slimme guards
        with open("guard_routes.txt", 'r') as Guards:  # Open het routebestand
            for line in Guards:  # Itereer door elke regel (één route per regel)
                # Converteer elk coordinatenpaar naar een lijst van integers
                temp_route = [list(map(int, pair.split(','))) for pair in line.strip().split(';')]
                # Bepaal of het een slimme (1) of domme (0) guard is
                if temp_route[0][0] == 1:
                    temp_route[0].pop(0)  # Verwijder type-identificatie
                    self.smart_guard_routes.append(temp_route)  # Voeg toe aan slimme routes
                
                if temp_route[0][0] == 0:   
                    temp_route[0].pop(0)  # Verwijder type-identificatie
                    self.dumb_guard_routes.append(temp_route)  # Voeg toe aan domme routes

    def new(self):
        """Start een nieuw spel: reset entiteiten en laad alles."""
        self.entities.clear()  # Verwijder oude entiteiten van vorige sessie
        self.walls = []  # Lijst van muur-objecten
        self.possible_score_pos = []  # Lijst met locaties waar punten kunnen verschijnen
        self.score = 0  # Reset score
        self.load_data()  # Laad opnieuw kaart en guardroutes
        self.exits = []  # Exitlocaties opnieuw initialiseren
        self.gameover = False  # Flag die aangeeft of het spel 'Game Over' is
        self.gameover_screen_drawn = False  # Zodat het Game Over scherm maar 1 keer wordt getekend
        self.exit_screen = False  # Flag die bepaalt of exit-scherm moet worden getoond
        for row_idx, row in enumerate(self.kaart.data): # Loop door kaartdata (2D-array)
            for col_idx, tile in enumerate(row):
                if tile == '1':  # Muur
                    wall = Wall(self, (col_idx, row_idx))
                    self.walls.append(wall)
                
                elif tile == 'P':  # Speler
                    self.player = Player(self, (col_idx, row_idx), GEEL)
                    self.startpos = vec(col_idx*TILESIZE, row_idx*TILESIZE)  # Spawnlocatie
                    self.entities.append(self.player)

                elif tile == "C":  # coordinaten terug vinden in het spel
                    print(f"kolom {col_idx}, rij {row_idx}")

                elif tile == "E":  # Exit
                    exit_tile = Exit(self, (col_idx, row_idx))
                    self.exits.append(exit_tile)

                elif tile == "S":  # Mogelijke scorelocatie
                    self.possible_score_pos.append((col_idx, row_idx))

                elif tile == "B":  # Rugzak-object
                    self.bag = Bag(self,(col_idx,row_idx))
                    self.entities.append(self.bag)

        for route in self.dumb_guard_routes: # Voeg domme guards toe met route
            guard = Domme_Guard(self, (route[0][0], route[0][1]), route)
            self.entities.append(guard)

        for route in self.smart_guard_routes: # Voeg slimme guards toe met route
            guard = Slimme_Guard(self, (route[0][0], route[0][1]), route)
            self.entities.append(guard)

        # Voeg willekeurige scoreobjecten toe
        for i in range(AANTAL_PUNTEN):  # aantal punten dat je wilt genereren (uit settings)
            pos = random.choice(self.possible_score_pos)  # Kies willekeurig een positie uit de lijst van mogelijke scorelocaties
            punt = Score(self, pos)  # Maak een Score-object op die locatie; geef het huidige Game-object mee als context
            self.possible_score_pos.remove(pos)  # Verwijder die locatie zodat er niet twee punten op dezelfde plek komen
            self.entities.append(punt)  # Voeg het score-object toe aan de lijst met actieve entiteiten zodat het wordt getekend en geüpdatet

        self.camera = Camera(self.kaart.BREEDTE, self.kaart.HOOGTE)  # Camera instellen
        self.player.load_close_walls()  # Optimalisatie: laadt muren dicht bij de speler

    def run(self):
        """Hoofdloop: verwerkt input, updates en tekent frames."""
        self.new()  # Initialiseer nieuw spel
        events = pg.event.get()  # Haal alle gebeurtenissen op
        self.check_exit(events)  # Verwerk sluit-event
        self.playing = True  # Zet spel-status op actief
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000  # Delta time in seconden (voor bewegingstiming)
            self.handle_events()  # Verwerk input
            if self.gameover:
                if not self.gameover_screen_drawn:
                    self.draw_game_over_screen()
                    self.gameover_screen_drawn = True

            elif self.exit_screen:
                self.draw_exit_screen()  # Exit-behaald scherm

            else:
                self.update()  # Update posities en logica
                self.draw()  # Teken alles

    def handle_events(self):
        """Vangt alle gebruikersinput op: toetsenbord, muis, afsluiten."""
        for event in pg.event.get():  # Doorloop alle gebeurtenissen
            if event.type == pg.QUIT:  # Venster sluiten
                self.playing = False
                self.running = False
                pg.quit()
                exit()

            elif event.type == pg.KEYDOWN:  # Toetsenbordinput
                if event.key == pg.K_ESCAPE:  # Escape: afsluiten
                    self.playing = False
                    self.running = False
                    pg.quit()
                    exit()

                if self.exit_screen:  # Terug naar startscherm
                    self.exit_screen = False
                    self.toon_startscherm()

                elif self.gameover:  # Restart game na game over
                    self.new()

            elif event.type == pg.MOUSEBUTTONDOWN:  # Muisinput
                if self.gameover and self.button_rect and self.button_rect.collidepoint(event.pos):
                    self.new()  # Herstarten bij klik op knop

    def check_exit(self, events):
        """Verwerkt Escape-toets en sluiten via vensterkruisje"""
        for event in events:
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                self.playing = False
                pg.quit()
                exit()

    def update(self):
        """Update alle objecten en check botsingen."""
        for entity in self.entities:
            entity.update()  # Roep update() aan van elke entiteit
            if isinstance(entity, Guard):
                # Botsing tussen speler en guard
                if self.player.rect.colliderect(entity.rect):
                    self.player.pos = self.startpos.copy()  # Reset spelerpositie
                    self.score = 0  # Score terug naar 0
                    for entity in self.entities:
                        if isinstance(entity, Guard):
                            entity.reset()  # Reset guard-posities

                    self.player.lives -= 1  # Levens verminderen
                    if self.player.lives == 0:  # Game Over
                        self.gameover = True
                        self.teller += 1
                        print(f"Speler gepakt door guard! GAME OVER. {self.teller}e poging.")

        # Check of speler bij een uitgang is aangekomen
        for exit_tile in self.exits:
            if self.player.rect.colliderect(exit_tile.rect):
                if not self.gameover:
                    print("speler heeft de uitgang bereikt")
                    self.exit_screen = True
                    break

        self.camera.update(self.player)  # Camera volgt speler

    def draw_score(self):
        scorefont = pg.font.SysFont(None, 32)
        score_display = scorefont.render(f"{self.score}", True, WIT)
        score_rect = score_display.get_rect(center=(BREEDTE - 16, 16))
        self.screen.blit(score_display, score_rect)

    def draw(self):
        """Teken alle game-elementen op het scherm."""
        self.screen.fill(ACHTERGRONDKLEUR)  # Achtergrondkleur vullen
        self.teken_grid()  # Raster tekenen

        for entity in self.entities:
            self.screen.blit(entity.image, self.camera.apply(entity))  # Teken entiteit
            if isinstance(entity, Guard):
                entity.draw_view_field()  # Teken zichtveld guard

        for wall in self.walls:
            self.screen.blit(wall.image, self.camera.apply(wall))

        for exit in self.exits:
            self.screen.blit(exit.image, self.camera.apply(exit))
            exit.draw(self.screen, self.camera)

        if self.show_bag: # Als de rugzak zichtbaar wordt
            text = pg.font.SysFont(None, 48).render("Press P to use", True, WIT)
            rect = text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 80))
            self.screen.blit(text, rect)
            
        self.draw_lives()
        self.draw_score()
        pg.display.flip()  # Alles tegelijk tonen (double buffering)

    def teken_grid(self):
        """Teken raster op de achtergrond voor visuele referentie."""
        deltax, deltay = self.camera.return_shift_of_screen()
        for x in range(deltax - TILESIZE//2, BREEDTE+deltax+TILESIZE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x, 0), (x, HOOGTE))

        for y in range(deltay - TILESIZE//2, HOOGTE+deltay+TILESIZE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0, y), (BREEDTE, y))

    def toon_startscherm(self):
        """Toont het startscherm vóór het spel begint met een knop om te starten."""
        font_title = pg.font.SysFont(None, 72)  # Maakt een groot lettertype-object voor de titeltekst
        font_button = pg.font.SysFont(None, 48)  # Maakt een iets kleiner lettertype voor de startknoptekst
        title_lines = ["METAL GEAR SOLID V(UB):", "THE PHANTOM KATER"]  # Tekstregels die samen de titel vormen
        # Render elke titelregel naar een Surface-object met witte kleur
        title_surfs = [font_title.render(line, True, WIT) for line in title_lines]
        start_y = HOOGTE // 2 - 140  # Verticale positie van de eerste regel; zorgt dat titel mooi gecentreerd staat
        title_rects = []  # Lijst voor de rects van elke titelregel
        # Bepaal de rechthoeken voor elke titelregel, zodat ze netjes gecentreerd staan
        for i, surf in enumerate(title_surfs):
            title_rects.append(surf.get_rect(center=(BREEDTE // 2, start_y + i * 80)))  # Voeg de rect toe aan de lijst

        button_text = font_button.render("Klik om te starten", True, WIT) # Render de tekst voor de knop "Klik om te starten"
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 80)) # Positioneer de knop gecentreerd onder de titel
        self.teller = 0  # Reset het aantal pogingen bij start van het spel
        wachten = True  # Vlag om in de lus te blijven tot de speler klikt of sluit
        while wachten:
            self.screen.fill(ZWART)  # Maak het scherm volledig zwart (achtergrond)
            # Teken de titelregels (tekst + positie)
            for surf, rect in zip(title_surfs, title_rects): # Zip koppelt een item uit de eerste lijst aan het overeenkomstige item uit de tweede lijst
                self.screen.blit(surf, rect)

            # Teken de rode knopachtergrond (vergroot iets t.o.v. de tekst)
            pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))
            # Teken de tekst bovenop de knop
            self.screen.blit(button_text, button_rect)
            pg.display.flip()  # Update het scherm zodat alle nieuwe elementen zichtbaar worden
            events = pg.event.get()  # Haal alle pygame-events op (toetsenbord, muis, sluiten)
            self.check_exit(events)  # Verwerk eventueel sluiten of Escape via universele functie
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):  # Controleer of speler op de knop klikt
                        wachten = False  # Verlaat startscherm
                        self.new()  # Start het spel met alle entiteiten

    def draw_game_over_screen(self):
        """Toont het scherm na game over met resetmogelijkheid."""
        self.screen.fill(ZWART)  # Maak het volledige scherm zwart (achtergrondkleur voor het Game Over scherm)
        font_large = pg.font.SysFont(None, 72)  # Definieer een groot lettertype voor de hoofdtekst ("GAME OVER")
        text_surface = font_large.render("GAME OVER", True, ROOD)  # Render de tekst "GAME OVER" in rood als een afbeelding (surface)
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))  
        # Bepaal de positie van de tekst: gecentreerd horizontaal, iets boven het midden van het scherm
        self.screen.blit(text_surface, text_rect)  # Teken de "GAME OVER"-tekst op het scherm
        font_button = pg.font.SysFont(None, 48)  # Kies een kleiner lettertype voor de knoptekst
        button_text = font_button.render("Klik om te herstarten", True, WIT)  
        # Render de knoptekst als een witte afbeelding (surface)
        self.button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 50))  
        # Positioneer de knoptekst onder het midden van het scherm en bewaar de bijhorende rechthoek
        pg.draw.rect(self.screen, ROOD, self.button_rect.inflate(20, 20))  
        # Teken een rode knop-achtergrond iets groter dan de tekst (met extra padding van 20 pixels)
        self.screen.blit(button_text, self.button_rect)  # Teken de tekst bovenop de rode knop
        font_teller = pg.font.SysFont(None, 45)  # Definieer een lettertype voor de pogingenteller
        teller_text = font_teller.render(f"Aantal pogingen: {self.teller}", True, WIT)  
        # Render de tekst met het aantal keer dat de speler Game Over ging
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 150))  
        # Positioneer deze tekst onder de knop (nog wat verder naar beneden)
        self.screen.blit(teller_text, teller_rect)  # Teken de tellertekst op het scherm
        pg.display.flip()  # Werk het scherm bij zodat alles in één keer zichtbaar wordt
        events = pg.event.get()  # Verzamel alle gebeurtenissen sinds de laatste update (muis, toetsenbord, quit...)
        self.check_exit(events)  # Roep de universele methode aan om te controleren of speler wil afsluiten (Escape of venster sluiten)

    def draw_exit_screen(self):
        """Toont het scherm wanneer speler succesvol ontsnapt."""
        self.screen.fill(GROEN)  # Maak het scherm volledig groen als achtergrondkleur voor het 'Exit behaald'-scherm
        font_large = pg.font.SysFont(None, 72)  # Groot lettertype voor de titeltekst
        text_surface = font_large.render("EXIT BEHAALD! ", True, WIT)  
        # Render de boodschap "EXIT BEHAALD!" in witte kleur als een afbeelding
        text_rect = text_surface.get_rect(center=(BREEDTE // 2, HOOGTE // 2 - 100))  
        # Plaats de titel gecentreerd horizontaal, iets boven het midden
        self.screen.blit(text_surface, text_rect)  # Teken de titeltekst op het scherm
        font_teller = pg.font.SysFont(None, 45)  # Lettertype voor pogingenteller en score
        teller_text = font_teller.render(f"Aantal pogingen: {self.teller}", True, WIT)  
        # Render het aantal pogingen dat nodig was om te winnen
        score_text = font_teller.render(f"Score: {self.score}", True, WIT)  
        # Render de behaalde score van de speler
        teller_rect = teller_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 100))  
        # Plaats 'Aantal pogingen' iets onder het midden
        score_rect = score_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 145))  
        # Plaats de score nog wat lager
        self.screen.blit(teller_text, teller_rect)  # Teken het pogingen-aantal op het scherm
        self.screen.blit(score_text, score_rect)  # Teken de scoretekst op het scherm
        font_button = pg.font.SysFont(None, 48)  # Lettertype voor de terugkeerknop
        button_text = font_button.render("Klik om terug te keren naar het startscherm", True, WIT)  
        # Render knoptekst in het wit
        button_rect = button_text.get_rect(center=(BREEDTE // 2, HOOGTE // 2 + 200))  
        # Plaats knop onderaan het scherm
        pg.draw.rect(self.screen, ROOD, button_rect.inflate(20, 20))  
        # Teken een rode rechthoek achter de knoptekst (iets groter dan de tekst voor padding)
        self.screen.blit(button_text, button_rect)  # Teken de knoptekst op de knop
        pg.display.flip()  # Update het scherm zodat alles zichtbaar wordt
        wachten = True  # Flag om in de lus te blijven totdat gebruiker klikt of sluit
        while wachten:
            events = pg.event.get()  # Haal alle pygame events op
            self.check_exit(events)  # Check of gebruiker Escape of sluitknop gebruikt
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:  # Als gebruiker met de muis klikt
                    if button_rect.collidepoint(event.pos):  # En op de knop klikt
                        wachten = False  # Verlaat de lus
                        self.toon_startscherm()  # Ga terug naar het startscherm

    def draw_lives(self):
        """Tekent de levensbalk met hartjes op basis van huidige levens."""
        full_hearts = self.player.lives // 2  
        # Tel hoeveel volledige harten moeten worden getekend (elke 2 levens = 1 vol hart)
        half_hearts = self.player.lives % 2  
        # Als het aantal levens oneven is, is er één half hart
        empty_hearts = int(MAX_LIVES / 2 - full_hearts - half_hearts)  
        # Reken uit hoeveel lege harten nog nodig zijn om het totaal op MAX_LIVES te brengen
        heart = pg.image.load("Full_Heart.png").convert_alpha()  
        # Laad de afbeelding voor een volledig hart met transparantie
        heart = pg.transform.scale(heart, (64, 64))  
        # Schaal het volledige hart naar 64x64 pixels
        half_heart = pg.image.load("Half_Heart.png").convert_alpha()  
        # Laad de afbeelding voor een half hart
        half_heart = pg.transform.scale(half_heart, (64, 64))  
        # Schaal het halve hart naar 64x64 pixels
        empty_heart = pg.image.load("Empty_Heart.png").convert_alpha()  
        # Laad de afbeelding voor een leeg hart
        empty_heart = pg.transform.scale(empty_heart, (64, 64))  
        # Schaal het lege hart naar 64x64 pixels
        pos_life = [5, 5]  
        # Startpositie linksboven voor het eerste hart (x=5, y=5)
        for i in range(full_hearts):
            self.screen.blit(heart, pos_life)  
            # Teken een vol hart op het scherm op huidige positie
            pos_life[0] += 69  
            # Verplaats x-positie naar rechts voor het volgende hart (64px + 5px marge)

        for i in range(half_hearts):
            self.screen.blit(half_heart, pos_life)  
            # Teken eventueel één half hart
            pos_life[0] += 69  

        for i in range(empty_hearts):
            self.screen.blit(empty_heart, pos_life)  
            # Teken de resterende lege harten
            pos_life[0] += 69  

# --- Startpunt van het spel ---
game = Game()  # Maak game object aan
game.toon_startscherm()  # Toon het intro scherm
while game.running:  # Start hoofdgame loop zolang game actief is
    game.run()

pg.quit()  # Stop pygame als alles klaar is