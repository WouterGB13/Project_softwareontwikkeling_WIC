import heapq #is dit het algoritme? also: deze file: wordt dit de nieuwe entities file uiteindlijk of wat is het doel? (like moeten we nog verder werken aan de oude)
import pygame as pg
from GameSettings import BREEDTE, HOOGTE, TILESIZE

vec = pg.math.Vector2


def heuristic(a, b):
    """Eenvoudige manhattan afstand voor grids."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, grid):
    """
    A* pathfinding algoritme.
    start en goal zijn Vector2s of tuples.
    grid is een 2D lijst waar 1 = muur, 0 = vrije ruimte.
    Geeft een lijst van Vector2 tiles als pad terug.
    """
    # Zorg ervoor dat start en goal tuples zijn
    start = (int(start.x), int(start.y)) if isinstance(start, vec) else start
    goal = (int(goal.x), int(goal.y)) if isinstance(goal, vec) else goal

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # 4 richtingen

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            # reconstruct path
            path = []
            while current in came_from:
                path.append(vec(current))  # Maak er Vector2 van
                current = came_from[current]
            path.reverse()
            return path

        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            # Buiten de map?
            if not (0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid)):
                continue

            # Muur?
            if grid[neighbor[1]][neighbor[0]] == 1:
                continue

            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Geen pad gevonden


def load_map(game):
    """
    Converteer walls in game.entities naar een 2D grid.
    1 = muur, 0 = vrije ruimte.
    """

    grid = [[0 for _ in range(BREEDTE)] for _ in range(HOOGTE)]

    for entity in game.entities:
        if entity.__class__.__name__ == "Wall":
            tile_x = int(entity.pos.x // TILESIZE)
            tile_y = int(entity.pos.y // TILESIZE)
            grid[tile_y][tile_x] = 1

    return grid
