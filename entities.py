import pygame as pg
from GameSettings import *

entitylijst = []

#maak hier entity classes
class Player():
    def __init__(self,game,x,y, kleur): #gebruik relatieve posities zodat de player altijd binnen squares blijft
        self.game = game
        self.x = x
        self.y = y
        self.kleur = kleur

    def move(self, dx=0, dy=0): #beweging met standaardhoeveelheid 0 zodat er standaard geen beweging is
        self.x += dx
        self.y += dy

    def update(self):
        self.rect_x = self.x * TILESIZE
        self.rect_y = self.y * TILESIZE

    #zelf tekenen is nodig omdat we geen sprite super-class mogen gebruiken    
    def draw(self):
        pg.draw.rect(self.game.screen, self.kleur,(self.rect_x,self.rect_y,TILESIZE,TILESIZE)) 