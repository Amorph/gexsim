import pygame

# Define the colors we will use in RGB format
from utils.vector2 import Vector2
from view.base import BaseView

screen = None
clock = None
renderer = None
textImg = None


class PyGameView(BaseView):
    BLACK = (127, 127, 127)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    def __init__(self, properties):
        super(PyGameView, self).__init__()

        pygame.init()
        self.clock = pygame.time.Clock()

        # Set the height and width of the screen
        size = properties['size']
        self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.RESIZABLE)

        pygame.display.set_caption(properties['name'])

        font = pygame.font.SysFont(None, 24)  # pygame.font.Font(None, 18)
        text = """Press SPACE BAR to start"""
        self.textImg = font.render(text, 1, (255, 0, 0))

    def destroy(self):
        pygame.quit()

    def sleep(self, milliseconds):
        self.clock.tick(milliseconds)

    def update(self) -> bool:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                self.on_key_down(event.key, event.mod)
            elif event.type == pygame.KEYUP:
                self.on_key_up(event.key, event.mod)
        return True

    def start_frame(self):
        self.screen.fill((0, 0, 0))

    def finish_frame(self):
        pygame.display.flip()

    def draw_line(self, start, end, color):
        pygame.draw.line(self.screen, self.convert_color(color),
                         self.convert_position(start), self.convert_position(end))

    def draw_quad(self, leftTop, size, color):
        di_lt = self.convert_position(leftTop)
        di_rb = self.convert_position(leftTop + size)

        pygame.draw.rect(self.screen, self.convert_color(color), [di_lt[0], di_lt[1],
                                                             di_rb[0] - di_lt[0], di_rb[1] - di_lt[1]])

    def convert_position(self, world: Vector2) -> list:
        return [world.x * 6, world.y * 6]

    def convert_color(self, color) -> tuple:
        return color.x * 255, color.y * 255, color.z * 255


def init(properties):
    global screen, textImg, clock

    pygame.init()
    clock = pygame.time.Clock()

    # Set the height and width of the screen
    size = properties['size']
    screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.RESIZABLE)

    pygame.display.set_caption(properties['name'])

    font = pygame.font.SysFont(None, 24)  # pygame.font.Font(None, 18)
    text = """Press SPACE BAR to start"""
    textImg = font.render(text, 1, (255, 0, 0))


def sleep(milliseconds):
    global clock
    clock.tick(milliseconds)


def update():
    global screen
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            return False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            print('sdfsdfsdf', str(event))
    return True


def draw(scene):
    pass
    # #
    # # Clear the screen and set the screen background
    # screen.fill((0,0,0))
    #
    # # Draw on the screen a GREEN line from (0,0) to (50.75)
    # # 5 pixels wide.
    # pygame.draw.line(screen, GREEN, [0, 0], [50, 30], 5)
    #
    # # Draw on the screen a GREEN line from (0,0) to (50.75)
    # # 5 pixels wide.
    # pygame.draw.lines(screen, BLACK, False, [[0, 80], [50, 90], [200, 80], [220, 30]], 5)
    #
    # # Draw on the screen a GREEN line from (0,0) to (50.75)
    # # 5 pixels wide.
    # pygame.draw.aaline(screen, GREEN, [0, 50], [50, 80], True)
    #
    # # Draw a rectangle outline
    # pygame.draw.rect(screen, BLACK, [75, 10, 50, 20], 2)
    #
    # # Draw a solid rectangle
    # pygame.draw.rect(screen, BLACK, [150, 10, 50, 20])
    #
    # # Draw an ellipse outline, using a rectangle as the outside boundaries
    # pygame.draw.ellipse(screen, RED, [225, 10, 50, 20], 2)
    #
    # # Draw an solid ellipse, using a rectangle as the outside boundaries
    # pygame.draw.ellipse(screen, RED, [300, 10, 50, 20])
    #
    # # This draws a triangle using the polygon command
    # pygame.draw.polygon(screen, BLACK, [[100, 100], [0, 200], [200, 200]], 5)
    #
    # # Draw an arc as part of an ellipse.
    # # Use radians to determine what angle to draw.
    # pygame.draw.arc(screen, BLACK, [210, 75, 150, 125], 0, pi / 2, 2)
    # pygame.draw.arc(screen, GREEN, [210, 75, 150, 125], pi / 2, pi, 2)
    # pygame.draw.arc(screen, BLUE, [210, 75, 150, 125], pi, 3 * pi / 2, 2)
    # pygame.draw.arc(screen, RED, [210, 75, 150, 125], 3 * pi / 2, 2 * pi, 2)
    #
    # # Draw a circle
    # pygame.draw.circle(screen, BLUE, [60, 250], 40)
    # screen.blit(textImg, (0, 0))
    # # self.window.blit(self.background, (0, 0))
    #
    # # Go ahead and update the screen with what we've drawn.
    # # This MUST happen after all the other drawing commands.
    # pygame.display.flip()


def destroy():
    pygame.quit()
