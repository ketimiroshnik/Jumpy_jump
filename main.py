import pygame
import pytmx
import collections
import random
import sys
import os
import sqlite3

FPS = 60
SIZE = WIDTH, HEIGHT = 600, 350

IMAGES_DIR = "images"
MAPS_DIR = 'maps'
MUSIC_DIR = 'music'
DATA_DIR = 'data'
FONTS_DIR = 'fonts'

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


LEVEL_NAMES = {1: 'map1', 2: 'map2', 3: 'map3', 4: 'map4',
               5: 'map5', 6: 'map6', 7: 'map7', 8: 'map8',
               9: 'map9', 10: 'map10'}

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

nickname = ''
player_id = 0
coins_status = 0
hero_name = ''
# состояние пройденности уровней
level_statuses = {}

# беззвучный режим
quiet = False

# переменные для работы с БД
con = sqlite3.connect(f"{DATA_DIR}/players.db")
cur = con.cursor()

font_name = f'{FONTS_DIR}/font3.ttf'
font_color = (255, 255, 255)

back_image = pygame.transform.scale(load_image('background.jpg'), SIZE)


def player_info(player):
    global nickname, player_id, coins_status, hero_name, level_statuses
    nickname = player
    # id игрока
    player_id = cur.execute("SELECT id FROM players_info WHERE nickname = ?", (nickname,)).fetchone()[0]
    # финансовое состояние игрока
    coins_status = cur.execute("SELECT money FROM players_info WHERE nickname = ?", (nickname,)).fetchone()[0]
    level_statuses = {}
    hero_name = 'hero1'
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


# запускает звук
def play_sound(sound_name):
    if quiet:
        return
    fullname = os.path.join(MUSIC_DIR, sound_name)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    effect = pygame.mixer.Sound(f'{MUSIC_DIR}/{sound_name}')
    effect.play()


