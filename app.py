import pygame as pg
from os.path import join
import pygame.display
from time import sleep

from entities import Player, Block, Background, Fire, HeartWidget, RockHead

from engine import load_music, load_sprite_sheets, handle_player_move, draw, draw_game_over_screen, handle_entities

# programm constants
SIZE_X, SIZE_Y = 960, 680
FPS = 60
LARGE_TILE_SIZE = 48
MEDIUM_TILE_SIZE = 32
MUSIC_ENDED = pygame.USEREVENT

screen = pg.display.set_mode((SIZE_X, SIZE_Y))

# Application
def app(isover):
    # initialization
    clock = pg.time.Clock()
    pygame.display.set_caption("Platformer")
    app_is_running = True
    is_over = isover

    offset_x = 0
    scroll_area_width = 200

    # Music initialization
    pygame.mixer.music.set_endevent(MUSIC_ENDED)

    song_index = 0
    songs = load_music(join("resources", "tracks"))
    pygame.mixer.music.load(songs[song_index])
    pygame.mixer.music.play()
    song_index += 1

    # Textures
    background = Background(16, 16, SIZE_X, SIZE_Y, "Brown.png")

    # Map
    # Various constants defines textures which will be displayed from resourcepack
    floor = [Block(i * LARGE_TILE_SIZE, SIZE_Y - LARGE_TILE_SIZE, LARGE_TILE_SIZE, LARGE_TILE_SIZE*2, 0)
             for i in range(-SIZE_X // LARGE_TILE_SIZE, (SIZE_X * 2) // LARGE_TILE_SIZE)]
    terrain = [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160, MEDIUM_TILE_SIZE,
        LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE+32) for i in range(15, 31)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160-32, MEDIUM_TILE_SIZE,
        LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE+32) for i in range(20, 29)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160-64, MEDIUM_TILE_SIZE,
        LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE + 32) for i in range(25, 28)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160-64, MEDIUM_TILE_SIZE,
        LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE + 32) for i in range(-8, 2)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160-216, MEDIUM_TILE_SIZE,
        LARGE_TILE_SIZE * 4 + 96, LARGE_TILE_SIZE + 32) for i in range(5, 14)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160 - 16, MEDIUM_TILE_SIZE,
                      LARGE_TILE_SIZE * 4 + 96, LARGE_TILE_SIZE + 96) for i in range(-50, -32)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160 + 16, MEDIUM_TILE_SIZE,
                      LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE + 32) for i in range(-33, -31)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160 + 48, MEDIUM_TILE_SIZE,
                      LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE + 32) for i in range(-32, -30)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160 + 80, MEDIUM_TILE_SIZE,
                      LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE + 32) for i in range(-31, -29)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 160 + 112, MEDIUM_TILE_SIZE,
                      LARGE_TILE_SIZE * 3 + 64, LARGE_TILE_SIZE + 32) for i in range(-30, -28)]
    terrain += [Block(i * MEDIUM_TILE_SIZE, SIZE_Y - MEDIUM_TILE_SIZE - 16 - (32 * j), MEDIUM_TILE_SIZE,
                      LARGE_TILE_SIZE * 4 + 96, LARGE_TILE_SIZE + 32) for i in range(50, 55)
                      for j in range(1, 18)]

    fire1 = Fire(100, SIZE_Y-110, 16, 32,
        load_sprite_sheets("traps/Fire", 16, 32), "on")

    fire2 = Fire(320, SIZE_Y - 110, 16, 32,
                 load_sprite_sheets("traps/Fire", 16, 32), "on")

    fire3 = Fire(-40, SIZE_Y - 160-160, 16, 32,
                 load_sprite_sheets("traps/Fire", 16, 32), "on")

    fire4 = Fire(-240, SIZE_Y - 160 - 160, 16, 32,
                 load_sprite_sheets("traps/Fire", 16, 32), "off")

    map_of_objects = [*floor, *terrain, fire1, fire2, fire3, fire4]

    # Entities
    player = Player(180, SIZE_Y-32-1, 32, 32,
        load_sprite_sheets("NinjaFrog", 32, 32, True))

    # player1 = Player(340, SIZE_Y-32-200, 32, 32,
    #     load_sprite_sheets("NinjaFrog", 32, 32, True))

    rockhead1 = RockHead(280, SIZE_Y-32-500, 32, 32,
                        load_sprite_sheets("RockHead", 38, 38, False))

    rockhead2 = RockHead(1100, SIZE_Y - 32 - 10, 32, 32,
                         load_sprite_sheets("RockHead", 38, 38, False))

    rockhead3 = RockHead(0, SIZE_Y - 32 - 10, 32, 32,
                         load_sprite_sheets("RockHead", 38, 38, False))

    entities = [rockhead1, rockhead2, rockhead3]


    # Gameplay
    while app_is_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            if event.type == pg.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
            if event.type == MUSIC_ENDED:
                song_index = (song_index + 1) % len(songs)  # Go to the next song (or first if at last).
                pg.mixer.music.load(songs[song_index])
                pg.mixer.music.play()

        # Animate Objects
        player.loop(FPS)
        if player.lifes <= 0:
            app_is_running = False

        rockhead1.loop(FPS)
        rockhead1.patrol(150, 380)
        rockhead2.loop(FPS)
        rockhead2.patrol(400, 1500)
        rockhead3.loop(FPS)
        rockhead3.patrol(-400, 10)

        fire1.loop()
        fire2.loop()
        fire3.loop()
        fire4.loop()

        # Widgets update
        widgets = [HeartWidget(64 * i, 15, 64, 64, i, name="Heart") if player.lifes > i
        else HeartWidget(64 * i, 15, 64, 64, i, 128) for i in range(0, player.LIFES)]

        handle_player_move(player, map_of_objects + [*entities])
        handle_entities(entities, map_of_objects)

        # BottomEdge
        if player.pos()[1] > 2000:
            player.lifes = 0

        draw(screen, background, map_of_objects, entities, widgets, player, offset_x)
        if not(app_is_running):
            sleep(1.5)
            pg.display.set_caption("Game Over")
            background = Background(16, 16, SIZE_X, SIZE_Y, "Gray.png")
            draw_game_over_screen(screen, background)
            choosen = False
            while not(choosen):
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        is_over = True
                        choosen = True
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            is_over = False
                            choosen = True
                        if event.key == pg.K_ESCAPE:
                            is_over = True
                            choosen = True

        if ((player.rect.right - offset_x >= SIZE_X - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        pg.draw.rect(screen, (255, 255, 0), terrain[0].rect)
        clock.tick(60)
    return is_over


if __name__ == "__main__":
    pg.init()
    is_game_over = False
    while not(is_game_over):
        is_game_over = app(is_game_over)
    pg.quit()
    exit(0)
else:
    raise "NotAModuleError"
