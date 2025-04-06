#gevolgde tutotials via https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i
#tips voor elkaar:
#om alle instances van een bepaalde term te selecteren en tegelijk te kunnen veranderen, selecteer woord en druk op ctrl+shift+L
#in pg.ingebouwde sprite basisklasse mag niet gebruitkt worden
#save altijd een file na het aanmaken van een nieuwe klasse, ander krijg je "niet defined" error bij het starten van programma

import pygame as pg
from GameSettings import * #importeer alle setting zonder steeds GameSettings."setting" te moeten typen
from entities import *
from map_en_camera import *

class Game:
    def __init__(self):
        # startup van game window, etc 
        pg.init()
        #pg.mixer.init() #initieert geluidsfunctie van pg.(niet gebruikt in project)
        self.screen = pg.display.set_mode((BREEDTE,HOOGTE))
        pg.display.set_caption(TITEL)
        self.clock = pg.time.Clock()
        self.running = True
    
    def load_data(self):
        self.kaart = Map('Kaart2.txt')
    
    def new(self):
        #start nieuwe game
        self.walls = []
        for rij, tiles in enumerate(self.kaart.data): #genereer y-coordinaat en tegels van bijhorende rij
            for kolom, tile in enumerate(tiles): #genereer x-coordinaat van individuele tegels
                if tile =='1':
                    wall = Wall(self,kolom,rij)
                    self.walls.append(wall) #maak hier later een apparte functie/whatever van die entitylijst afgaat voor alle muur-class enities in deze in self.walls zet
                    entitylijst.append(wall)
                if tile == 'P':
                    self.player = Player(self,kolom,rij,GEEL) #werkt met squares als coord. , niet met pixels
                    entitylijst.append(self.player)
        self.camera = Camera(self.kaart.width,self.kaart.height)

                    
    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    
    def update(self):
        #update game loop
        for entity in entitylijst:
            entity.update()
        self.camera.update(self.player)

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
        for entity in entitylijst:
            self.screen.blit(entity.image, self.camera.apply(entity)) #apply de relative coord. gegenereerd door de camera op het tekenen van alle entities (past werkelijk pos. niet aan)
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
    game.load_data()
    game.new()
    game.run()
    game.game_over()
pg.quit()