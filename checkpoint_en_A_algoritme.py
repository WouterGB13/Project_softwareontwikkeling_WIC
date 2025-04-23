#ik zou graag gebruik maken van checkpoint in de map zelf, zonder coordinaten te gebruiken

#dit moet bij de Map of main game class:

def extract_guard_route(self, char='G'):
    route = []
    for y, row in enumerate(self.mapdata):  # self.mapdata is je kaart
        for x, tile in enumerate(row):
            if tile == char:
                route.append((x, y))
    return sorted(route, key=lambda pos: (pos[1], pos[0]))  # optioneel: gesorteerd op rijen



# dit in "spelinitialisatie" maar geen idee wa ze bedoelen daarmee

# Guard route genereren vanuit mapdata
guard_route = game.map.extract_guard_route('G')

# Guard starten op eerste punt van de route
gx, gy = guard_route[0]
guard = Guard(game, gx, gy, guard_route)
game.guard_group.add(guard)


#en k heb ook een A* algoritme gevonden waarbij hij de kortste route tot het volgende checkpoint bekijkt

# Stap 1: Vind alle G-punten op de map
for y in kaart_hoogte:
    for x in kaart_breedte:
        als map[y][x] == 'G':
            voeg (x, y) toe aan G-punten

# Stap 2: Gebruik A* tussen elke G en de volgende G
# Voor elk paar G[i] -> G[i+1]:
	# Gebruik het A* algoritme om kortste route tussen die 2 punten te vinden
	# Plak dat pad (zonder dubbele knooppunten) in de totale route van de guard

# Stap 3: A* zelf (heuristiek: Manhattan distance)
#A*(start, doel):
# 1. Initialiseer open list met start
# 2. Gebruik een came_from dict voor reconstructie
# 3. Gebruik g_score en f_score
# 4. Stop als je het doel hebt bereikt

#CODEIMPLEMENTATIE
import heapq

def astar(mapdata, start, goal):
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])  # Manhattan afstand

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        x, y = current
        for dx, dy in [(0,1),(1,0),(-1,0),(0,-1)]:  # buren
            neighbor = (x+dx, y+dy)
            nx, ny = neighbor
            if 0 <= ny < len(mapdata) and 0 <= nx < len(mapdata[0]) and mapdata[ny][nx] != '1':
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []


# KORTSTE ROUTE TUSSEN ALLE G-PUNTEN
def build_guard_route(mapdata, char='G'):
    # Vind alle G-punten
    g_points = []
    for y, row in enumerate(mapdata):
        for x, tile in enumerate(row):
            if tile == char:
                g_points.append((x, y))
    
    # Route met A* verbinden
    full_path = []
    for i in range(len(g_points) - 1):
        path = astar(mapdata, g_points[i], g_points[i+1])
        if i > 0:
            path = path[1:]  # dubbele punt vermijden
        full_path.extend(path)
    return full_path

# Voorbeeldgebruik
route = build_guard_route(game.map.mapdata, char='G')
guard = Guard(game, route[0][0], route[0][1], route)
game.guard_group.add(guard)
