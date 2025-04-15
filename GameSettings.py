# Game opties en instellingen
TITEL = "METAL GEAR SOLID V(UB): THE PHANTOM KATER"  # Titel van het spelvenster

# Zorg dat de afmetingen deelbaar zijn door TILESIZE voor een netjes grid
BREEDTE = 1024  # Schermbreedte in pixels (bijv. 32 * 32)
HOOGTE = 768    # Schermhoogte in pixels (bijv. 24 * 32)
FPS = 60        # Frames per seconde (hoe vaak het scherm wordt ververst)

# Definities van handige RGB-kleuren
WIT = (255,255,255)
ZWART = (0,0,0)
ROOD = (255,0,0)
GROEN = (0,255,0)
BLAUW = (0,0,255)
DONKERGRIJS = (40,40,40)
LICHTGRIJS = (100,100,100)
GEEL = (255,255,0)

ACHTERGRONDKLEUR = DONKERGRIJS  # Achtergrondkleur van het spel

TILESIZE = 32  # Grootte van één tegel (vierkant) in pixels; bij voorkeur een macht van 2
GRIDBREEDTE = BREEDTE/TILESIZE  # Aantal tegels horizontaal
GRIDHOOGTE = HOOGTE/TILESIZE    # Aantal tegels verticaal

# Instellingen voor de speler
SPELER_SNELHEID = 300  # Snelheid waarmee de speler beweegt (pixels per seconde)

#instellingen voor guards
GUARD_SNELHEID = 350
GUARD_ROT_SPEED_PER_SPEED = 0.5
ROT_SPEED = GUARD_ROT_SPEED_PER_SPEED*GUARD_SNELHEID