#tips voor elkaar:
#om alle instances van een bepaalde term te selecteren en tegelijk te kunnen veranderen, selecteer woord en druk op ctrl+shift+L
#in pg.ingebouwde sprite basisklasse mag niet gebruitkt worden

import pygame as pg
from GameSettings import * #importeer alle setting zonder steeds GameSettings."setting" te moeten typen

class Game:
    def __init__(self):
        # startup van game window, etc 
        pg.init()
        #pg.mixer.init() #initieert geluidsfunctie van pg.(niet gebruikt in project)
        self.screen = pg.display.set_mode((BREEDTE,HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = pg.time.Clock()
        self.running = True
    
    def new(self):
        #start nieuwe game
        pass

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
    
    def update(self):
        #update game loop
        pass

    def events(self):
        #events binnen game loop
        for event in pg.event.get():
        #check voor game afsluiten met X van de gamewindow
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
    
    def teken_grid(self):
        for x in range(0, BREEDTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (x,0) , (x,HOOGTE), 1)
        for y in range(0, HOOGTE, TILESIZE):
            pg.draw.line(self.screen, LICHTGRIJS, (0,y) , (BREEDTE,y), 1)
                

    def draw(self):
        # teken frame
        self.screen.fill(ACHTERGRONDKLEUR)
        self.teken_grid()
        #altijd laatste line van renderen
        pg.display.flip() 

    def toon_startscherm(self):
        pass

    def game_over(self):
        pass

#uit te voeren code
game = Game()
game.toon_startscherm()
while game.running:
    game.new()
    game.run()
    game.game_over()

pg.quit()