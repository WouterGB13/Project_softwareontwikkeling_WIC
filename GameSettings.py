# Game opties en instellingen
TITEL = "METAL GEAR SOLID V(UB): THE PHANTOM KATER"  # Titel van het spelvenster

# Zorg dat de afmetingen deelbaar zijn door TILESIZE voor een netjes grid
BREEDTE = 1024  # Schermbreedte in pixels (bijv. 32 * 32)
HOOGTE = 768    # Schermhoogte in pixels (bijv. 24 * 32)
FPS = 60        # Frames per seconde (hoe vaak het scherm wordt ververst)

# Definities van handige RGB-kleuren
WIT = (255,255,255)       # Voor tekst of visuele effecten
ZWART = (0,0,0)           # Vaak gebruikt voor tekst of om lijntjes te tekenen
ROOD = (255,0,0)          # Voor vijanden
LICHTROOD = (255,100,100) # Voor vijanden of waarschuwingen
GROEN = (0,255,0)         # Voor muren of veilige zones
BLAUW = (0,0,255)         # Optioneel: water, portalen, etc.
DONKERGRIJS = (40,40,40)  # Basiskleur voor achtergrond
LICHTGRIJS = (100,100,100)  # Voor gridlijnen of contrast
GEEL = (255,255,0)        # Spelerkleur

ACHTERGRONDKLEUR = DONKERGRIJS  # Achtergrondkleur van het spel

TILESIZE = 32  # Grootte van één tegel (vierkant) in pixels; bij voorkeur een macht van 2
GRIDBREEDTE = BREEDTE//TILESIZE  # Aantal tegels horizontaal
GRIDHOOGTE = HOOGTE//TILESIZE    # Aantal tegels verticaal

# Instellingen voor de speler
SPELER_SNELHEID = 300  # Snelheid waarmee de speler beweegt (pixels per seconde)

# instellingen voor guards
GUARD_SNELHEID = 50  # Hoe snel guards zich verplaatsen
GUARD_SNELHEID_CHASE = 270
GUARD_ROT_SPEED_PER_SPEED = 0.5  # Rotatiesnelheid afhankelijk van loopsnelheid
ROT_SPEED = GUARD_ROT_SPEED_PER_SPEED*GUARD_SNELHEID  # Effectieve rotatiesnelheid in graden per seconde

TILE_VIEW_DISTANCE = 4  # Aantal tegels dat een guard ver kan kijken
VIEW_DIST = TILE_VIEW_DISTANCE * TILESIZE  # Zichtafstand in pixels
VIZIE_BREEDTE = 50  # Halve gezichtsbreedte in graden (totaal zichtveld = 2 * deze waarde)
RESOLUTIE = 180  # Aantal straal-lijnen in zichtveld (default = hoge resolutie)
SEARCH_TIME = 10000 #ms
CHASE_TIME = 0