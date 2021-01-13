import pygame
import pytmx
import collections
import random
import sys
import os
import sqlite3

FPS = 70
SIZE = WIDTH, HEIGHT = 600, 350

IMAGES_DIR = "images"
MAPS_DIR = 'maps'

pygame.init()
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()

tile_width, tile_height = 32, 32

VH = 4
VW = 4


# количество пикселей передвижения за одни кадр по каждой оси
# обязательно должно быть делителем размера тайла


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


LEVEL_NAMES = {1: 'example_map_2', 2: 'example_map', 3: 'example_map_2', 4: 'example_map',
               5: 'example_map_2', 6: 'example_map', 7: 'example_map_2', 8: 'example_map',
               9: 'example_map_2', 10: 'example_map'}
LEVEL_COUNT = 10

HERO_NAMES = ['hero1', 'hero2', 'hero3']

# хранение раскадровки каждого перса
HERO_IMAGES = collections.defaultdict(dict)

HERO_IMAGES['hero1'] = {'down': [pygame.transform.scale(load_image("hero1/run1.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero1/run2.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero1/run3.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero1/run4.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero1/run5.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero1/run6.png"), (tile_width, tile_height))],
                        'up': [pygame.transform.scale(load_image("hero1/run11.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero1/run21.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero1/run31.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero1/run41.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero1/run51.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero1/run61.png"), (tile_width, tile_height))],
                        'state': pygame.transform.scale(load_image("hero1/hero.png"), (tile_width, tile_height)),
                        'frame': 2}

HERO_IMAGES['hero2'] = {'down': [pygame.transform.scale(load_image("hero2/run1.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero2/run2.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero2/run3.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero2/run4.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero2/run5.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero2/run6.png"), (tile_width, tile_height))],
                        'up': [pygame.transform.scale(load_image("hero2/run11.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero2/run21.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero2/run31.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero2/run41.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero2/run51.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero2/run61.png"), (tile_width, tile_height))],
                        'state': pygame.transform.scale(load_image("hero2/hero.png"), (tile_width, tile_height)),
                        'frame': 2}

HERO_IMAGES['hero3'] = {'down': [pygame.transform.scale(load_image("hero3/run1.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero3/run2.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero3/run3.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero3/run4.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero3/run5.png"), (tile_width, tile_height)),
                                 pygame.transform.scale(load_image("hero3/run6.png"), (tile_width, tile_height))],
                        'up': [pygame.transform.scale(load_image("hero3/run11.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero3/run21.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero3/run31.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero3/run41.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero3/run51.png"), (tile_width, tile_height)),
                               pygame.transform.scale(load_image("hero3/run61.png"), (tile_width, tile_height))],
                        'state': pygame.transform.scale(load_image("hero3/hero.png"), (tile_width, tile_height)),
                        'frame': 2}

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()

# множитель монет
COINS_PER_LEVEL = 10

# переменные для работы с БД
con = sqlite3.connect("players/players.db")
cur = con.cursor()
# имя игрока
nickname = 'asdf'
# id игрока
player_id = cur.execute("SELECT id FROM players_info WHERE nickname = ?", (nickname,)).fetchone()[0]
# финансовое состояние игрока
coins_status = cur.execute("SELECT money FROM players_info WHERE nickname = ?", (nickname,)).fetchone()[0]

hero_name = 'hero1'

# состояние пройденности уровней
level_statuses = {}
levels_db = cur.execute("SELECT levels FROM players_info WHERE nickname = ?", (nickname,)).fetchone()[0].split(';')
try:
    levels_db = list(map(int, levels_db))
except ValueError:
    levels_db = []

for e in levels_db:
    level_statuses[e] = True

if levels_db:
    if max(levels_db) < LEVEL_COUNT:
        level_statuses[max(levels_db) + 1] = False
else:
    level_statuses[1] = False

for i in range(1, LEVEL_COUNT + 1):
    if i not in level_statuses:
        level_statuses[i] = None


