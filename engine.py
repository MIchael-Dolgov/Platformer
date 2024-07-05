from os.path import isfile
from os import listdir
from entities import *
def flip(sprites):
    return [pg.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(entity, width, height, direction=False):
    path = join("resources", "entities", entity)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pg.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pg.Surface((width, height), pg.SRCALPHA, 32)
            rect = pg.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pg.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def handle_vertical_collision(entity, objects, dy):
    collided_objects = []
    for obj in objects:
        if pg.sprite.collide_mask(entity, obj):
            if dy >= 0:
                entity.rect.bottom = obj.rect.top
                entity.landed()
            elif dy < 0:
                entity.rect.top = obj.rect.bottom
                entity.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(entity, objects, dx):
    entity.move(dx, 0)
    entity.update()
    collided_object = None
    for obj in objects:
        if pg.sprite.collide_mask(entity, obj):
            collided_object = obj
            break

    entity.move(-dx, 0)
    entity.update()
    return collided_object

def handle_player_move(player, objects):
    keys = pg.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, player.VEL * -2)
    collide_right = collide(player, objects, player.VEL * 2)

    if keys[pg.K_a] and not collide_left:
        player.move_left(player.VEL)
    if keys[pg.K_d] and not collide_right:
        player.move_right(player.VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)

    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and ((obj.name == "fire" and obj.condition == "on") or obj.name == "RockHead"):
            player.make_hit()

def handle_entities(entities: list, objects: list):
    for entity in entities:
        collide_left = collide(entity, objects, entity.VEL * -2)
        collide_right = collide(entity, objects, entity.VEL * 2)
        vertical_collide = handle_vertical_collision(entity, objects, entity.y_vel)
        if (collide_right or collide_left):
            entity.move_right(0)
            entity.move_left(0)


def load_music(path):
    songs = []
    for filename in listdir(path):
        if filename.endswith('.wav'):
            songs.append(join(path, filename))
    return songs



def draw(scrn, background: Background, map: list, entities: list, widgets: list, player: Player, offset_x):
    coords, img = background.prepare_for_draw()
    for coord in coords:
        scrn.blit(img, coord)

    coords, img = background.prepare_for_draw()
    for coord in coords:
        scrn.blit(img, coord)

    player.draw(scrn, offset_x)

    for entity in entities:
        entity.draw(scrn, offset_x)

    for block in map:
        scrn.blit(block.image, (block.x - offset_x, block.y))

    # Widgets processing
    for widget in widgets:
        scrn.blit(widget.image, (widget.x, widget.y))


    pg.display.update()

def draw_screen(scrn, background: Background):
    coords, img = background.prepare_for_draw()
    for coord in coords:
        scrn.blit(img, coord)
    pg.display.update()

def draw_game_over_screen(scrn, background: Background):
    coords, img = background.prepare_for_draw()
    for coord in coords:
        scrn.blit(img, coord)
    over_font = pg.font.Font(None, 100)
    over_text = over_font.render("Game Over", True, (255, 100, 100))
    over_text_rec = over_text.get_rect(center = (480, 240))
    over_font_small = pg.font.Font(None, 40)
    text1 = over_font_small.render("Press space to play again", True, (121, 122, 120))
    text2 = over_font_small.render("Press escape to exit", True, (121, 122, 120))
    text1_rect = text1.get_rect(center = (480, 340))
    text2_rect = text2.get_rect(center = (480, 390))
    scrn.blit(over_text, over_text_rec)
    scrn.blit(text1, text1_rect)
    scrn.blit(text2, text2_rect)
    pg.display.update()