# запускает музыку
def play_music(music_name=None):
    if quiet:
        pygame.mixer.music.stop()
        return
    if not music_name:
        pygame.mixer.music.play(-1)
        return
    fullname = os.path.join(MUSIC_DIR, music_name)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    pygame.mixer.music.load(f'{MUSIC_DIR}/{music_name}')
    pygame.mixer.music.play(-1)


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
                        'menu': Button((20, 320), (30, 30), ['menu_btn.png']),
                        'sound': SoundButton(pos=(70, 320), size=(30, 30))}

        font = pygame.font.Font(font_name, 25)
        self.text = font.render(f"Уровень {level_number}", True, font_color)

    def render(self, screen):
        self.level.render(screen)
        all_sprites.draw(screen)
        for btn in self.buttons:
            self.buttons[btn].render(screen)
        screen.blit(self.text, ((WIDTH - self.text.get_width()) // 2, 325))

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
        if self.buttons['sound'].get_click(pos):
            return 4
        return None

    def move_hero(self):
        if not self.is_pause:
            self.hero.press()

    def check_win(self):
        return self.level.get_tile_id(self.hero.get_position()) == self.level.finish_tile

    def check_lose(self):
        return self.hero.get_screen_position()[0] <= 0


class Button:
    def __init__(self, pos, size, image_names, sound=True):
        self.sound = sound
        self.pos = pos
        self.size = size
        self.images = []
        self.ind_image = 0
        for name in image_names:
            self.images.append(pygame.transform.scale(load_image(name), self.size))

        self.image = self.images[self.ind_image]
        self.rect = pygame.Rect(*pos, *size)

    def get_click(self, pos):
        if self.rect.collidepoint(pos):
            play_sound('press_btn.mp3')
            self.on_click()
            return True
        return False

    def render(self, screen):
        if self.image:
            screen.blit(self.image, self.pos)

    def on_click(self):
        self.ind_image += 1
        if self.ind_image >= len(self.images):
            self.ind_image = 0
        self.image = pygame.transform.scale(self.images[self.ind_image], self.size)


# кпока, отвечающая за смену звука
class SoundButton:
    images = {True: load_image('notsound_btn.png'), False: load_image('sound_btn.png')}

    def __init__(self, pos, size):
        self.images = {True: pygame.transform.scale(SoundButton.images[True], size),
                       False: pygame.transform.scale(SoundButton.images[False], size)}
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(*pos, *size)

    def render(self, screen):
        screen.blit(self.images[quiet], self.pos)

    def get_click(self, pos):
        if self.rect.collidepoint(pos):
            play_sound('press_btn.mp3')
            return True
        return False


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
        font = pygame.font.Font(font_name, 20)
        text = font.render(f"{coins_status}", True, font_color)
        x = (self.text_size[0] - text.get_width()) // 2
        y = (self.text_size[1] - text.get_height()) // 2
        image.blit(text, (x + self.icon_size[0], y))
        screen.blit(image, self.pos)


# иконки уровней в меню
class LevelIcon:
    images = {'table': load_image('level.png'), 'unlock': load_image('unlock.png'), 'lock': load_image('lock.png')}

    def __init__(self, number, status, pos, size):
        font = pygame.font.Font(font_name, 26)
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
                        'mainmenu': Button(pos=(220, 10), size=(150, 30), image_names=['mainmenu_btn.png']),
                        'sound': SoundButton(pos=(540, 300), size=(45, 45)),
                        'how_to_play': TextButton(pos=(190, 300), image='help_btn.png', text=' Как играть')}
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
        elif self.buttons['sound'].get_click(pos):
            return LEVEL_COUNT + 3
        elif self.buttons['how_to_play'].get_click(pos):
            return LEVEL_COUNT + 4


# функция, реализующая меню с уровнями
def level_menu():
    global level_statuses, quiet, back_image

    all_sprites.empty()

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
                areyousure(level_menu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = menu.get_click(event.pos)
                if res in range(1, LEVEL_COUNT + 1):
                    play_sound('choose_level.mp3')
                    return in_level(res)
                    # переход в уровень
                if res == LEVEL_COUNT + 1:
                    return shop_menu()
                    # переход в магазин
                elif res == LEVEL_COUNT + 2:
                    return mainmenu()
                    # переход в главное меню
                elif res == LEVEL_COUNT + 3:
                    quiet = not quiet
                    play_music('menu.mp3')
                    # изменить статус тишины
                elif res == LEVEL_COUNT + 4:
                    return howtoplaymenu()
                    # переход в меню с подсказками

        screen.blit(back_image, (0, 0))

        menu.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


# Класс, реализующий меню с обучением
class HowToPlay:
    def __init__(self):
        self.buttons = {'got_it': Button(pos=(275, 300), size=(45, 45), image_names=['ok_btn.png']),
                        'sound': SoundButton(pos=(540, 300), size=(45, 45))}
        self.text = [' Как только Вы запустите  уровень, Ваш персонаж',
                    'и камера начнут  движение.  Ваша цель -  пройти',
                    'уровень,  не  отстав  от  камеры.   В этом  Вам',
                    'будут  мешать  препятствия.   Если  Вы  слишком',
                    'долго  не  будете  двигаться,  застряв  в  них,',
                    'то  проиграете - камера Вас обгонит.  Нажимайте',
                    'ПРОБЕЛ,  чтобы   сменить  гравитацию  и  обойти',
                    'препятствие!']

    def get_click(self, pos):
        if self.buttons['got_it'].get_click(pos):
            return 1
        if self.buttons['sound'].get_click(pos):
            return 2

    def render(self, screen):
        for btn in self.buttons:
            self.buttons[btn].render(screen)
        font = pygame.font.Font(font_name, 35)
        text = font.render('Как играть', True, (200, 200, 200))
        screen.blit(text, (205, 10))
        font = pygame.font.Font(font_name, 22)
        move = 0
        for txt in self.text:
            text = font.render(txt, True, font_color)
            screen.blit(text, (17, 70 + 26 * move))
            move += 1


# Обучающее меню
def howtoplaymenu():
    global quiet
    hint = HowToPlay()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(howtoplaymenu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = hint.get_click(event.pos)
                if res == 1:
                    return level_menu()
                    # возврат в главное меню
                if res == 2:
                    quiet = not quiet
                    play_music('menu.mp3')
                    # изменить статус тишины
        screen.blit(back_image, (0, 0))
        hint.render(screen)
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
                        'choose': None,
                        'sound': SoundButton(pos=(540, 300), size=(45, 45))}
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
            return 0
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
        if self.buttons['sound'].get_click(pos):
            return 6

    def change_image(self):
        self.image = HERO_IMAGES['hero{}'.format(self.pos)]['state']

    def render(self, screen):
        if self.can_buy()[0] == False:
            self.buttons['buy'] = None
            self.buttons['choose'] = Button(pos=(260, 235), size=(80, 20), image_names=['choose_btn.png'], sound=False)
        else:
            self.buttons['choose'] = None
            self.buttons['buy'] = Button(pos=(260, 235), size=(80, 20), image_names=['buy_btn.png'], sound=False)

        screen.blit(pygame.transform.scale(load_image('table.png'), (300, 200)), (160, 100))
        for btn in self.buttons:
            if self.buttons[btn]:
                self.buttons[btn].render(screen)
        font = pygame.font.Font(font_name, 20)
        text = font.render('Название: {}'.format(
            cur.execute("SELECT skin_name FROM store WHERE skin_id LIKE ?", ('hero{}'.format(self.pos),)).fetchone()[
                0]), True, font_color)
        screen.blit(text, (185, 140))
        text = font.render('Цена: {}'.format(
            cur.execute("SELECT price FROM store WHERE skin_id LIKE ?", ('hero{}'.format(self.pos),)).fetchone()[0]),
            True, font_color)
        screen.blit(text, (185, 160))
        screen.blit(pygame.transform.scale(load_image('coins.png'), (10, 10)), (185 + text.get_width() + 2, 160))
        font = pygame.font.Font(font_name, 16)
        text = font.render(self.can_buy()[1], True, font_color)
        screen.blit(text, (185, 180))
        if f"hero{self.pos}" == hero_name:
            text = font.render('Выбран', True, font_color)
            screen.blit(text, (185, 200))
        screen.blit(self.image, (350, 175))
        self.coins.render(screen)


# функция, реализующая магазин
def shop_menu():
    global coins_status, hero_name, quiet, back_image
    shop = Shop()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(shop_menu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = shop.get_click(event.pos)
                if res == 0:
                    return mainmenu()
                    # вернуться в меню
                if res == 1:
                    if shop.pos > 1:
                        shop.pos -= 1
                    # предыдущий предмет
                    else:
                        shop.pos = shop.length
                    # последний в списке предмет
                    shop.change_image()
                    # сменить картинку персонажа
                if res == 2:
                    if shop.pos < shop.length:
                        shop.pos += 1
                        shop.image = HERO_IMAGES['hero{}'.format(shop.pos)]['state']
                    # следующий предмет
                    else:
                        shop.pos = 1
                    # первый в списке предмет
                    shop.change_image()
                    # сменить картинку персонажа
                if res == 3:
                    price = shop.can_buy()
                    if price[0]:
                        coins_status -= price[2]
                        shop.skins += ';{}'.format('hero{}'.format(shop.pos))
                        cur.execute("UPDATE players_info SET skins = ? WHERE id = ?", (shop.skins, player_id))
                        cur.execute("UPDATE players_info SET money = ? WHERE id = ?", (coins_status, player_id))
                        con.commit()
                        play_sound('buy.mp3')
                    elif price[0] is None:
                        play_sound('cannotbuy.mp3')
                    # купить предмет
                if res == 4:
                    hero_name = f"hero{shop.pos}"
                    play_sound('choose_hero.mp3')
                    # выбрать скин
                if res == 5:
                    return level_menu()
                    # вернуться к выбору уровней
                if res == 6:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины
        screen.blit(back_image, (0, 0))
        shop.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


# процесс игры в уровне
def in_level(level_number):
    global level, hero, camera, game, coins_status, hero_name, quiet, back_image

    level_name = LEVEL_NAMES[level_number]

    with open(f'{MAPS_DIR}/{level_name}.txt') as file:
        free_tiles = list(map(int, file.readline().split()))
        target_tile = list(map(int, file.readline().split()))[0]

    all_sprites.empty()

    level = LevelMap(f'{level_name}.tmx', free_tiles, target_tile)
    hero = Player(0, 8, hero_name)
    camera = Camera()
    game = Game(level, hero, camera, level_number)

    music = random.choice(['fon1.mp3', 'fon2.mp3'])
    play_music(music)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(level_menu, terminate)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.move_hero()
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = game.check_buttons(event.pos)
                if res == 1:
                    return in_level(level_number)
                    #  перезапуск уровня
                elif res == 2:
                    pass
                elif res == 3:
                    play_music('menu.mp3')
                    return level_menu()
                    # переход в меню с уровнями
                elif res == 4:
                    quiet = not quiet
                    play_music(music)
                    # изменить статус тишины

        screen.blit(back_image, (0, 0))

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


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 0.1

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        screen_rect = (0, 0, WIDTH, HEIGHT)
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


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
                        'next': Button((340 + x, 200 + y), (40, 40), ['next_btn.png']),
                        'sound': SoundButton(pos=(540, 300), size=(45, 45))}
        if level_number == LEVEL_COUNT or level_statuses[level_number + 1] is None:
            self.buttons['next'] = None

        if is_win:
            message = f"Уровень {level_number} пройден!"
        else:
            message = f"Уровень {level_number} провален"

        font = pygame.font.Font(font_name, 40)
        text = font.render(message, True, font_color)
        x = (self.size[0] - text.get_width()) // 2
        y = 90
        self.image.blit(text, (x, y))

        if added_coins:
            font = pygame.font.Font(font_name, 20)
            x += text.get_width()
            y += text.get_height() + 10
            text = font.render(f"+{self.added_coins}", True, font_color)
            x -= text.get_width() + 30
            self.image.blit(text, (x, y))
            self.image.blit(pygame.transform.scale(load_image('coins.png'),
                                                   (20, 20)), (x + text.get_width() + 5, y))

        self.coins.render(self.image)

    def render(self, screen):
        screen.blit(self.image, self.pos)

        for btn in self.buttons:
            if self.buttons[btn]:
                self.buttons[btn].render(screen)

        all_sprites.draw(screen)

    def get_click(self, pos):
        if self.buttons['menu'].get_click(pos):
            return LEVEL_COUNT + 1
        elif self.buttons['again'].get_click(pos):
            return LEVEL_COUNT + 2
        elif self.buttons['next'] and self.buttons['next'].get_click(pos):
            return LEVEL_COUNT + 3
        elif self.buttons['sound'].get_click(pos):
            return LEVEL_COUNT + 4

    def update(self):
        all_sprites.update()


# конец уровня
def level_over(level_number, is_win, added_coins=None):
    global quiet, back_image

    all_sprites.empty()

    window = LevelOver(level_number, is_win, added_coins)
    i = 0

    if is_win:
        play_sound('win.mp3')
    else:
        play_sound('lose.mp3')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(level_menu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = window.get_click(event.pos)
                if res == LEVEL_COUNT + 1:
                    play_music('menu.mp3')
                    return level_menu()
                    # переход в меню с уровнями
                elif res == LEVEL_COUNT + 2:
                    return in_level(level_number)
                    # перезапуск уровня
                elif res == LEVEL_COUNT + 3:
                    return in_level(level_number + 1)
                    # следующий уровень
                elif res == LEVEL_COUNT + 4:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины

        screen.blit(back_image, (0, 0))

        window.update()
        if i % 50 == 0 and is_win:
            create_particles((random.randrange(0, WIDTH - 50), random.randrange(0, HEIGHT - 50)))
        i += 1

        window.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


# Строка ввода
class InputBox:
    def __init__(self, pos, hide, limiter):
        self.text = ''
        self.size = 200, 30
        self.pos = pos
        self.rect = pygame.Rect(*self.pos, *self.size)
        self.image = pygame.transform.scale(load_image('line.png'), self.size)
        self.can_input = False
        self.hide = hide
        self.limiter = limiter
        self.i = 0

    def get_click(self, pos):
        self.can_input = False
        if self.rect.collidepoint(pos):
            self.can_input = True

    def input(self, event):
        if self.can_input:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.limiter[1]:
                self.text += event.unicode

    def render(self, screen):
        # pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        screen.blit(self.image, self.pos)
        font = pygame.font.Font(None, 27)
        if self.hide:
            text = font.render(len(self.text) * '*', True, (0, 0, 0))
        else:
            text = font.render(self.text, True, (0, 0, 0))
        screen.blit(text, (self.pos[0] + 8, self.pos[1] + 3))

        if self.i % 70 in range(0, 20) and self.can_input:
            x = self.pos[0] + text.get_width() + 9
            pygame.draw.line(screen, (0, 0, 0), (x, self.pos[1] + 5), (x, self.pos[1] + 5 + text.get_height() - 4), 1)
        self.i += 1


# выдает подсказу про логин или пароль
class HelpEnter:
    def __init__(self, pos, size, image, up):
        self.up = up
        self.pos = pos
        self.size = size
        self.image = pygame.transform.scale(load_image('help_btn.png'), self.size)
        self.image2 = pygame.transform.scale(load_image(image), (190, 140))
        self.rect = pygame.Rect(pos[0] - 5, pos[1] - 5, size[0] + 10, size[1] + 10)

        self.work = False

    def get_move(self, pos):
        self.work = False
        if self.rect.collidepoint(pos):
            self.work = True

    def render(self, screen):
        screen.blit(self.image, self.pos)

        if self.work:
            x = self.pos[0] + 2
            y = self.pos[1] + 10
            if self.up:
                y -= self.image2.get_height()
            screen.blit(self.image2, (x, y))


# Функция, реализующая регистрацию и вход в аккаунт
def entertogame(newbie):
    global quiet, back_image

    enter = EnterToGame(newbie)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(choose_menu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = enter.get_click(event.pos)
                if res == 1:
                    return choose_menu()
                    # Возврат к выбору действия
                if res == 2:
                    res = enter.check()
                    if res and newbie:
                        cur.execute(
                            "INSERT INTO players_info(nickname, password, money, skins, levels) VALUES(?, ?, ?, ?, ?)",
                            (enter.input_boxes['nickname'].text,
                             enter.input_boxes['password'].text, 0, 'hero1', ''))
                        con.commit()
                        player_info(enter.input_boxes['nickname'].text)
                        return mainmenu()
                        # переход в главное меню
                    elif res and not newbie:
                        player_info(enter.input_boxes['nickname'].text)
                        return mainmenu()
                        # переход в главное меню
                if res == 3:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины
            if event.type == pygame.KEYDOWN:
                enter.input(event)
            if event.type == pygame.MOUSEMOTION:
                enter.get_move(event.pos)
        screen.blit(back_image, (0, 0))
        enter.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


# Класс, реализующий регистрацию и вход в аккаунт
class EnterToGame:
    def __init__(self, newbie):
        self.input_boxes = {'nickname': InputBox(pos=((WIDTH - 200) // 2, 130), hide=False, limiter=(8, 16)),
                            'password': InputBox(pos=((WIDTH - 200) // 2, 180), hide=True, limiter=(4, 8))}
        self.buttons = {'back': Button(pos=(10, 300), size=(45, 45), image_names=['previous_btn.png']),
                        'sound': SoundButton(pos=(540, 300), size=(45, 45)),
                        'help_pass': HelpEnter(pos=(403, 182), size=(20, 20), image='cloud2.png', up=False),
                        'help_nick': HelpEnter(pos=(403, 133), size=(20, 20), image='cloud1.png', up=True)}
        self.errormessage = None
        if newbie:
            self.buttons['action'] = Button(pos=((WIDTH - 200) // 2, 230), size=(200, 45),
                                            image_names=['signup_btn.png'])
        else:
            self.buttons['action'] = Button(pos=((WIDTH - 200) // 2, 230), size=(200, 45),
                                            image_names=['signin_btn.png'])
        self.newbie = newbie

    def get_click(self, pos):
        for input_box in self.input_boxes:
            self.input_boxes[input_box].get_click(pos)
        if self.buttons['back'].get_click(pos):
            return 1
        if self.buttons['action'].get_click(pos):
            return 2
        if self.buttons['sound'].get_click(pos):
            return 3

    def clear(self):
        self.input_boxes = {'nickname': InputBox(pos=((WIDTH - 200) // 2, 130), hide=False, limiter=(8, 16)),
                            'password': InputBox(pos=((WIDTH - 200) // 2, 180), hide=True, limiter=(4, 8))}

    def input(self, event):
        for input_box in self.input_boxes:
            self.input_boxes[input_box].input(event)

    def render(self, screen):
        for input_box in self.input_boxes:
            self.input_boxes[input_box].render(screen)
        font = pygame.font.Font(font_name, 25)
        text = font.render('Введите логин и пароль', True, font_color)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, 65))
        font = pygame.font.Font(font_name, 20)
        text = font.render('Логин:', True, font_color)
        screen.blit(text, (110, 135))
        text = font.render('Пароль:', True, font_color)
        screen.blit(text, (110, 185))
        for button in self.buttons:
            self.buttons[button].render(screen)
        if self.errormessage:
            text = font.render(self.errormessage, True, (255, 0, 0))
            screen.blit(text, ((WIDTH - text.get_width()) // 2, 280))

    def check(self):
        if self.newbie:
            for input_box in self.input_boxes:
                if not self.input_boxes[input_box].limiter[0] <= len(self.input_boxes[input_box].text) <= \
                       self.input_boxes[input_box].limiter[1]:
                    self.errormessage = 'Ошибка в длине ввода'
                    self.clear()
                    return False
            for i in self.input_boxes['nickname'].text:
                if i not in 'qwertyuiopasdfghjklzxcvbnm0123456789_':
                    self.errormessage = 'В логине имеются символы, отличные от указанных'
                    self.clear()
                    return False
            for i in self.input_boxes['password'].text:
                if i not in 'qwertyuiopasdfghjklzxcvbnm0123456789':
                    self.errormessage = 'В пароле имеются символы, отличные от указанных'
                    self.clear()
                    return False
            nicknames = cur.execute("SELECT nickname FROM players_info").fetchall()
            for i in nicknames:
                if self.input_boxes['nickname'].text == i[0]:
                    self.errormessage = 'Логин занят'
                    self.clear()
                    return False
            return True
        else:
            try:
                password = cur.execute("SELECT password FROM players_info WHERE nickname=?",
                                       (self.input_boxes['nickname'].text,)).fetchone()[0]
                if password == self.input_boxes['password'].text:
                    return True
                self.errormessage = 'Введен неверный пароль'
                self.clear()
            except TypeError:
                self.errormessage = 'Введен неверный логин'
                self.clear()
            return False

    def get_move(self, pos):
        self.buttons['help_nick'].get_move(pos)
        self.buttons['help_pass'].get_move(pos)


# Класс, реализуюший выбор регистрации или входа в аккаунт
class Choose:
    def __init__(self):
        self.buttons = {
            'sign_up': Button(pos=((WIDTH - 200) // 2, 135), size=(200, 45), image_names=['signup_btn.png']),
            'sign_in': Button(pos=((WIDTH - 200) // 2, 230), size=(200, 45), image_names=['signin_btn.png']),
            'sound': SoundButton(pos=(540, 300), size=(45, 45))}

    def get_click(self, pos):
        if self.buttons['sign_up'].get_click(pos):
            return 1
        if self.buttons['sign_in'].get_click(pos):
            return 2
        if self.buttons['sound'].get_click(pos):
            return 3

    def render(self, screen):
        font = pygame.font.Font(font_name, 40)
        text = font.render('Добро пожаловать!', True, font_color)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, 20))
        font = pygame.font.Font(font_name, 20)
        text = font.render('Если вы здесь впервые, то можете', True, font_color)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, 105))
        text = font.render('Иначе можете', True, font_color)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, 205))
        for btn in self.buttons:
            self.buttons[btn].render(screen)

        # Выбор регистрации или входа в аккаунт


def choose_menu():
    global quiet, back_image

    choose = Choose()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(choose_menu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = choose.get_click(event.pos)
                if res == 1:
                    return entertogame(True)
                    # Регистрация
                if res == 2:
                    return entertogame(False)
                    # Вход в аккаунт
                if res == 3:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины
        screen.blit(back_image, (0, 0))
        choose.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


# Класс главного меню
class MainMenu:
    def __init__(self):
        self.buttons = {'levels': TextButton(pos=(150, 85), image='menu_btn.png', text=' Выбор уровня'),
                        'shop': TextButton(pos=(150, 135), image='shop_btn.png', text=' Магазин'),
                        'rating': TextButton(pos=(150, 185), image='rating_btn.png', text=' Рейтинг'),
                        'change': TextButton(pos=(150, 235), image='restart_btn.png', text=' Сменить пользователя'),
                        'exit': TextButton(pos=(150, 285), image='close_btn.png', text=' Выйти'),
                        'sound': SoundButton(pos=(550, 300), size=(45, 45))}

    def render(self, screen):
        for btn in self.buttons:
            self.buttons[btn].render(screen)

        font = pygame.font.Font(font_name, 60)
        text = font.render('MAIN MENU', True, (200, 200, 200))
        screen.blit(text, ((WIDTH - text.get_width()) // 2, 20))
        font = pygame.font.Font(font_name, 20)
        text = font.render(nickname, True, font_color)
        screen.blit(text, (5, 5))

    def get_click(self, pos):
        if self.buttons['rating'].get_click(pos):
            return 1
        if self.buttons['shop'].get_click(pos):
            return 2
        if self.buttons['levels'].get_click(pos):
            return 3
        if self.buttons['change'].get_click(pos):
            return 4
        if self.buttons['exit'].get_click(pos):
            return 5
        if self.buttons['sound'].get_click(pos):
            return 6


# Кнопка с текстом
class TextButton:
    def __init__(self, pos, image, text):
        self.text = text
        self.pos = pos
        font = pygame.font.Font(font_name, 30)
        text = font.render(self.text, True, font_color)
        self.width = text.get_width()
        self.height = text.get_height()
        self.image = pygame.Surface((self.height + self.width + 2, self.height),
                                    pygame.SRCALPHA, 32)
        self.image.blit(pygame.transform.scale(load_image(image), (self.height, self.height)), (0, 0))
        self.image.blit(text, (self.height + 2, 0))
        self.rect = pygame.Rect(pos[0], pos[1], self.width + self.height, self.height)

    def render(self, screen):
        screen.blit(self.image, self.pos)

    def get_click(self, pos):
        if self.rect.collidepoint(pos):
            play_sound('press_btn.mp3')
            return True
        return False


# Главное меню
def mainmenu():
    global quiet, back_image

    menu = MainMenu()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(mainmenu, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = menu.get_click(event.pos)
                if res == 1:
                    return score_table()
                    # Рейтинг
                if res == 2:
                    return shop_menu()
                    # Магазин
                if res == 3:
                    return level_menu()
                    # Выбор уровня
                if res == 4:
                    return areyousure(mainmenu, choose_menu)
                    # Смена пользователя
                if res == 5:
                    areyousure(mainmenu, terminate)
                    # Выйти из игры
                if res == 6:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины
        screen.blit(back_image, (0, 0))
        menu.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


# таблица рекордов
class ScoreTable:
    def __init__(self):
        self.buttons = {'mainmenu': Button(pos=(10, 300), size=(45, 45), image_names=['previous_btn.png']),
                        'sound': SoundButton(pos=(540, 300), size=(45, 45))}

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
        font = pygame.font.Font(font_name, 40)
        text = font.render('Таблица рекордов', True, (255, 255, 255))
        x = (WIDTH - text.get_width()) // 2
        screen.blit(text, (x, 10))

        if not self.best:
            font = pygame.font.Font(font_name, 25)
            text = font.render('Здесь пока нет рекордов', True, font_color)
            x = (WIDTH - text.get_width()) // 2
            screen.blit(text, (x, 100))
            return

        width_col0, width_col1, width_col2 = 100, 150, None
        left, top = 60, 70
        delta_y = 20
        y = top

        font = pygame.font.Font(font_name, 25)
        text = font.render('Номер', True, font_color)
        x = (width_col0 - text.get_width()) // 2
        screen.blit(text, (x + left, y))
        text = font.render('Ник', True, font_color)
        x = (width_col1 - text.get_width()) // 2
        screen.blit(text, (x + left + width_col0, y))
        font = pygame.font.Font(None, 20)
        text = font.render('Количество пройденных уровней', True, font_color)
        screen.blit(text, (left + width_col0 + width_col1, y))
        width_col2 = text.get_width()
        y += text.get_height() + delta_y

        len_line_x = width_col0 + width_col1 + width_col2 + 5
        pygame.draw.line(screen, font_color, (left, top - 5), (left + len_line_x, top - 5))
        pygame.draw.line(screen, font_color, (left, y - delta_y // 2), (left + len_line_x, y - delta_y // 2))

        font = pygame.font.Font(font_name, 25)
        i = 1
        for nick, count in self.best:
            text = font.render(str(i), True, (200, 200, 200))
            screen.blit(text, (left + 30, y))
            text = font.render(nick, True, (200, 200, 200))
            screen.blit(text, (left + width_col0 + 10, y))
            text = font.render(str(count), True, (200, 200, 200))
            screen.blit(text, (left + width_col0 + width_col1 + 10, y))
            y += text.get_height() + delta_y
            pygame.draw.line(screen, (220, 220, 220), (left, y - delta_y // 2), (left + len_line_x, y - delta_y // 2))
            if y + text.get_height() > HEIGHT:
                break
            i += 1

        for btn in self.buttons:
            self.buttons[btn].render(screen)

    def get_click(self, pos):
        if self.buttons['mainmenu'].get_click(pos):
            return 1
        if self.buttons['sound'].get_click(pos):
            return 2


# таблица рекордов
def score_table():
    global quiet, back_image

    table = ScoreTable()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(score_table, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = table.get_click(event.pos)
                if res == 1:
                    return mainmenu()
                    # переход в главное меню
                if res == 2:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины

        screen.blit(back_image, (0, 0))
        table.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


# начальный экран
class StartWindow:
    def __init__(self):
        self.buttons = {
            'play': Button(pos=((WIDTH - 200) // 2, 200), size=(200, 45), image_names=['play_game_btn.png']),
            'sound': SoundButton(pos=(540, 300), size=(45, 45))}

        self.name_image = load_image('game_name2.png')

    def render(self, screen):
        screen.blit(self.name_image, ((WIDTH - self.name_image.get_width()) // 2, 100))
        for btn in self.buttons:
            self.buttons[btn].render(screen)

    def get_click(self, pos):
        if self.buttons['play'].get_click(pos):
            return 1
        if self.buttons['sound'].get_click(pos):
            return 2


# начальный экран
def start_window():
    global quiet, back_image

    window = StartWindow()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                areyousure(start_window, terminate)
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = window.get_click(event.pos)
                if res == 1:
                    return choose_menu()
                    # переход в меню входа в игру
                if res == 2:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины

        screen.blit(back_image, (0, 0))
        window.render(screen)

        pygame.display.flip()
        clock.tick(FPS)


# Класс подтверждения действия
class AreYouSure:
    def __init__(self):
        self.buttons = {
            'ok': Button(pos=((WIDTH - 100) // 2 - 25, 155), size=(45, 45), image_names=['ok_btn.png']),
            'no': Button(pos=((WIDTH - 100) // 2 + 70, 155), size=(45, 45), image_names=['close_btn.png']),
            'sound': SoundButton(pos=(540, 300), size=(45, 45))}

    def get_click(self, pos):
        if self.buttons['ok'].get_click(pos):
            return 1
        if self.buttons['no'].get_click(pos):
            return 2
        if self.buttons['sound'].get_click(pos):
            return 3

    def render(self, screen):
        for btn in self.buttons:
            self.buttons[btn].render(screen)
        font = pygame.font.Font(font_name, 30)
        text = font.render('Вы уверены?', True, font_color)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, 85))


# Подтвердить действие
def areyousure(previous, confirm):
    global quiet

    sure = AreYouSure()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                res = sure.get_click(event.pos)
                if res == 1:
                    return confirm()
                    # Подтверждение действия
                if res == 2:
                    return previous()
                    # Отмена действия
                if res == 3:
                    quiet = not quiet
                    play_music()
                    # изменить статус тишины
        screen.blit(back_image, (0, 0))

        sure.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


def main():
    play_music('menu.mp3')
    start_window()


if __name__ == '__main__':
    main()