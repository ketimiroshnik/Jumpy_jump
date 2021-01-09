import pygame
import pytmx
import sys
import os

FPS = 40
SIZE = WIDTH, HEIGHT = 600, 320

IMAGES_DIR = "images"
MAPS_DIR = 'maps'

pygame.init()
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()

tile_width, tile_height = 32, 32


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join(IMAGES_DIR, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (50, 70, 0))
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10,
                                              text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


class Player(pygame.sprite.Sprite):
    images = {'down': pygame.transform.scale(load_image("hero_down.png"), (tile_width, tile_height)),
              'up': pygame.transform.scale(load_image("hero_up.png"), (tile_width, tile_height))}

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.images = Player.images
        self.image = self.images['down']
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.dx = 0
        self.dy = 0
        self.d = {'up': 1, 'down': 2}
        self.now = self.d['down']

    def press(self):
        if self.now == self.d['up']:
            self.now = self.d['down']
            self.image = self.images['down']
        else:
            self.now = self.d['up']
            self.image = self.images['up']

    def update(self):
        if self.now == self.d['up']:
            if self.rect.y % tile_height == 0:
                y = self.rect.y // tile_height
                x1 = (self.rect.x - self.dx) // tile_width
                x2 = (self.rect.x - self.dx + tile_width - 1) // tile_width
                if level.is_free((x1, y - 1)) and level.is_free((x2, y - 1)):
                    self.rect = self.rect.move(0, -VH)
            else:
                self.rect = self.rect.move(0, -VH)
        elif self.now == self.d['down']:
            if (self.rect.y + tile_height) % tile_height == 0:
                y = (self.rect.y + tile_height) // tile_height
                x1 = (self.rect.x - self.dx) // tile_width
                x2 = (self.rect.x - self.dx + tile_width - 1) // tile_width
                if level.is_free((x1, y)) and level.is_free((x2, y)):
                    self.rect = self.rect.move(0, VH)
            else:
                self.rect = self.rect.move(0, VH)

        if (self.rect.x - self.dx + tile_width) % tile_width == 0:
            x = (self.rect.x - self.dx + tile_width) // tile_width
            y1 = self.rect.y // tile_height
            y2 = (self.rect.y + tile_height - 1) // tile_height
            if level.is_free((x, y1)) and level.is_free((x, y2)):
                self.rect = self.rect.move(VW, 0)
        else:
            self.rect = self.rect.move(VW, 0)

    def get_position(self):
        return (self.rect.x - self.dx) // tile_width, self.rect.y // tile_height

    def get_screen_position(self):
        return self.rect.x + tile_width, self.rect.y + tile_height

    def set_delta(self, x, y):
        self.dx += x
        self.dy += y


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.done = False

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        obj.set_delta(self.dx, self.dy)

    def update(self, hero, level):
        if (hero.rect.x >= WIDTH / 2 or self.done) and ((level.width - 1) * tile_width + level.dx) >= WIDTH:
            self.done = True
            self.dx = -VW
            self.dy = 0
        else:
            self.dx = 0
            self.dy = 0

    def update_map(self, level):
        level.move(self.dx, self.dy)


class Map:
    def __init__(self, filename, free_tile, finish_tile):
        global tile_height, tile_width
        self.map = pytmx.load_pygame(f"{MAPS_DIR}/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tile
        self.finish_tile = finish_tile
        # tile_width = self.width
        # tile_height = self.height
        self.dx = 0
        self.dy = 0

    def move(self, x, y):
        self.dx += x
        self.dy += y

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size + self.dx, y * self.tile_size + self.dy))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles


class Game:
    def __init__(self, level, hero):
        self.level = level
        self.hero = hero

    def render(self, screen):
        self.level.render(screen)
        all_sprites.draw(screen)

    def update(self):
        self.hero.update()

    def move_hero(self):
        self.hero.press()

    def check_win(self):
        return self.level.get_tile_id(self.hero.get_position()) == self.level.finish_tile

    def check_lose(self):
        return self.hero.get_screen_position()[0] <= 0


camera = Camera()

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()

player_image = pygame.transform.scale(load_image("hero_down.png"), (tile_width, tile_height))

VH = 4
VW = 4
# количество пикселей передвижения за одни кадр по каждой оси
# обязательно должно быть делителем размера тайла

if __name__ == '__main__':
    start_screen()

    screen.fill((0, 0, 0))

    level = Map('example_map_2.tmx', [30, 15], 15)
    hero = Player(0, 8)
    game = Game(level, hero)

    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    game.move_hero()

        screen.fill((245, 245, 220))

        if not game_over:
            game.update()
            camera.update(hero, level)
            for sprite in all_sprites:
                camera.apply(sprite)
            camera.update_map(level)

        game.render(screen)

        if game.check_win():
            game_over = True
            show_message(screen, "You won!")
        if game.check_lose():
            game_over = True
            show_message(screen, "You lost!")

        pygame.display.flip()
        clock.tick(FPS)