def terminate():
    pygame.quit()
    sys.exit()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, hero_name):
        super().__init__(player_group, all_sprites)

        # выбор группы изображений
        self.all_images = HERO_IMAGES[hero_name]
        self.now_images = self.all_images['down']
        self.info_img = {'index': 0, 'step': 1, 'frame': 0, 'score': self.all_images['frame']}

        self.image = self.now_images[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)

        # суммарный сдвиг камеры
        self.dx = 0
        self.dy = 0

        # обозначение куда сейчас идет персонаж
        self.d = {'up': 1, 'down': 2}
        self.now = self.d['down']

    # сработал сигнал смены направления движения
    def press(self):
        if self.rect.y % tile_height == 0:
            y = self.rect.y // tile_height
            x1 = (self.rect.x - self.dx) // tile_width
            x2 = (self.rect.x - self.dx + tile_width - 1) // tile_width
            if self.now == self.d['up']:
                if not level.is_free((x1, y - 1)) or not level.is_free((x2, y - 1)):
                    pass
                else:
                    return
            else:
                if not level.is_free((x1, y + 1)) or not level.is_free((x2, y + 1)):
                    pass
                else:
                    return
        else:
            return

        if self.now == self.d['up']:
            self.now = self.d['down']

            # замена группы кадров
            self.info_img = {'index': 0, 'step': 1, 'frame': 0, 'score': self.all_images['frame']}
            self.now_images = self.all_images['down']
            self.image = self.now_images[0]
        else:
            self.now = self.d['up']

            # замена группы кадров
            self.info_img = {'index': 0, 'step': 1, 'frame': 0, 'score': self.all_images['frame']}
            self.now_images = self.all_images['up']
            self.image = self.now_images[0]

    def update(self):
        # перемецение персонажа по вертикали если это возможно
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

        # перемецение персонажа по горизонтали если это возможно
        if (self.rect.x - self.dx + tile_width) % tile_width == 0:
            x = (self.rect.x - self.dx + tile_width) // tile_width
            y1 = self.rect.y // tile_height
            y2 = (self.rect.y + tile_height - 1) // tile_height
            if level.is_free((x, y1)) and level.is_free((x, y2)):
                self.rect = self.rect.move(VW, 0)
        else:
            self.rect = self.rect.move(VW, 0)

            # замена кадра
        if self.info_img['frame'] == self.info_img['score']:
            self.info_img['index'] += self.info_img['step']
            self.info_img['frame'] = -1
        self.info_img['frame'] += 1
        if self.info_img['index'] > len(self.now_images) - 1:
            self.info_img['index'] = len(self.now_images) - 1
            self.info_img['step'] = -1
        elif self.info_img['index'] < 0:
            self.info_img['index'] = 0
            self.info_img['step'] = 1
        self.image = self.now_images[self.info_img['index']]

    # возвращает координаты тайла, на котором находится
    def get_position(self):
        return (self.rect.x - self.dx) // tile_width, self.rect.y // tile_height

    # возвращает абсолютные координаты
    def get_screen_position(self):
        return self.rect.x + tile_width, self.rect.y + tile_height

    # фиксирует передвижение камеры
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


