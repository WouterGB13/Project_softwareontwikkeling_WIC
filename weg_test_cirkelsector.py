import pygame as pg
import math
import sys #waarvoor gebruiken wij dit?

# Initialisatie
pg.init()
width, height = 600, 600
screen = pg.display.set_mode((width, height))
pg.display.set_caption("Cirkelsector met Pygame")

# Kleuren
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)

# Instellingen voor de sector
center = (300, 300)  # Middelpunt van de cirkel
radius = 150         # Straal van de sector
start_angle = 30     # In graden
end_angle = 150      # In graden
segments = 100       # Hoeveelheid segmenten om de boog vloeiend te maken

# Functie om sectorpunten te berekenen
def get_sector_points(center, radius, start_angle, end_angle, segments):
    points = [center]
    for i in range(segments + 1):
        angle = math.radians(start_angle + (end_angle - start_angle) * i / segments)
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle)  # let op pygame's y-as
        points.append((x, y))
    return points

# Genereer sectorpunten
sector_points = get_sector_points(center, radius, start_angle, end_angle, segments)

# Hoofdloop
running = True
while running:
    screen.fill(WHITE)

    # Teken de sector
    pg.draw.polygon(screen, BLUE, sector_points)

    pg.display.flip()

    # Event-afhandeling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

pg.quit()
sys.exit()
