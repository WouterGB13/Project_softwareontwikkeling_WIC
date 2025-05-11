# Game instellingen en opties

# Titel
TITEL = "METAL GEAR SOLID V(UB): THE PHANTOM KATER"

# Schermgrootte
BREEDTE = 1056  # pixels (zorg dat deelbaar is door TILESIZE)
HOOGTE = 800

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
PAARS = (140, 4, 215)
BRUIN = (138, 102, 66)

ACHTERGRONDKLEUR = DONKERGRIJS

# Tile-instellingen
TILESIZE = 32  # grootte per tegel (vierkant, in pixels)
GRIDBREEDTE = BREEDTE // TILESIZE  # aantal tegels horizontaal
GRIDHOOGTE = HOOGTE // TILESIZE    # aantal tegels verticaal

# Speler instellingen
SPELER_SNELHEID = 300  # pixels per seconde (300)
MAX_LIVES = 6

# Guard instellingen
GUARD_SNELHEID = 50   # patrol snelheid
GUARD_SNELHEID_CHASE = 250  # snelheid tijdens achtervolging (270 origineel, aangepast voor testing purposes)
ALERT_DISTANCE = 200  # afstand waarbinnen guards elkaar waarschuwen (pixels)
ROTATE_SPEED = 360  # graden per seconde

ADAPTIVE_CONES = False


# Zicht instellingen
TILE_VIEW_DISTANCE = 10  # aantal tegels
TILE_HEAR_DISTANCE = 2 #echte afstand is dit min 1 want hij rekent vanaf de centers
VIEW_DIST = TILE_VIEW_DISTANCE * TILESIZE  # in pixels
HEAR_DIST = TILE_HEAR_DISTANCE * TILESIZE
VISIE_BREEDTE = 37.5  # halve breedte zichtveld in graden
RESOLUTIE = 10  # hoeveelheid straal-lijnen in zichtveld (hoger = gedetailleerder)

# Search & Chase timers (in milliseconden)
SEARCH_TIME_MS = 10000  # zoektijd na speler uit zicht
CHASE_TIME_MS = 0  # niet gebruikt momenteel
STUCK_DISTANCE_THRESHOLD = 1.5  # pixels
STUCK_TIME_LIMIT = 2000  # milliseconden (2 seconden)
CHASE_TIMEOUT = 3000  # milliseconden (3 seconden)

#trap
cooldown_time = 3000  # tijd tussen het activeren van de trap en het kunnen gebruiken van de trap (in milliseconden)

#aantal punten die tegelijk op map aanwezig zijn (niet meer dan aantal mogelijke locaties)
AANTAL_PUNTEN = 15