from GameSettings import *

def adding_tuples(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])

def find_path(game, start_loc_map, end_loc_map): #de locaties zijn tuples (bv: (2,3))
    map = game.kaart.data
    snelste_weg = [start_loc_map]
    opties = []
    optie_kosten = []
    vast_komen_te_zitter = [None]
    aantal_keren_langs_pos = {}
    beweegopties = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    
    positie = start_loc_map
    vorige_posities = [None]
    
    timer = 0
    
    while positie != end_loc_map and timer < 1000:
        timer += 1
        opties.clear()
        optie_kosten.clear()
        
        for pos in aantal_keren_langs_pos:
            if aantal_keren_langs_pos[pos] == 3 and not pos in vast_komen_te_zitter:
                vast_komen_te_zitter.append(pos)
                
        for optie in beweegopties:
            som = adding_tuples(positie, optie)
            if map[som[1]][som[0]] != '1':
                opties.append(som)
                optie_kosten.append((som[0] - end_loc_map[0])**2 + (som[1] - end_loc_map[1])**2)
        
        if len(opties) > 1:
            for pos in vast_komen_te_zitter:
                for index in range(len(opties)):
                    if opties[index] == pos:
                        opties.pop(index)
                        optie_kosten.pop(index)
                        break
            for vorige_pos in vorige_posities:
                for index in range(len(opties)):
                    if opties[index] == vorige_pos:
                        opties.pop(index)
                        optie_kosten.pop(index)
                        break       
            if len(opties) == 0:
                vorige_posities = [None]
                continue
                    
            laagste_kost_index = 0
            for index in range(1, len(optie_kosten)):
                if optie_kosten[index] < optie_kosten[laagste_kost_index]:
                    laagste_kost_index = index
            vorige_posities.append(positie)
            positie = opties[laagste_kost_index]
        elif len(opties) == 1:
            vorige_posities = [None]
            vorige_posities.append(positie)
            positie = opties[0]
        else:
            snelste_weg.append(False)
            break
            
        snelste_weg.append(positie)
        if positie in aantal_keren_langs_pos:
            aantal_keren_langs_pos[positie] += 1
        else:
            aantal_keren_langs_pos[positie] = 1
            
        if timer == 1000:
            print("time's up")
            snelste_weg.append(False)
            
    snelste_weg.append(True)
    snelste_weg.pop(-1)
    return snelste_weg


def simplefy_path(path):
    geskipped1 = False
    geskipped2 = False
    for a in range(len(path)*2):
        for x in range(len(path)):
            geskipped1 = False
            for y in range(len(path)):
                if path[x] == path[y] and x != y:
                    for z in range(x, y, int(y-x/abs(y-x))):
                            path.pop(x+1)
                    geskipped1 = True
                    break
            if geskipped1: break
            
    for a in range(10):
        for x in range(len(path)):
            geskipped2 = False
            for y in range(x, len(path)):
                geskipped2 = False
                for b in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    if adding_tuples(path[x], b) == path[y] and abs(x-y) != 1: #er zijn overbodige stappen gedaan want uiteindelijk kunnen we dus alle tussenstappen tussen x en y in slechts 1 stap doen:
                        for z in range(x, y, int(y-x/abs(y-x))):
                            path.pop(x+1)
                        geskipped2 = True
                        break
                if geskipped2: break
            if geskipped2: break
    return path