class LevelMap:
    def __init__(self, filename, free_tile, finish_tile):
        global tile_height, tile_width
        self.map = pytmx.load_pygame(f"{MAPS_DIR}/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tile
        self.finish_tile = finish_tile
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
    def __init__(self, level, hero, camera, level_number):
        self.is_pause = False

        self.level = level
        self.hero = hero
        self.camera = camera
        self.buttons = {'again': Button((550, 320), (30, 30), ['restart_btn.png']),
                        'pause': Button((500, 320), (30, 30), ['pause_btn.png', 'play_btn.png']),
                        'menu': Button((20, 320), (30, 30), ['menu_btn.png'])}

        font = pygame.font.Font(None, 25)
        self.text = font.render(f"Уровень {level_number}", True, (100, 100, 100))

    def render(self, screen):
        self.level.render(screen)
        all_sprites.draw(screen)
        for btn in self.buttons:
            self.buttons[btn].render(screen)
        screen.blit(self.text, ((WIDTH - self.text.get_width()) // 2, 330))

    def update(self):
        if not self.is_pause:
            self.hero.update()
            self.camera.update(self.hero, self.level)
            self.camera.apply(self.hero)
            self.camera.update_map(self.level)

    def check_buttons(self, pos):
        if self.buttons['again'].get_click(pos):
            return 1
        if self.buttons['pause'].get_click(pos):
            self.is_pause = not self.is_pause
            return 2
        if self.buttons['menu'].get_click(pos):
            return 3
        return None

    def move_hero(self):
        if not self.is_pause:
            self.hero.press()

    def check_win(self):
        return self.level.get_tile_id(self.hero.get_position()) == self.level.finish_tile

    def check_lose(self):
        return self.hero.get_screen_position()[0] <= 0


class Button:
    def __init__(self, pos, size, image_names):
        self.pos = pos
        self.size = size
        self.images = []
        self.ind_image = 0
        for name in image_names:
            self.images.append(pygame.transform.scale(load_image(name), self.size))

        self.image = self.images[self.ind_image]

    def get_click(self, pos):
        if self.pos is None or self.size is None:
            return
        if self.pos[0] <= pos[0] <= (self.pos[0] + self.size[0]) \
                and self.pos[1] <= pos[1] <= (self.pos[1] + self.size[1]):
            self.on_click()
            return True
        else:
            return None

    def render(self, screen):
        if self.image:
            screen.blit(self.image, self.pos)

    def on_click(self):
        self.ind_image += 1
        if self.ind_image >= len(self.images):
            self.ind_image = 0
        self.image = pygame.transform.scale(self.images[self.ind_image], self.size)


# выводит в указанной позиции финансы игрока
class CoinsStatus:
    def __init__(self, pos):
        self.pos = pos
        self.icon_size = 20, 20
        self.text_size = 50, 20

    def render(self, screen):
        image = pygame.Surface((self.icon_size[0] + self.text_size[0], self.icon_size[1] + self.text_size[1]),
                                    pygame.SRCALPHA, 32)
        image.blit(pygame.transform.scale(load_image('coins.png'), self.icon_size), (0, 0))
        font = pygame.font.Font(None, 20)
        text = font.render(f"{coins_status}", True, (0, 0, 0))
        x = (self.text_size[0] - text.get_width()) // 2
        y = (self.text_size[1] - text.get_height()) // 2
        image.blit(text, (x + self.icon_size[0], y))
        screen.blit(image, self.pos)


# иконки уровней в меню
class LevelIcon:
    images = {'table': load_image('level.png'), 'unlock': load_image('unlock.png'), 'lock': load_image('lock.png')}

    def __init__(self, number, status, pos, size):
        font = pygame.font.Font(None, 26)
        text = font.render(f"{number}", True, (200, 20, 0))
        x = (size[0] - text.get_width()) // 2
        y = (size[1] - text.get_height()) // 2
        if status:
            self.image = pygame.transform.scale(LevelIcon.images['table'], size)
        elif status is None:
            self.image = pygame.transform.scale(LevelIcon.images['lock'], size)
            y += size[1] / 6
        else:
            self.image = pygame.transform.scale(LevelIcon.images['unlock'], size)
            y += size[1] / 6

        self.image.blit(text, (x, y))

        self.pos = pos
        self.number = number
        self.size = size
        self.status = status

    def render(self, screen):
        screen.blit(self.image, self.pos)

    def get_click(self, pos):
        if self.pos is None or self.size is None or self.status is None:
            return False
        if self.pos[0] <= pos[0] <= (self.pos[0] + self.size[0]) \
                and self.pos[1] <= pos[1] <= (self.pos[1] + self.size[1]):
            return True
        else:
            return False


# меню с уровнями
class LevelMenu:
    def __init__(self, level_icons):
        self.level_icons = level_icons
        self.buttons = {'shop': Button(pos=(540, 10), size=(35, 35), image_names=['shop_btn.png']),
                        'mainmenu': Button(pos=(220, 10), size=(150, 30), image_names=['mainmenu_btn.png'])}
        self.coins = CoinsStatus((20, 20))

    def render(self, screen):
        for obj in self.level_icons:
            obj.render(screen)
        for btn in self.buttons:
            self.buttons[btn].render(screen)
        self.coins.render(screen)

    def get_click(self, pos):
        for obj in self.level_icons:
            if obj.get_click(pos):
                return obj.number
        if self.buttons['shop'].get_click(pos):
            return LEVEL_COUNT + 1
        elif self.buttons['mainmenu'].get_click(pos):
            return LEVEL_COUNT + 2


# функция, реализующая меню с уровнями
def level_menu():
    global level_statuses

    all_sprites.empty()
    screen.fill((245, 245, 220))

    level_icons = []

    for i in range(LEVEL_COUNT):
        size = (80, 80)
        delta = (30, 50)
        left = (WIDTH - size[0] * 5 - delta[0] * 4) // 2
        top = 70
        x = left + (i % 5) * size[0] + i % 5 * delta[0]
        y = top + (i // 5) * size[1] + i // 5 * delta[1]
        level_icons.append(LevelIcon(i + 1, level_statuses[i + 1], (x, y), size))

    menu = LevelMenu(level_icons)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = menu.get_click(event.pos)
                if res in range(1, LEVEL_COUNT + 1):
                    return in_level(res)
                    # переход в уровень
                if res == LEVEL_COUNT + 1:
                    return shop_menu()
                    # переход в магазин
                elif res == LEVEL_COUNT + 2:
                    # переход в главное меню
                    pass

        screen.fill((245, 245, 220))

        menu.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


# магазин
class Shop:
    def __init__(self):
        self.pos = 1
        self.length = len(cur.execute("SELECT skin_id FROM store").fetchall())
        self.skins = cur.execute("SELECT skins FROM players_info WHERE nickname = ?", (nickname,)).fetchone()[0]
        self.buttons = {'mainmenu': Button(pos=(220, 10), size=(150, 30), image_names=['mainmenu_btn.png']),
                        'previous': Button(pos=(50, 150), size=(60, 60), image_names=['previous_btn.png']),
                        'next': Button(pos=(500, 150), size=(60, 60), image_names=['next_btn.png']),
                        'menu': Button((530, 10), (45, 45), ['menu_btn.png']),
                        'buy': None,
                        'choose': None}
        self.coins = CoinsStatus((20, 20))
        self.image = HERO_IMAGES['hero1']['state']

    def can_buy(self):
        if 'hero{}'.format(self.pos) not in self.skins.split(';'):
            price = \
            cur.execute("SELECT price FROM store WHERE skin_id LIKE ?", ('hero{}'.format(self.pos),)).fetchone()[0]
            if price <= coins_status:
                return True, 'Можно купить', price
            return None, 'Недостаточно монет'
        return False, 'Уже куплен'

    def get_click(self, pos):
        if self.buttons['mainmenu'].get_click(pos):
            pass
        if self.buttons['previous'].get_click(pos):
            return 1
        if self.buttons['next'].get_click(pos):
            return 2
        if self.buttons['buy'] and self.buttons['buy'].get_click(pos):
            return 3
        if self.buttons['choose'] and self.buttons['choose'].get_click(pos):
            return 4
        if self.buttons['menu'].get_click(pos):
            return 5

    def render(self, screen):
        if self.can_buy()[0] == False:
            self.buttons['buy'] = None
            self.buttons['choose'] = Button(pos=(260, 235), size=(80, 20), image_names=['choose_btn.png'])
        else:
            self.buttons['choose'] = None
            self.buttons['buy'] = Button(pos=(260, 235), size=(80, 20), image_names=['buy_btn.png'])

        screen.blit(pygame.transform.scale(load_image('table.png'), (300, 200)), (160, 100))
        for btn in self.buttons:
            if self.buttons[btn]:
                self.buttons[btn].render(screen)
        font = pygame.font.Font(None, 20)
        text = font.render('Название: {}'.format(
            cur.execute("SELECT skin_name FROM store WHERE skin_id LIKE ?", ('hero{}'.format(self.pos),)).fetchone()[
                0]), True, (0, 0, 0))
        screen.blit(text, (185, 140))
        text = font.render('Цена: {}'.format(
            cur.execute("SELECT price FROM store WHERE skin_id LIKE ?", ('hero{}'.format(self.pos),)).fetchone()[0]),
                           True, (0, 0, 0))
        screen.blit(text, (185, 160))
        screen.blit(pygame.transform.scale(load_image('coins.png'), (10, 10)), (185 + text.get_width() + 2, 160))
        text = font.render(self.can_buy()[1], True, (0, 0, 0))
        screen.blit(text, (185, 180))
        if f"hero{self.pos}" == hero_name:
            text = font.render('Выбран', True, (0, 0, 0))
            screen.blit(text, (185, 200))
        screen.blit(self.image, (350, 175))
        self.coins.render(screen)


# функция, реализующая магазин
def shop_menu():
    global coins_status, hero_name
    shop = Shop()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = shop.get_click(event.pos)
                if res == 0:
                    return
                    # вернуться в меню
                if res == 1:
                    if shop.pos > 1:
                        shop.pos -= 1
                        shop.image = HERO_IMAGES['hero{}'.format(shop.pos)]['state']
                    # предыдущий предмет
                if res == 2:
                    if shop.pos < shop.length:
                        shop.pos += 1
                        shop.image = HERO_IMAGES['hero{}'.format(shop.pos)]['state']
                    # следующий предмет
                if res == 3:
                    price = shop.can_buy()
                    if price[0]:
                        coins_status -= price[2]
                        shop.skins += ';{}'.format('hero{}'.format(shop.pos))
                        cur.execute("UPDATE players_info SET skins = ? WHERE id = ?", (shop.skins, player_id))
                        cur.execute("UPDATE players_info SET money = ? WHERE id = ?", (coins_status, player_id))
                        con.commit()
                    # купить предмет
                if res == 4:
                    hero_name = f"hero{shop.pos}"
                if res == 5:
                    return level_menu()
        screen.fill((245, 245, 220))
        shop.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


# процесс игры в уровне
def in_level(level_number):
    global level, hero, camera, game, coins_status, hero_name

    level_name = LEVEL_NAMES[level_number]

    with open(f'{MAPS_DIR}/{level_name}.txt') as file:
        free_tiles = list(map(int, file.readline().split()))
        target_tile = list(map(int, file.readline().split()))[0]

    all_sprites.empty()
    screen.fill((0, 0, 0))

    level = LevelMap(f'{level_name}.tmx', free_tiles, target_tile)
    hero = Player(0, 8, hero_name)
    camera = Camera()
    game = Game(level, hero, camera, level_number)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.move_hero()
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = game.check_buttons(event.pos)
                if res == 1:
                    all_sprites.empty()
                    level = LevelMap(f'{level_name}.tmx', free_tiles, target_tile)
                    hero = Player(0, 8, hero_name)
                    camera = Camera()
                    game = Game(level, hero, camera, level_number)
                    break
                elif res == 2:
                    pass
                elif res == 3:
                    return level_menu()
                    # переход в меню с уровнями

        screen.fill((245, 245, 220))

        game.update()

        game.render(screen)

        if game.check_win():
            added_coins = 0
            if not level_statuses[level_number]:
                added_coins = level_number * COINS_PER_LEVEL
                coins_status += added_coins
                cur.execute("UPDATE players_info SET money = ? WHERE id = ?", (coins_status, player_id))
                con.commit()
            level_statuses[level_number] = True
            cur.execute("UPDATE players_info SET levels = ? WHERE id = ?",
                        (';'.join([str(i) for i in level_statuses if level_statuses[i]]), player_id))
            con.commit()
            if level_number < LEVEL_COUNT and not level_statuses[level_number + 1]:
                level_statuses[level_number + 1] = False
            is_win = True
            return level_over(level_number, is_win, added_coins)
        if game.check_lose():
            is_win = False
            return level_over(level_number, is_win, None)

        pygame.display.flip()
        clock.tick(FPS)


# конец уровня
class LevelOver:
    def __init__(self, level_number, is_win, added_coins=None):
        self.level_number = level_number
        self.coins = CoinsStatus((50, 40))
        self.added_coins = added_coins

        self.size = (500, 300)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        fon = pygame.transform.scale(load_image('table.png'), self.size)
        x = (WIDTH - fon.get_width()) // 2
        y = (HEIGHT - fon.get_height()) // 2
        self.pos = (x, y)
        self.image.blit(fon, (0, 0))

        self.buttons = {'again': Button((220 + x, 200 + y), (40, 40), ['restart_btn.png']),
                        'menu': Button((100 + x, 200 + y), (40, 40), ['menu_btn.png']),
                        'next': Button((340 + x, 200 + y), (40, 40), ['next_btn.png'])}
        if level_number == LEVEL_COUNT or level_statuses[level_number + 1] is None:
            self.buttons['next'] = None

        if is_win:
            message = f"Уровень {level_number} пройден!"
        else:
            message = f"Уровень {level_number} провален."

        font = pygame.font.Font(None, 50)
        text = font.render(message, True, (0, 0, 0))
        x = (self.size[0] - text.get_width()) // 2
        y = 90
        self.image.blit(text, (x, y))

        if added_coins:
            font = pygame.font.Font(None, 20)
            x += text.get_width()
            y += text.get_height() + 10
            text = font.render(f"+{self.added_coins}", True, (0, 0, 0))
            x -= text.get_width() + 20
            self.image.blit(text, (x, y))
            self.image.blit(pygame.transform.scale(load_image('coins.png'),
                                                   (20, 20)), (x + text.get_width() + 5, y))

        self.coins.render(self.image)

    def render(self, screen):
        screen.blit(self.image, self.pos)

        for btn in self.buttons:
            if self.buttons[btn]:
                self.buttons[btn].render(screen)

    def get_click(self, pos):
        if self.buttons['menu'].get_click(pos):
            return LEVEL_COUNT + 1
        elif self.buttons['again'].get_click(pos):
            return LEVEL_COUNT + 2
        elif self.buttons['next'] and self.buttons['next'].get_click(pos):
            return LEVEL_COUNT + 3


# конец уровня
def level_over(level_number, is_win, added_coins=None):
    all_sprites.empty()
    screen.fill((0, 0, 0))

    window = LevelOver(level_number, is_win, added_coins)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = window.get_click(event.pos)
                if res == LEVEL_COUNT + 1:
                    return level_menu()
                    # переход в меню с уровнями
                elif res == LEVEL_COUNT + 2:
                    return in_level(level_number)
                    # перезапуск уровня
                elif res == LEVEL_COUNT + 3:
                    return in_level(level_number + 1)
                    # следующий уровень

        screen.fill((245, 245, 220))
        window.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


class ScoreTable:
    def __init__(self):
        self.buttons = {'mainmenu': Button(pos=(10, 300), size=(45, 45), image_names=['previous_btn.png'])}
        self.best = []
        db = list(cur.execute("SELECT nickname, levels FROM players_info").fetchall())
        score = []
        for i in range(len(db)):
            if not db[i][1]:
                score.append((db[i][0], 0))
            else:
                score.append((db[i][0], len(db[i][1].split(';'))))
        score = sorted(score, key=lambda x: x[1])[::-1]
        res = sorted(list(set(list(map(lambda x: x[1], score)))))[::-1]
        i = 0
        while len(self.best) < 5 and i < len(res):
            if res[i] != 0:
                a = list(filter(lambda x: x[1] == res[i], score))
                self.best.extend(a)
            i += 1

    def render(self, screen):
        font = pygame.font.Font(None, 40)
        text = font.render('Таблица рекордов', True, (100, 100, 100))
        x = (WIDTH - text.get_width()) // 2
        screen.blit(text, (x, 10))

        if not self.best:
            font = pygame.font.Font(None, 25)
            text = font.render('Здесь пока нет рекордов', True, (150, 150, 150))
            x = (WIDTH - text.get_width()) // 2
            screen.blit(text, (x, 100))
            return

        width_col0, width_col1, width_col2 = 100, 150, None
        left, top = 60, 70
        delta_y = 20
        y = top

        font = pygame.font.Font(None, 25)
        text = font.render('Номер', True, (0, 0, 0))
        x = (width_col0 - text.get_width()) // 2
        screen.blit(text, (x + left, y))
        text = font.render('Ник', True, (0, 0, 0))
        x = (width_col1 - text.get_width()) // 2
        screen.blit(text, (x + left + width_col0, y))
        font = pygame.font.Font(None, 20)
        text = font.render('Количество пройденных уровней', True, (0, 0, 0))
        screen.blit(text, (left + width_col0 + width_col1, y))
        width_col2 = text.get_width()
        y += text.get_height() + delta_y

        len_line_x = width_col0 + width_col1 + width_col2 + 5
        pygame.draw.line(screen, (0, 0, 0), (left, top - 5), (left + len_line_x, top - 5))
        pygame.draw.line(screen, (0, 0, 0), (left, y - delta_y // 2), (left + len_line_x, y - delta_y // 2))

        font = pygame.font.Font(None, 25)
        i = 1
        for nick, count in self.best:
            text = font.render(str(i), True, (50, 50, 50))
            screen.blit(text, (left + 30, y))
            text = font.render(nick, True, (50, 50, 50))
            screen.blit(text, (left + width_col0 + 10, y))
            text = font.render(str(count), True, (50, 50, 50))
            screen.blit(text, (left + width_col0 + width_col1 + 10, y))
            y += text.get_height() + delta_y
            pygame.draw.line(screen, (30, 30, 30), (left, y - delta_y // 2), (left + len_line_x, y - delta_y // 2))
            if y + text.get_height() > HEIGHT:
                break
            i += 1

        for btn in self.buttons:
            self.buttons[btn].render(screen)

    def get_click(self, pos):
        if self.buttons['mainmenu'].get_click(pos):
            return 1


def score_table():
    screen.fill((245, 245, 220))

    table = ScoreTable()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = table.get_click(event.pos)
                if res == 1:
                    # переход в главное меню
                    pass

        screen.fill((245, 245, 220))
        table.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    screen.fill((0, 0, 0))

    level_menu()

    # score_table()


if __name__ == '__main__':
    main()