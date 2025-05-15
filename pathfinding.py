from GameSettings import *  # Importeert instellingen uit het bestand 'GameSettings', zoals constants of functies die relevant zijn voor het spel.

def adding_tuples(t1, t2):  # Definieert een functie die twee tuples optelt, handig voor coördinaten.
    return (t1[0] + t2[0], t1[1] + t2[1])  # Voegt de respectieve elementen van de twee tuples samen en retourneert het resultaat als een nieuwe tuple.

def find_path(game, start_loc_map, end_loc_map):  # Hoofdfunctie die het pad zoekt van de startlocatie naar de eindlocatie.
    map = game.kaart.data  # Verkrijgt de kaartgegevens van het spel (de kaart waarin de A*-zoektocht zal plaatsvinden).
    snelste_weg = [start_loc_map]  # Maakt een lijst met de startlocatie als eerste element.
    opties = []  # Lijst voor mogelijke opties van bewegingen.
    optie_kosten = []  # Lijst voor de kosten van de opties, bepaalt welke optie het beste is.
    vast_komen_te_zitter = [None]  # Lijst van posities die al als vast beschouwd zijn (waar geen nuttige bewegingen zijn).
    aantal_keren_langs_pos = {}  # Een woordenboek dat bijhoudt hoe vaak een positie al bezocht is.
    beweegopties = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # De vier mogelijke richtingen (bewegingen) van de speler op de kaart.

    positie = start_loc_map  # Begin de zoektocht bij de startlocatie.
    vorige_posities = [None]  # Lijst om de vorige posities bij te houden (om te vermijden dat we teruggaan naar waar we net vandaan kwamen).

    timer = 0  # Een timer om ervoor te zorgen dat we niet eindeloos blijven zoeken (om oneindige loops te voorkomen).

    while positie != end_loc_map and timer < 1000:  # Zolang de huidige positie niet de eindlocatie is en de timer onder de 1000 blijft.
        timer += 1  # Verhoog de timer om het aantal stappen te tellen.
        opties.clear()  # Leeg de lijst met mogelijke opties voor de volgende stap.
        optie_kosten.clear()  # Leeg de lijst met kosten voor de opties.

        for pos in aantal_keren_langs_pos:  # Voor elke positie die al meerdere keren is bezocht.
            if aantal_keren_langs_pos[pos] == 3 and not pos in vast_komen_te_zitter:  # Als de positie drie keer is bezocht, voeg deze dan toe aan vast_komen_te_zitter.
                vast_komen_te_zitter.append(pos)

        for optie in beweegopties:  # Voor elke mogelijke beweging (richting).
            som = adding_tuples(positie, optie)  # Voeg de optie toe aan de huidige positie om een nieuwe mogelijke positie te krijgen.
            if map[som[1]][som[0]] != '1':  # Controleer of de nieuwe positie geen muur is (aangegeven door '1').
                opties.append(som)  # Voeg de geldige nieuwe positie toe aan de lijst met opties.
                optie_kosten.append((som[0] - end_loc_map[0])**2 + (som[1] - end_loc_map[1])**2)  # Bereken de kosten van de beweging (kwadratisch verschil in x en y ten opzichte van de eindlocatie).

        if len(opties) > 1:  # Als er meer dan één geldige optie is.
            for pos in vast_komen_te_zitter:  # Verwijder alle posities die als vast worden beschouwd.
                for index in range(len(opties)): 
                    if opties[index] == pos:
                        opties.pop(index)
                        optie_kosten.pop(index)
                        break
            for vorige_pos in vorige_posities:  # Verwijder alle posities die al eerder zijn bezocht (om te voorkomen dat we in cirkels bewegen).
                for index in range(len(opties)):
                    if opties[index] == vorige_pos:
                        opties.pop(index)
                        optie_kosten.pop(index)
                        break       

            if len(opties) == 0:  # Als er geen geldige opties zijn, reset dan de bezochte posities en begin opnieuw.
                vorige_posities = [None]
                continue

            laagste_kost_index = 0  # Begin met het aannemen van de eerste optie als de laagste kosten.
            for index in range(1, len(optie_kosten)):  # Vergelijk de kosten van de verschillende opties.
                if optie_kosten[index] < optie_kosten[laagste_kost_index]:
                    laagste_kost_index = index  # Update de index van de optie met de laagste kosten.
            vorige_posities.append(positie)  # Voeg de huidige positie toe aan de lijst van vorige posities.
            positie = opties[laagste_kost_index]  # Kies de optie met de laagste kosten als de nieuwe positie.
        elif len(opties) == 1:  # Als er slechts één optie is.
            vorige_posities = [None]  # Reset de lijst van vorige posities.
            vorige_posities.append(positie)  # Voeg de huidige positie toe aan de lijst van vorige posities.
            positie = opties[0]  # Kies de enige optie als de nieuwe positie.
        else:  # Als er geen opties zijn, kan er geen pad gevonden worden.
            snelste_weg.append(False)  # Voeg False toe aan de lijst van snelste weg om aan te geven dat het pad niet mogelijk is.
            break

        snelste_weg.append(positie)  # Voeg de nieuwe positie toe aan de snelste weg.
        if positie in aantal_keren_langs_pos:  # Als de positie al eerder is bezocht, verhoog het aantal keren dat deze is bezocht.
            aantal_keren_langs_pos[positie] += 1
        else:
            aantal_keren_langs_pos[positie] = 1  # Als de positie nog niet is bezocht, stel het aantal bezoeken in op 1.

        if timer == 1000:  # Als de timer 1000 heeft bereikt, betekent dit dat het pad niet binnen de tijd kon worden gevonden.
            print("time's up")  # Print een bericht om aan te geven dat de tijd om is.
            snelste_weg.append(False)  # Voeg False toe aan de snelste weg om aan te geven dat het pad niet mogelijk is.

    snelste_weg.append(True)  # Als het pad is gevonden, voeg dan True toe aan het einde van de snelste weg.
    snelste_weg.pop(-1)  # Verwijder het laatste element, omdat het niet noodzakelijk is voor het ontwerp van het algoritme.
    return snelste_weg  # Retourneer de snelste weg.

