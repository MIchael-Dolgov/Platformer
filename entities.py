import pygame as pg
from os.path import join

import pygame.mask


class Object(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pg.Rect(x, y, width, height)


class Entity(Object):
    GRAVITY = 1
    VEL = 5
    ANIMATION_DELAY = 3
    SPRITES = None
    def __init__(self, x, y, width, height, sprites):
        super().__init__(x, y, width, height)
        self.rect = pg.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.animation_count = 0
        self.direction = "left"
        self.fall_count = 0
        self.SPRITES = sprites

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprite_sheet = "idle"
        sprite_sheet_name = sprite_sheet
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = ((self.animation_count //
                        self.ANIMATION_DELAY)) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class RockHead(Entity):
    LIFES = 1
    VEL = 1
    def __init__(self, x, y, width, height, sprites, name="RockHead"):
        super().__init__(x, y, width, height, sprites)
        self.jump_count = 0
        self.fall_count = 0
        self.hit = 0
        self.hit_count = 0
        self.SPRITES = sprites
        self.lifes = self.LIFES
        self.name = name
        self.go_left = True

    def patrol(self, x_start, x_end):
        if(self.rect.x < x_start or self.rect.x > x_end):
            self.go_left = not(self.go_left)
        if(self.go_left):
            self.move_left(self.VEL)
        else:
            self.move_right(self.VEL)

class Player(Entity):
    LIFES = 3
    def __init__(self, x, y, width, height, sprites):
        super().__init__(x, y, width, height, sprites)
        self.jump_count = 0
        self.fall_count = 0
        self.hit = 0
        self.hit_count = 0
        self.SPRITES = sprites
        self.lifes = self.LIFES
        self.sprite = None
        self.update_sprite()

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
            if self.hit_count== 1:
                self.lifes -= 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def pos(self):
        return (self.rect.x, self.rect.y)

    def update_lifes(self):
        self.lifes = self.LIFES

    def make_hit(self):
        self.hit = True

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

class Object(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Fire(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height, sprites, condition: str):
        super().__init__(x, y, width, height, "fire")
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.condition = condition
        self.sprites = sprites

    def on(self):
        self.condition = "on"

    def off(self):
        self.condition = "off"

    def switch(self):
        if(self.condition == "off"):
            self.condition = "on"
        else:
            self.condition = "off"

    def loop(self):
        sprites = self.sprites[self.condition]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Block(Object):
    def __init__(self, x, y, size, terrain_x=0, terrain_y=0):
        super().__init__(x, y, size, size)
        self.texture_map = (terrain_x, terrain_y)
        self.full_image = pg.image.load(join("resources", "textures", "Terrain.png")).convert_alpha()
        self.masc_rect = pg.Rect(terrain_x, terrain_y, size, size)
        self.size = size

        self.image = self.full_image.subsurface(self.masc_rect)
        del self.full_image, self.masc_rect, self.texture_map
        self.mask = pg.mask.from_surface(self.image)

    def update_coords(self, x, y):
        self.x = x
        self.y = y

    def fill_ground(self, width_screen, height_screen):
        coords = []
        for i in range(width_screen // self.width + 1):
            pos = (i * self.width, height_screen-self.height)
            coords.append(pos)
        return coords

class Background():

    def __init__(self, asset_wid, asset_hegt, window_widt, window_hegt, texture_name: str):
        self.asset_width = asset_wid
        self.asset_height = asset_hegt
        self.back_width = window_widt
        self.back_height = window_hegt
        self.asset_color_name = str(texture_name)

    def prepare_for_draw(self):
        image = pg.image.load(join("resources", "backgrounds", self.asset_color_name)).convert()
        _, _, width, height = image.get_rect()
        tiles = []

        for i in range(self.back_width // width + 1):
            for j in range(self.back_height // height + 1):
                pos = (i * width, j * height)
                tiles.append(pos)

        return tiles, image


class HeartWidget(Object):
    def __init__(self, x, y, width, height, number: int, terrain_x=0, terrain_y=0, name=None):
        super().__init__(x, y, width, height)
        self.texture_map = (terrain_x, terrain_y)
        self.full_image = pg.image.load(join("resources", "widgets", "hearts64x64.png")).convert_alpha()
        self.masc_rect = pg.Rect(terrain_x, terrain_y, width, height)
        self.width = width
        self.height = height

        self.image = self.full_image.subsurface(self.masc_rect)
        del self.full_image, self.masc_rect, self.texture_map
        self.mask = pg.mask.from_surface(self.image)
        self.name = name
        self.number = number


