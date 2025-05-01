# Game instellingen en opties

# Titel
TITEL = "METAL GEAR SOLID V(UB): THE PHANTOM KATER"

# Schermgrootte
BREEDTE = 1024  # pixels (zorg dat deelbaar is door TILESIZE)
HOOGTE = 768

# Framerate
FPS = 60  # frames per seconde

# Kleuren (RGB) 
WIT = (255, 255, 255)
ZWART = (0, 0, 0)
ROOD = (255, 0, 0)
LICHTROOD = (255, 100, 100)
GROEN = (0, 255, 0)
BLAUW = (0, 0, 255)
DONKERGRIJS = (40, 40, 40)
LICHTGRIJS = (100, 100, 100)
GEEL = (255, 255, 0)

ACHTERGRONDKLEUR = DONKERGRIJS

# Tile-instellingen
TILESIZE = 32  # grootte per tegel (vierkant, in pixels)
GRIDBREEDTE = BREEDTE // TILESIZE  # aantal tegels horizontaal
GRIDHOOGTE = HOOGTE // TILESIZE    # aantal tegels verticaal

# Speler instellingen
SPELER_SNELHEID = 300  # pixels per seconde

# Guard instellingen
GUARD_SNELHEID = 50  # patrol snelheid
GUARD_SNELHEID_CHASE = 270  # snelheid tijdens achtervolging
ALERT_DISTANCE = 200  # afstand waarbinnen guards elkaar waarschuwen (pixels)
ROTATE_SPEED = 360  # graden per seconde


# Zicht instellingen
TILE_VIEW_DISTANCE = 4  # aantal tegels
VIEW_DIST = TILE_VIEW_DISTANCE * TILESIZE  # in pixels
VISIE_BREEDTE = 50  # halve breedte zichtveld in graden
RESOLUTIE = 180  # hoeveelheid straal-lijnen in zichtveld (hoger = gedetailleerder)

# Search & Chase timers (in milliseconden)
SEARCH_TIME_MS = 10000  # zoektijd na speler uit zicht
CHASE_TIME_MS = 0  # niet gebruikt momenteel