# Functies voor het vereenvoudigen van het pad.
def simplefy_path(path): 
    geskipped1 = False
    geskipped2 = False
    for a in range(len(path)*2):  # Loop om onnodige lussen te vermijden (tweemaal hetzelfde punt bezoeken).
        for x in range(len(path)):
            geskipped1 = False
            for y in range(len(path)):
                if path[x] == path[y] and x != y:
                    for z in range(x, y, int(y-x/abs(y-x))):
                            path.pop(x+1)  # Verwijder onnodige tussenstappen.
                    geskipped1 = True
                    break
            if geskipped1: break

    for a in range(10):  # Loop om omwegen te vermijden (bijvoorbeeld als begin- en eindpunten naast elkaar liggen).
        for x in range(len(path)):
            geskipped2 = False
            for y in range(x, len(path)):
                geskipped2 = False
                for b in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    if adding_tuples(path[x], b) == path[y] and abs(x-y) != 1:
                        for z in range(x, y, int(y-x/abs(y-x))):
                            path.pop(x+1)  # Verwijder overbodige stappen.
                        geskipped2 = True
                        break
                if geskipped2: break
            if geskipped2: break
    return path  # Retourneer het vereenvoudigde pad.

# Functie voor het afsnijden van het pad.
def cut_path(guard, path, vision_range):  
    aantal_stappen = min(int(vision_range*cut_path_view_dist_factor), len(path)-1)  # Bepaal het aantal stappen op basis van het gezichtsbereik.
    zelf_pixel_pos = adding_tuples((path[0][0] * TILESIZE, path[0][1] * TILESIZE), (TILESIZE/2, TILESIZE/2))  # Zet de startpositie om naar pixelcoördinaten.
    for stap in range(aantal_stappen, 1, -1):  # Loop van ver naar dichtbij om te kijken of we het pad kunnen afsnijden.
        ppms = adding_tuples((path[stap][0] * TILESIZE, path[stap][1] * TILESIZE), (int(TILESIZE/2), int(TILESIZE/2)))  # Pixelpositie voor de mogelijke stap.
        pos_tile_hoeken = [
            adding_tuples(ppms, (-TILESIZE/2,-TILESIZE/2)),  # LinksBoven
            adding_tuples(ppms, (TILESIZE/2,-TILESIZE/2)),  # RechtsBoven
            adding_tuples(ppms, (-TILESIZE/2,TILESIZE/2)),  # LinksOnder
            adding_tuples(ppms, (TILESIZE/2,TILESIZE/2))  # RechtsOnder
        ]

        vrij = True
        for hoek in pos_tile_hoeken:
            if guard.line_of_sight_clear(zelf_pixel_pos, hoek, guard.game.player.smart_walls) != True:  # Controleer of het pad vrij is van obstakels.
                vrij = False
                break
        if vrij:  # Als het pad vrij is, verwijder dan onnodige posities uit het pad.
            for z in range(1, stap):
                path.pop(1)
            break
    return path  # Retourneer het pad na het afsnijden.

def reverse_cut_path(guard, path, vision_range):  # Zelfde als cut_path, maar dan vanaf het einde van het pad.
    aantal_stappen = min(int(vision_range*cut_path_view_dist_factor), len(path)-1)
    zelf_pixel_pos = adding_tuples((path[-1][0] * TILESIZE, path[-1][1] * TILESIZE), (TILESIZE/2, TILESIZE/2))  # Zet de laatste positie om naar pixelcoördinaten.
    for stap in range(len(path) - aantal_stappen, len(path)-1, 1):  # Loop van het einde van het pad naar de beginpositie.
        ppms = adding_tuples((path[stap][0] * TILESIZE, path[stap][1] * TILESIZE), (int(TILESIZE/2), int(TILESIZE/2)))  # Pixelpositie voor de mogelijke stap.
        pos_tile_hoeken = [
            adding_tuples(ppms, (-TILESIZE/2,-TILESIZE/2)),  # LinksBoven
            adding_tuples(ppms, (TILESIZE/2,-TILESIZE/2)),  # RechtsBoven
            adding_tuples(ppms, (-TILESIZE/2,TILESIZE/2)),  # LinksOnder
            adding_tuples(ppms, (TILESIZE/2,TILESIZE/2))  # RechtsOnder
        ]

        vrij = True
        for hoek in pos_tile_hoeken:
            if guard.line_of_sight_clear(zelf_pixel_pos, hoek, guard.game.player.smart_walls) != True:  # Controleer of het pad vrij is.
                vrij = False
                break
        if vrij:  # Als het pad vrij is, verwijder dan onnodige posities uit het pad.
            for z in range(1, len(path) - stap - 1):
                path.pop(-2)
            break
    return path  # Retourneer het pad na het afsnijden.