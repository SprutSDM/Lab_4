import pygame
import random
import math
from pygame import gfxdraw

class iEdge:
    def __init__(self, key, vertex1, vertex2, value=None, color='red'):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.color = color
        self.value = value


class iVertex:
    def __init__(self, key, value=None, 
                 color='light_gray', color_edge='black', color_text='black',
                 cord=None,
                 rad=8):
        self.key = key
        self.value = str(value)
        self.label = None
        self.color = color
        self.color_edge = color_edge
        self.color_text = color_text
        if cord == None:
            #cord = (0.05 + int(random.random() * 0.9 * 500) / 500, 
            #        0.05 + int(random.random() * 0.9 * 500) / 500)
            r = random.random() ** 0.5 * 0.45
            grad = random.random() * math.pi * 2
            cord = (0.5 + math.sin(grad) * r, 0.5 + math.cos(grad) * r)
        self.cord = cord
        self.cord_layout = cord
        self.rad = rad
        self.related = []


class iGraph:
    def __init__(self, vertex, edges):
        self.vertex = []
        self.edges = []
        print(vertex)
        print(edges)
        for i in range(len(vertex)):
            self.vertex.append(iVertex(key=i, value=vertex[i]))
        for i in range(len(edges)):
            self.edges.append(iEdge(key=i, vertex1=edges[i][0], 
                                    vertex2=edges[i][1]))
            self.vertex[edges[i][0]].related.append(self.vertex[edges[i][1]])
            self.vertex[edges[0][1]].related.append(self.vertex[edges[i][0]])

class iLayout:
    def __init__(self, size=(720, 720), fps=30):
        self.size = size
        self.fps = fps
        self.colors = {
            'white': (245, 245, 245),
            'gray': (158, 158, 158),
            'light_gray': (224, 224, 224),
            'red': (244, 67, 54),
            'blue': (63, 81, 181),
            'black': (33, 33, 33),
            'green': (76, 175, 80)
            }
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('iGraph')

    def vizualizate(self, graph):
        self.running = True
        self.graph = graph
        self.arrange()
        self.optimaze_arrange_random()
        self.scaling()
        self.myfont = pygame.font.SysFont('monospace', 15)
        self.render_label()
        
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.draw()
            pygame.display.flip()
            clock.tick(self.fps)
        pygame.quit()
    
    def arrange(self):
        vertex = self.graph.vertex
        hitboxs = list()
        for vert in vertex:
            x = vert.cord[0]
            y = vert.cord[1]
            r = vert.rad / min(self.size)
            loop = True
            while loop:
                loop = False
                for htb in hitboxs:
                    if (htb[0] - x) ** 2 + (htb[1] - y) ** 2 <= (r + htb[2]) ** 2 * 1.5:
                        loop = True
                        break
                if loop == True:
                    rad = random.random() ** 0.5 * 0.45
                    grad = random.random() * math.pi * 2
                    x = 0.5 + math.sin(grad) * rad
                    y = 0.5 + math.cos(grad) * rad
                else:
                    vert.cord = (x, y)
                    hitboxs.append([x, y, r])

    def optimaze_arrange_random(self, quality = 2):
        vertex = self.graph.vertex
        for i in range(len(vertex) ** quality):
            v1 = random.randint(0, len(vertex) - 1)
            v2 = v1
            while v1 == v2: 
                v2 = random.randint(0, len(vertex) - 1)
            tens1 = 0
            for vert in vertex[v1].related:
                tens1 += (vertex[v1].cord[0] - vert.cord[0]) ** 2 + (vertex[v1].cord[1] - vert.cord[1]) ** 2
            for vert in vertex[v2].related:
                tens1 += (vertex[v2].cord[0] - vert.cord[0]) ** 2 + (vertex[v2].cord[1] - vert.cord[1]) ** 2
            
            tens2 = 0
            for vert in vertex[v1].related:
                tens2 += (vertex[v2].cord[0] - vert.cord[0]) ** 2 + (vertex[v2].cord[1] - vert.cord[1]) ** 2
            for vert in vertex[v2].related:
                tens2 += (vertex[v1].cord[0] - vert.cord[0]) ** 2 + (vertex[v1].cord[1] - vert.cord[1]) ** 2
            if tens2 < tens1:
                vertex[v1].cord, vertex[v2].cord = vertex[v2].cord, vertex[v1].cord

    def render_label(self):
        for vert in self.graph.vertex:
            if vert.value != None:
                vert.label = self.myfont.render(vert.value, 1, self.colors[vert.color_text])
    
    def scaling(self):
        for vert in self.graph.vertex:
            vert.cord_layout = (int(vert.cord[0] * self.size[0]), int(vert.cord[1] * self.size[1]))
    
    def set_color(self, rgb):
        color = pygame.Color(0, 0, 0, 0)
        color.r = rgb[0]
        color.g = rgb[1]
        color.b = rgb[2]
        color.a = 255
        return color
    
    def get_color(self, name_color):
        if name_color in self.colors:
            return self.set_color(self.colors[name_color])
        else:
            return self.set_color(self.colors['black'])

    def draw(self):
        self.screen.fill(self.get_color('white'))
        for i in range(len(self.graph.edges)):
            edge = self.graph.edges[i]
            pygame.draw.line(self.screen, self.get_color(edge.color), 
                             self.graph.vertex[edge.vertex1].cord_layout,
                             self.graph.vertex[edge.vertex2].cord_layout)
        for i in range(len(self.graph.vertex)):
            vert = self.graph.vertex[i]
            pygame.draw.circle(self.screen, self.get_color(vert.color), vert.cord_layout, vert.rad, 0)
            pygame.draw.circle(self.screen, self.get_color(vert.color_edge), vert.cord_layout, vert.rad, 1)
            if vert.label != None:
                self.screen.blit(vert.label, (vert.cord_layout[0] - (len(vert.value) * 9) / 2, vert.cord_layout[1] + vert.rad + 2)) 


'''if __name__ == '__main__':
    graph = iGraph(['123456789', 1, 2, 3], [(1, 2), (2, 3), (3, 1)])
    layout = iLayout()
    layout.vizualizate(graph)'''