import pygame
import time
import json
import sys


class Geometry:
    minx = miny = sys.maxsize
    maxx = maxy = -sys.maxsize

    defaultid = 0

    def __init__(self, points=[]):
        self.id = "0"
        self.points = points
        for newp in points:
            if (newp[0] < self.minx): self.minx = newp[0]
            if (newp[0] > self.maxx): self.maxx = newp[0]
            if (newp[1] < self.miny): self.miny = newp[1]
            if (newp[1] > self.maxy): self.maxy = newp[1]


        self.properties = {}

def pygame_init():
    pygame.display.init()

    size = 800, 600

    return pygame.display.set_mode(size)


def map_to_screen(x, y, cam):
    sc = 3.75 # depends on ppi of display!

    return ((x-cam[0])*sc,(y-cam[1])*sc)

def draw_noise(noise_surface, noise_polys):
    noise_surface.fill((0,0,0,0))
    for noise_poly in noise_polys:
        print(noise_poly.points)
        screencoords2 = [ map_to_screen(x[0], x[1], [566300, -5932300]) for x in noise_poly.points]
        if len(screencoords2) <= 2:
            continue
        col = (255,255,255,255)

    pygame.draw.polygon(noise_surface, col, screencoords2, 0 )

def fromjson(filepath):
    geoms = []
    try:
        with open(filepath) as file:
            try:
                data = json.load(file)
            except ValueError:
                print("No JSON found!")
                return []
            idx = 1
            for feature in data["features"]:
                points = []
                # print(feature)
                if feature["geometry"]["type"] == "MultiPolygon":
                    for point in feature["geometry"]["coordinates"][0][0]:
                        newp = (point[0], -point[1])
                        points.append(newp)
                elif feature["geometry"]["type"] == "Polygon":
                    for point in feature["geometry"]["coordinates"][0]:
                        newp = (point[0], -point[1])
                        points.append(newp)
                g = Geometry(points)
                g.id = filepath + str(idx)
                idx += 1
                g.properties = feature["properties"]
                geoms.append(g)
    except EnvironmentError:
        print("GeoJSON file not found!")
        return []

    return geoms


def draw_geojson(geojson_path):
    screen = pygame_init()
    noise_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    draw_noise(noise_surf, fromjson(geojson_path))
    noise_surf.fill((255,0,0,0))
    while 1:
        screen.blit(noise_surf,(0,0))
