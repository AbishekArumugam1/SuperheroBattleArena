import asyncio
import json
import pygame
import random
import math

pygame.init()

MUSIC_FILE = "brainrot_music.ogg"
MUSIC_ENABLED = False
try:
    pygame.mixer.init()
    MUSIC_ENABLED = False
except pygame.error:
    pass

music_playing = False

def start_battle_music():
    global music_playing
    if not MUSIC_ENABLED or music_playing:
        return
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
        music_playing = True
    except (pygame.error, FileNotFoundError, OSError):
        music_playing = False

def stop_battle_music():
    global music_playing
    if MUSIC_ENABLED:
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
    music_playing = False


WIDTH = 1100
HEIGHT = 650
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUPERHERO BATTLE ARENA - CAMPAIGN")
clock = pygame.time.Clock()


FONT = pygame.font.SysFont('arial', 32)
MED = pygame.font.SysFont("arial", 22, bold=True)
SMALL = pygame.font.SysFont("arial", 17)
BIG = pygame.font.SysFont("arial", 45, bold=True)
HUGE = pygame.font.SysFont("arial", 65, bold=True)

WHITE = (245, 245, 245)
BLACK = (12, 14, 24)
RED = (230, 55, 55)
GREEN = (60, 220, 100)
BLUE = (50, 160, 255)
GOLD = (255, 210, 50)
CYAN = (60, 230, 255)
PURPLE = (175, 75, 255)
PINK = (255, 90, 180)
ORANGE = (255, 120, 35)
DARK = (25, 30, 48)
GREY = (105, 115, 130)


ARENAS = [
    ("TRAINING", (18, 25, 55), (10, 70, 85)),
    ("CITY", (20, 35, 75), (35, 25, 55)),
    ("VOLCANO", (70, 30, 20), (35, 12, 12)),
    ("SHADOW", (35, 20, 65), (12, 8, 30)),
    ("WARZONE", (55, 55, 60), (20, 25, 30)),
    ("FINAL BATTLE", (80, 25, 35), (25, 8, 15)),
]


HEROES = {

    "THUNDER": {
        "color": BLUE,
        "hp": 130,
        "attack": 25,
        "special": 55,
        "speed": 3.0,
        "power": "LIGHTNING"
    },

    "FLAME": {
        "color": ORANGE,
        "hp": 110,
        "attack": 30,
        "special": 70,
        "speed": 3.2,
        "power": "FIRE"
    },

    "SHADOW": {
        "color": PURPLE,
        "hp": 95,
        "attack": 38,
        "special": 80,
        "speed": 3.8,
        "power": "SHADOW"
    },

    "GUARDIAN": {
        "color": GREEN,
        "hp": 180,
        "attack": 20,
        "special": 50,
        "speed": 2.6,
        "power": "SHIELD"
    }
}

HERO_NAMES = list(HEROES.keys())



LEVELS = [

    {
        "name": "TRAINING GROUND",
        "enemy": "TRAINING BOT",
        "hp": 70,
        "atk": 7,
        "speed": 1.2,
        "unlock": "ATTACK",
        "tip": "Learn movement and basic attacks."
    },

    {
        "name": "ROOKIE BATTLE",
        "enemy": "ROOKIE",
        "hp": 90,
        "atk": 10,
        "speed": 1.5,
        "unlock": "JUMP",
        "tip": "Use UP to jump."
    },

    {
        "name": "POWER AWAKENING",
        "enemy": "POWER BOT",
        "hp": 115,
        "atk": 12,
        "speed": 1.8,
        "unlock": "SPECIAL",
        "tip": "Use E for your unique special power."
    },

    {
        "name": "DEFENDER TRIAL",
        "enemy": "BRUISER",
        "hp": 140,
        "atk": 16,
        "speed": 2.0,
        "unlock": "BLOCK",
        "tip": "Hold SHIFT to block attacks."
    },

    {
        "name": "SPEED TRIAL",
        "enemy": "SPEED DEMON",
        "hp": 155,
        "atk": 18,
        "speed": 2.5,
        "unlock": "DASH",
        "tip": "Press F to dash."
    },

    {
        "name": "VILLAIN ARMY",
        "enemy": "ELITE",
        "hp": 195,
        "atk": 20,
        "speed": 2.7,
        "unlock": "COMBO",
        "tip": "Attack continuously to build combos."
    },

    {
        "name": "ELITE VILLAIN",
        "enemy": "RAGE LORD",
        "hp": 270,
        "atk": 25,
        "speed": 3.0,
        "unlock": "ULTIMATE",
        "tip": "The enemy becomes stronger when its HP is low."
    },

    {
        "name": "FINAL BOSS",
        "enemy": "DARK OVERLORD",
        "hp": 390,
        "atk": 30,
        "speed": 3.3,
        "unlock": "ALL",
        "tip": "Everything is unlocked. Defeat the Final Boss!"
    }
]



MENU = "MENU"
LEVEL_INTRO = "LEVEL_INTRO"
BATTLE = "BATTLE"
LEVEL_CLEAR = "LEVEL_CLEAR"
GAME_OVER = "GAME_OVER"

state = MENU

selected = 0
level = 1
hero_name = "THUNDER"

unlocked = set()


hero = pygame.Rect(130, 430, 60, 95)
enemy = pygame.Rect(880, 430, 65, 95)

hero_hp = 0
hero_max = 0
hero_energy = 100

enemy_hp = 0
enemy_max = 0

vx = 0
vy = 0

on_ground = True
blocking = False

facing = 1

attack_cd = 0
special_cd = 0
dash_cd = 0

enemy_cd = 0
enemy_special_cd = 0

combo = 0
combo_timer = 0

rage = False

winner = ""

particles = []
damage_numbers = []


projectiles = []
pickups = []
enemy_projectiles = []
attack_anim_timer = 0

special_effect_timer = 0
special_effect_type = ""

burn_timer = 0

enemy_knockback = 0


def draw_text(text, font, position, color=WHITE, center=False):

    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=position)
    else:
        rect = surface.get_rect(topleft=position)

    screen.blit(surface, rect)


def reset_level():

    global hero
    global enemy
    global hero_hp
    global hero_max
    global hero_energy
    global enemy_hp
    global enemy_max

    global vx
    global vy
    global on_ground
    global blocking
    global facing

    global attack_cd
    global special_cd
    global dash_cd
    global enemy_cd
    global enemy_special_cd

    global combo
    global combo_timer
    global rage
    global winner

    global special_effect_timer
    global special_effect_type

    global burn_timer
    global enemy_knockback
    global attack_anim_timer

    enemy_projectiles.clear()

    hero_data = HEROES[hero_name]
    level_data = LEVELS[level - 1]

    hero = pygame.Rect(130, 430, 60, 95)
    enemy = pygame.Rect(880, 430, 65, 95)

    hero_max = hero_data["hp"] + (level - 1) * 5

    hero_hp = hero_max
    hero_energy = 100

    enemy_max = level_data["hp"]
    enemy_hp = enemy_max

    vx = 0
    vy = 0

    on_ground = True
    blocking = False
    facing = 1

    attack_cd = 0
    special_cd = 0
    dash_cd = 0

    enemy_cd = 0
    enemy_special_cd = 0

    combo = 0
    combo_timer = 0

    rage = False
    winner = ""

    special_effect_timer = 0
    special_effect_type = ""

    burn_timer = 0
    enemy_knockback = 0

    particles.clear()
    damage_numbers.clear()
    projectiles.clear()
    attack_anim_timer = 0


def start_game():

    global level
    global unlocked
    global state

    level = 1

    unlocked = {"ATTACK"}

    reset_level()

    state = LEVEL_INTRO


def load_level(number):

    global level
    global unlocked
    global state

    level = number

    unlocked.add("ATTACK")

    if level >= 2:
        unlocked.add("JUMP")

    if level >= 3:
        unlocked.add("SPECIAL")

    if level >= 4:
        unlocked.add("BLOCK")

    if level >= 5:
        unlocked.add("DASH")

    if level >= 6:
        unlocked.add("COMBO")

    if level >= 7:
        unlocked.add("ULTIMATE")

    reset_level()

    state = LEVEL_INTRO


def burst(x, y, color, amount=12):

    for _ in range(amount):

        angle = random.uniform(0, math.tau)
        speed = random.uniform(1, 5)

        particles.append([
            x,
            y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            random.randint(15, 35),
            color
        ])


def damage_number(x, y, amount, color=RED):

    damage_numbers.append([
        x,
        y,
        str(int(amount)),
        45,
        color
    ])


def update_effects():

    for p in particles[:]:

        p[0] += p[2]
        p[1] += p[3]

        p[3] += 0.1
        p[4] -= 1

        if p[4] <= 0:
            particles.remove(p)

    for d in damage_numbers[:]:

        d[1] -= 1
        d[3] -= 1

        if d[3] <= 0:
            damage_numbers.remove(d)


def draw_effects():

    for p in particles:

        pygame.draw.circle(
            screen,
            p[5],
            (int(p[0]), int(p[1])),
            max(1, p[4] // 10)
        )

    for d in damage_numbers:

        draw_text(
            d[2],
            FONT,
            (int(d[0]), int(d[1])),
            d[4],
            True
        )


def damage_enemy(amount, color=RED):

    global enemy_hp
    global enemy_knockback

    enemy_hp = max(
        0,
        enemy_hp - amount
    )

    damage_number(
        enemy.centerx,
        enemy.top - 20,
        amount,
        color
    )

    burst(
        enemy.centerx,
        enemy.centery,
        color,
        15
    )

    enemy_knockback = 8


def damage_player(amount):

    global hero_hp

    if blocking:

        if hero_name == "GUARDIAN":

            amount = max(
                1,
                int(amount * 0.15)
            )

            burst(
                hero.centerx,
                hero.centery,
                GREEN,
                10
            )

        else:

            amount = max(
                1,
                int(amount * 0.30)
            )

            burst(
                hero.centerx,
                hero.centery,
                CYAN,
                8
            )

    hero_hp = max(
        0,
        hero_hp - amount
    )

    damage_number(
        hero.centerx,
        hero.top - 20,
        amount,
        RED
    )


def hero_in_attack_range(extra=0):

    distance = abs(
        hero.centerx - enemy.centerx
    )

    hitbox = enemy.inflate(
        70 + extra,
        30 + extra
    )

    return (
        distance <= 185 + extra
        and hero.colliderect(hitbox)
    )


def enemy_can_hit():

    distance = abs(
        hero.centerx - enemy.centerx
    )

    vertical = hero.colliderect(enemy)

    return (
        distance <= 125
        and vertical
    )


def spawn_projectile(kind, x, y, direction, damage, color, speed=9, size=12, lifetime=90):
    projectiles.append({
        "kind": kind,
        "x": float(x),
        "y": float(y),
        "direction": direction,
        "damage": damage,
        "color": color,
        "speed": speed,
        "size": size,
        "life": lifetime
    })


def hero_attack():
    global attack_cd
    global combo
    global combo_timer
    global hero_energy
    global attack_anim_timer
    global burn_timer

    if attack_cd > 0:
        return

    attack_cd = 20
    attack_anim_timer = 10

    if "COMBO" in unlocked and combo_timer > 0:
        combo += 1
    else:
        combo = 1

    combo_timer = 55

    damage = HEROES[hero_name]["attack"]

    if "COMBO" in unlocked:
        damage += min(combo - 1, 4) * 5

    if hero_name == "THUNDER":
        spawn_projectile(
            "LIGHTNING", hero.centerx + facing * 35, hero.centery - 5,
            facing, damage, CYAN, 13, 10, 55
        )
        burst(hero.centerx + facing * 55, hero.centery, CYAN, 8)

    elif hero_name == "FLAME":
        spawn_projectile(
            "FIREBALL", hero.centerx + facing * 35, hero.centery - 5,
            facing, damage, ORANGE, 10, 14, 70
        )
        burst(hero.centerx + facing * 45, hero.centery, ORANGE, 10)

    elif hero_name == "SHADOW":
        spawn_projectile(
            "SHADOW", hero.centerx + facing * 35, hero.centery - 5,
            facing, damage, PURPLE, 14, 11, 55
        )
        burst(hero.centerx + facing * 50, hero.centery, PURPLE, 12)

    elif hero_name == "GUARDIAN":
        spawn_projectile(
            "SHIELD", hero.centerx + facing * 40, hero.centery,
            facing, damage, GREEN, 8, 20, 60
        )
        burst(hero.centerx + facing * 50, hero.centery, GREEN, 10)

    hero_energy = min(100, hero_energy + 8)


def hero_special():

    global special_cd
    global hero_energy
    global special_effect_timer
    global special_effect_type
    global burn_timer
    global enemy_knockback

    if "SPECIAL" not in unlocked:
        return

    if special_cd > 0:
        return

    if hero_energy < 30:
        return

    special_cd = 75

    hero_energy -= 30

    special_effect_timer = 25

    if hero_name == "THUNDER":

        special_effect_type = "THUNDER"

        damage = 55

        if "ULTIMATE" in unlocked:
            damage += 10

        spawn_projectile(
            "LIGHTNING", hero.centerx + facing * 40, hero.centery - 10,
            facing, damage, CYAN, 15, 15, 70
        )

        if False and hero_in_attack_range(100):

            damage_enemy(
                damage,
                CYAN
            )

            for i in range(3):

                burst(
                    enemy.centerx + random.randint(-30, 30),
                    enemy.centery + random.randint(-40, 20),
                    CYAN,
                    18
                )


    elif hero_name == "FLAME":

        special_effect_type = "FLAME"

        damage = 70

        if "ULTIMATE" in unlocked:
            damage += 15

        spawn_projectile(
            "FIREBALL", hero.centerx + facing * 40, hero.centery - 10,
            facing, damage, ORANGE, 11, 20, 80
        )

        if False and hero_in_attack_range(120):

            damage_enemy(
                damage,
                ORANGE
            )

            burn_timer = 180

            burst(
                enemy.centerx,
                enemy.centery,
                ORANGE,
                45
            )


    elif hero_name == "SHADOW":

        special_effect_type = "SHADOW"

        damage = 80

        if "ULTIMATE" in unlocked:
            damage += 20

        spawn_projectile(
            "SHADOW", hero.centerx + facing * 40, hero.centery - 10,
            facing, damage, PURPLE, 16, 17, 65
        )

        if False and hero_in_attack_range(140):

            damage_enemy(
                damage,
                PURPLE
            )

            hero.x = enemy.x - 100

            burst(
                enemy.centerx,
                enemy.centery,
                PURPLE,
                50
            )


    elif hero_name == "GUARDIAN":

        special_effect_type = "GUARDIAN"

        damage = 50

        if "ULTIMATE" in unlocked:
            damage += 15

        spawn_projectile(
            "SHIELD", hero.centerx + facing * 45, hero.centery,
            facing, damage, GREEN, 9, 26, 70
        )

        if hero_in_attack_range(80):

            damage_enemy(
                damage,
                GREEN
            )

            enemy_knockback = 25

            burst(
                enemy.centerx,
                enemy.centery,
                GREEN,
                35
            )


def hero_dash():

    global dash_cd

    if "DASH" not in unlocked:
        return

    if dash_cd > 0:
        return

    dash_cd = 70

    direction = facing

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        direction = -1

    if keys[pygame.K_RIGHT]:
        direction = 1

    hero.x += direction * 145

    hero.x = max(
        20,
        min(WIDTH - 90, hero.x)
    )

    if hero_name == "SHADOW":

        hero.x += direction * 45

    burst(
        hero.centerx,
        hero.centery,
        HEROES[hero_name]["color"],
        20
    )

def update_projectiles():
    global burn_timer
    for shot in projectiles[:]:
        shot["x"] += shot["speed"] * shot["direction"]
        shot["life"] -= 1

        if random.random() < 0.8:
            burst(
                shot["x"] - shot["direction"] * 8,
                shot["y"],
                shot["color"],
                1
            )

        shot_rect = pygame.Rect(
            int(shot["x"] - shot["size"]),
            int(shot["y"] - shot["size"]),
            shot["size"] * 2,
            shot["size"] * 2
        )

        if shot_rect.colliderect(enemy):
            damage_enemy(shot["damage"], shot["color"])

            if shot["kind"] == "FIREBALL":
                burn_timer = max(burn_timer, 100)

            if shot["kind"] == "SHADOW":
                burst(shot["x"], shot["y"], PURPLE, 18)

            elif shot["kind"] == "LIGHTNING":
                burst(shot["x"], shot["y"], CYAN, 20)

            elif shot["kind"] == "FIREBALL":
                burst(shot["x"], shot["y"], ORANGE, 24)

            elif shot["kind"] == "SHIELD":
                burst(shot["x"], shot["y"], GREEN, 22)

            projectiles.remove(shot)

        elif (
            shot["life"] <= 0
            or shot["x"] < -50
            or shot["x"] > WIDTH + 50
        ):
            projectiles.remove(shot)


def draw_projectiles():
    for shot in projectiles:
        x = int(shot["x"])
        y = int(shot["y"])
        r = int(shot["size"])
        color = shot["color"]

        if shot["kind"] == "LIGHTNING":
            points = [
                (x - r, y),
                (x, y - r),
                (x - 2, y - 3),
                (x + r, y),
                (x, y + r),
                (x + 2, y + 3)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.circle(screen, WHITE, (x, y), max(2, r // 3))

        elif shot["kind"] == "FIREBALL":
            pygame.draw.circle(screen, ORANGE, (x, y), r + 5)
            pygame.draw.circle(screen, GOLD, (x, y), r)
            pygame.draw.circle(screen, WHITE, (x - r // 3, y - r // 3), max(2, r // 3))

        elif shot["kind"] == "SHADOW":
            pygame.draw.circle(screen, PURPLE, (x, y), r)
            pygame.draw.circle(screen, BLACK, (x, y), max(2, r // 2))
            pygame.draw.circle(screen, PURPLE, (x, y), r, 2)

        elif shot["kind"] == "SHIELD":
            pygame.draw.circle(screen, GREEN, (x, y), r, 5)
            pygame.draw.circle(screen, GOLD, (x, y), max(3, r - 7), 3)

        # glow ring
        pygame.draw.circle(screen, color, (x, y), r + 5, 2)


def spawn_enemy_projectile():

    info = LEVELS[level - 1]

    if level < 3:
        return

    direction = -1 if enemy.centerx > hero.centerx else 1

    if info["enemy"] == "POWER BOT":
        kind, color, size, speed = "ENERGY", CYAN, 11, 7
    elif info["enemy"] == "BRUISER":
        kind, color, size, speed = "SHOCKWAVE", GOLD, 16, 6
    elif info["enemy"] == "SPEED DEMON":
        kind, color, size, speed = "DARK", PURPLE, 9, 10
    elif info["enemy"] in ("RAGE LORD", "DARK OVERLORD"):
        kind, color, size, speed = "CHAOS", RED, 15, 8
    else:
        kind, color, size, speed = "ENERGY", RED, 10, 6

    enemy_projectiles.append({
        "kind": kind,
        "x": float(enemy.centerx),
        "y": float(enemy.centery),
        "direction": direction,
        "damage": info["atk"] + (8 if rage else 0),
        "color": color,
        "speed": speed,
        "size": size,
        "life": 100
    })


def update_enemy_projectiles():

    global hero_hp

    for shot in enemy_projectiles[:]:

        shot["x"] += shot["speed"] * shot["direction"]
        shot["life"] -= 1

        shot_rect = pygame.Rect(
            int(shot["x"] - shot["size"]),
            int(shot["y"] - shot["size"]),
            shot["size"] * 2,
            shot["size"] * 2
        )

        if shot_rect.colliderect(hero):
            damage_player(shot["damage"])
            burst(shot["x"], shot["y"], shot["color"], 18)
            enemy_projectiles.remove(shot)

        elif shot["life"] <= 0 or shot["x"] < -60 or shot["x"] > WIDTH + 60:
            enemy_projectiles.remove(shot)


def draw_enemy_projectiles():

    for shot in enemy_projectiles:
        x, y = int(shot["x"]), int(shot["y"])
        r = int(shot["size"])
        c = shot["color"]

        if shot["kind"] == "ENERGY":
            pygame.draw.circle(screen, c, (x, y), r)
            pygame.draw.circle(screen, WHITE, (x, y), max(2, r // 3))
        elif shot["kind"] == "SHOCKWAVE":
            pygame.draw.circle(screen, c, (x, y), r, 5)
            pygame.draw.circle(screen, WHITE, (x, y), max(2, r // 3), 2)
        elif shot["kind"] == "DARK":
            pygame.draw.circle(screen, BLACK, (x, y), r)
            pygame.draw.circle(screen, c, (x, y), r, 4)
        else:
            pygame.draw.circle(screen, RED, (x, y), r + 4)
            pygame.draw.circle(screen, GOLD, (x, y), r)
            pygame.draw.circle(screen, WHITE, (x, y), max(2, r // 3))

        pygame.draw.circle(screen, c, (x, y), r + 5, 2)


def update_battle():

    global vx
    global vy
    global on_ground
    global blocking
    global facing

    global attack_cd
    global special_cd
    global dash_cd

    global enemy_cd
    global enemy_special_cd

    global combo
    global combo_timer
    global rage

    global hero_energy

    global burn_timer
    global enemy_knockback

    global special_effect_timer
    global special_effect_type
    global attack_anim_timer

    global state
    global winner

    keys = pygame.key.get_pressed()

    vx = 0

    if keys[pygame.K_LEFT]:

        vx = -HEROES[hero_name]["speed"]
        facing = -1

    if keys[pygame.K_RIGHT]:

        vx = HEROES[hero_name]["speed"]
        facing = 1

    hero.x += int(vx)

    hero.x = max(
        20,
        min(WIDTH - 90, hero.x)
    )

    if (
        "JUMP" in unlocked
        and keys[pygame.K_UP]
        and on_ground
    ):

        vy = -13
        on_ground = False

    vy += 0.7
    hero.y += int(vy)

    ground = 525

    if hero.bottom >= ground:

        hero.bottom = ground
        vy = 0
        on_ground = True


    blocking = (
        keys[pygame.K_LSHIFT]
        or keys[pygame.K_RSHIFT]
    )

    if "BLOCK" not in unlocked:
        blocking = False

    if attack_cd > 0:
        attack_cd -= 1

    if special_cd > 0:
        special_cd -= 1

    if dash_cd > 0:
        dash_cd -= 1

    if enemy_cd > 0:
        enemy_cd -= 1

    if enemy_special_cd > 0:
        enemy_special_cd -= 1

    if special_effect_timer > 0:
        special_effect_timer -= 1
    else:
        special_effect_type = ""

    if attack_anim_timer > 0:
        attack_anim_timer -= 1

    update_projectiles()
    update_enemy_projectiles()

    if combo_timer > 0:

        combo_timer -= 1

    else:

        combo = 0

    hero_energy = min(
        100,
        hero_energy + 0.08
    )
    
    if burn_timer > 0:

        burn_timer -= 1

        if burn_timer % 30 == 0:

            damage_enemy(
                3,
                ORANGE
            )

    dx = hero.centerx - enemy.centerx

    if enemy_knockback > 0:

        if dx > 0:
            enemy.x -= enemy_knockback
        else:
            enemy.x += enemy_knockback

        enemy_knockback -= 1

    elif abs(dx) > 90:

        if dx > 0:

            enemy.x += LEVELS[level - 1]["speed"]

        else:

            enemy.x -= LEVELS[level - 1]["speed"]

    enemy.x = max(
        250,
        min(WIDTH - 90, enemy.x)
    )

    rage = (
        level >= 7
        and enemy_hp <= enemy_max * 0.45
    )

    if (
        rage
        and abs(dx) < 180
        and enemy_special_cd == 0
    ):

        enemy_special_cd = 110

        if level >= 3:
            spawn_enemy_projectile()

        if enemy_can_hit():

            damage_player(
                LEVELS[level - 1]["atk"] + 12
            )

        burst(
            enemy.centerx,
            enemy.centery,
            RED,
            25
        )

    elif (
        abs(dx) < 125
        and enemy_cd == 0
    ):

        if rage:
            enemy_cd = 35
        else:
            enemy_cd = 55

        if enemy_can_hit():

            damage = LEVELS[level - 1]["atk"]

            if rage:
                damage += 8

            damage_player(damage)

    if (
        level >= 3
        and abs(dx) >= 220
        and enemy_cd == 0
    ):
        enemy_cd = 80 if not rage else 55
        spawn_enemy_projectile()

    if enemy_hp <= 0:

        winner = "HERO"
        state = LEVEL_CLEAR

    elif hero_hp <= 0:

        winner = "ENEMY"
        state = GAME_OVER

def draw_background():

    screen.fill(
        (12, 16, 30)
    )
    
    for x in range(0, WIDTH, 50):

        pygame.draw.line(
            screen,
            (27, 37, 58),
            (x, 0),
            (x, 525)
        )

    for y in range(0, 526, 50):

        pygame.draw.line(
            screen,
            (27, 37, 58),
            (0, y),
            (WIDTH, y)
        )

    pygame.draw.rect(
        screen,
        (35, 40, 52),
        (0, 525, WIDTH, 125)
    )

    pygame.draw.line(
        screen,
        GOLD,
        (0, 525),
        (WIDTH, 525),
        3
    )

def draw_character(rect, color, name, enemy_character=False):

    pygame.draw.ellipse(
        screen,
        (5, 5, 10),
        (
            rect.x - 5,
            515,
            rect.w + 10,
            15
        )
    )

    pygame.draw.circle(
        screen,
        color,
        (
            rect.centerx,
            rect.y + 20
        ),
        20
    )

    pygame.draw.rect(
        screen,
        color,
        (
            rect.x,
            rect.y + 35,
            rect.w,
            55
        ),
        border_radius=10
    )

    pygame.draw.line(
        screen,
        color,
        (
            rect.x + 18,
            rect.bottom - 5
        ),
        (
            rect.x + 10,
            rect.bottom + 5
        ),
        8
    )

    pygame.draw.line(
        screen,
        color,
        (
            rect.right - 18,
            rect.bottom - 5
        ),
        (
            rect.right - 10,
            rect.bottom + 5
        ),
        8
    )

    if enemy_character:

        pygame.draw.circle(
            screen,
            RED,
            (
                rect.centerx - 7,
                rect.y + 17
            ),
            4
        )

        pygame.draw.circle(
            screen,
            RED,
            (
                rect.centerx + 7,
                rect.y + 17
            ),
            4
        )

    else:

        pygame.draw.circle(
            screen,
            WHITE,
            (
                rect.centerx - 7,
                rect.y + 17
            ),
            3
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                rect.centerx + 7,
                rect.y + 17
            ),
            3
        )

    if name == "GUARDIAN" and not enemy_character:

        pygame.draw.circle(
            screen,
            GOLD,
            (
                rect.right + 12,
                rect.centery
            ),
            18,
            4
        )
    if name == "FLAME" and not enemy_character:

        pygame.draw.circle(
            screen,
            ORANGE,
            rect.center,
            48,
            2
        )

    if name == "SHADOW" and not enemy_character:

        pygame.draw.circle(
            screen,
            PURPLE,
            rect.center,
            47,
            2
        )

    if name == "THUNDER" and not enemy_character:

        points = [
            (rect.centerx + 3, rect.y + 45),
            (rect.centerx - 7, rect.y + 65),
            (rect.centerx + 2, rect.y + 65),
            (rect.centerx - 5, rect.y + 82),
            (rect.centerx + 12, rect.y + 57),
            (rect.centerx + 3, rect.y + 57)
        ]

        pygame.draw.polygon(
            screen,
            GOLD,
            points
        )

    if not enemy_character and attack_anim_timer > 0:
        hand_x = rect.centerx + facing * (rect.w // 2 + 28)
        hand_y = rect.y + 50
        pygame.draw.line(
            screen,
            HEROES[hero_name]["color"],
            (rect.centerx, hand_y),
            (hand_x, hand_y),
            10
        )
        pygame.draw.circle(
            screen,
            WHITE,
            (hand_x, hand_y),
            5
        )

    draw_text(
        name,
        SMALL,
        (
            rect.centerx,
            rect.y - 25
        ),
        WHITE,
        True
    )

def draw_bar(
    x,
    y,
    width,
    height,
    value,
    maximum,
    color,
    label
):

    pygame.draw.rect(
        screen,
        BLACK,
        (x, y, width, height),
        border_radius=6
    )

    fill = int(
        (width - 6)
        * max(0, value)
        / maximum
    )

    pygame.draw.rect(
        screen,
        color,
        (
            x + 3,
            y + 3,
            fill,
            height - 6
        ),
        border_radius=4
    )

    draw_text(
        f"{label}: {int(value)}/{int(maximum)}",
        SMALL,
        (
            x + 8,
            y + 3
        )
    )

def draw_special_effect():

    if special_effect_timer <= 0:
        return

    if special_effect_type == "THUNDER":

        for i in range(3):

            x = enemy.centerx + random.randint(-30, 30)

            pygame.draw.line(
                screen,
                CYAN,
                (x, 70),
                (
                    x + random.randint(-20, 20),
                    enemy.top
                ),
                5
            )

    elif special_effect_type == "FLAME":

        radius = 70 + (
            25 - special_effect_timer
        ) * 3

        pygame.draw.circle(
            screen,
            ORANGE,
            enemy.center,
            radius,
            6
        )

        pygame.draw.circle(
            screen,
            GOLD,
            enemy.center,
            max(10, radius - 20),
            4
        )

    elif special_effect_type == "SHADOW":

        for r in range(20, 100, 20):

            pygame.draw.circle(
                screen,
                PURPLE,
                enemy.center,
                r,
                3
            )

    elif special_effect_type == "GUARDIAN":

        pygame.draw.circle(
            screen,
            GREEN,
            enemy.center,
            80,
            7
        )

        pygame.draw.line(
            screen,
            GOLD,
            (
                enemy.centerx - 60,
                enemy.centery
            ),
            (
                enemy.centerx + 60,
                enemy.centery
            ),
            8
        )


def draw_battle():

    draw_background()

    info = LEVELS[level - 1]

    draw_character(
        hero,
        HEROES[hero_name]["color"],
        hero_name
    )

    draw_character(
        enemy,
        RED,
        info["enemy"],
        True
    )

    draw_projectiles()
    draw_enemy_projectiles()
    draw_special_effect()

    draw_bar(
        25,
        20,
        330,
        28,
        hero_hp,
        hero_max,
        GREEN,
        hero_name + " HP"
    )

    draw_bar(
        745,
        20,
        330,
        28,
        enemy_hp,
        enemy_max,
        RED,
        info["enemy"] + " HP"
    )

    draw_bar(
        25,
        55,
        270,
        22,
        hero_energy,
        100,
        CYAN,
        "ENERGY"
    )

    draw_text(
        f"POWER: {HEROES[hero_name]['power']}",
        SMALL,
        (25, 85),
        HEROES[hero_name]["color"]
    )

    draw_text(
        f"LEVEL {level}/8",
        FONT,
        (
            WIDTH // 2,
            65
        ),
        GOLD,
        True
    )
    draw_text(
        f"VILLAIN: {info['enemy']}",
        SMALL,
        (745, 55),
        RED
    )

    if rage:

        draw_text(
            "⚠ RAGE MODE ⚠",
            FONT,
            (
                WIDTH // 2,
                120
            ),
            RED,
            True
        )

    if combo > 1:

        draw_text(
            f"COMBO x{combo}",
            BIG,
            (
                WIDTH // 2,
                170
            ),
            GOLD,
            True
        )

    if blocking:

        draw_text(
            "🛡 BLOCKING",
            FONT,
            (
                WIDTH // 2,
                500
            ),
            CYAN,
            True
        )

    if level == 1:

        controls = (
            "← → MOVE     SPACE ATTACK"
        )

    elif level == 2:

        controls = (
            "← → MOVE     UP JUMP     SPACE ATTACK"
        )

    elif level == 3:

        controls = (
            "SPACE ATTACK     E SPECIAL"
        )

    elif level == 4:

        controls = (
            "SPACE ATTACK     SHIFT BLOCK"
        )

    elif level == 5:

        controls = (
            "SPACE ATTACK     F DASH"
        )

    else:

        controls = (
            "← → MOVE   UP JUMP   SPACE ATTACK   "
            "E SPECIAL   SHIFT BLOCK   F DASH"
        )

    draw_text(
        controls,
        SMALL,
        (
            WIDTH // 2,
            610
        ),
        WHITE,
        True
    )

def draw_menu():

    screen.fill(BLACK)

    draw_text(
        "SUPERHERO",
        HUGE,
        (
            WIDTH // 2,
            65
        ),
        CYAN,
        True
    )

    draw_text(
        "BATTLE ARENA",
        HUGE,
        (
            WIDTH // 2,
            130
        ),
        GOLD,
        True
    )

    draw_text(
        "CHOOSE YOUR HERO",
        BIG,
        (
            WIDTH // 2,
            195
        ),
        WHITE,
        True
    )

    card_width = 250
    card_height = 190

    start_x = 15
    gap = 15

    for i, name in enumerate(HERO_NAMES):

        data = HEROES[name]

        x = start_x + i * (
            card_width + gap
        )

        y = 250

        if i == selected:

            pygame.draw.rect(
                screen,
                GOLD,
                (
                    x - 5,
                    y - 5,
                    card_width + 10,
                    card_height + 10
                ),
                border_radius=18
            )

        pygame.draw.rect(
            screen,
            data["color"],
            (
                x,
                y,
                card_width,
                card_height
            ),
            border_radius=15
        )

        draw_text(
            name,
            FONT,
            (
                x + card_width // 2,
                y + 28
            ),
            BLACK,
            True
        )

        draw_text(
            data["power"],
            SMALL,
            (
                x + card_width // 2,
                y + 55
            ),
            BLACK,
            True
        )

        draw_text(
            f"❤️ HP: {data['hp']}",
            SMALL,
            (
                x + card_width // 2,
                y + 88
            ),
            BLACK,
            True
        )

        draw_text(
            f"⚔ DAMAGE: {data['attack']}",
            SMALL,
            (
                x + card_width // 2,
                y + 113
            ),
            BLACK,
            True
        )

        draw_text(
            f"⚡ SPECIAL: {data['special']}",
            SMALL,
            (
                x + card_width // 2,
                y + 138
            ),
            BLACK,
            True
        )

        draw_text(
            f"🏃 SPEED: {data['speed']}",
            SMALL,
            (
                x + card_width // 2,
                y + 163
            ),
            BLACK,
            True
        )

    draw_text(
        "← → or A / D     SELECT HERO",
        FONT,
        (
            WIDTH // 2,
            475
        ),
        WHITE,
        True
    )

    draw_text(
        "ENTER / SPACE     START CAMPAIGN",
        FONT,
        (
            WIDTH // 2,
            515
        ),
        GOLD,
        True
    )

    draw_text(
        "ESC     QUIT",
        SMALL,
        (
            WIDTH // 2,
            555
        ),
        GREY,
        True
    )

def draw_intro():

    screen.fill(BLACK)

    info = LEVELS[level - 1]

    hero_color = HEROES[hero_name]["color"]

    draw_text(
        f"LEVEL {level}",
        HUGE,
        (
            WIDTH // 2,
            85
        ),
        GOLD,
        True
    )

    draw_text(
        info["name"],
        BIG,
        (
            WIDTH // 2,
            165
        ),
        CYAN,
        True
    )

    draw_text(
        f"HERO: {hero_name}",
        FONT,
        (
            WIDTH // 2,
            225
        ),
        hero_color,
        True
    )

    draw_text(
        f"POWER: {HEROES[hero_name]['power']}",
        FONT,
        (
            WIDTH // 2,
            260
        ),
        hero_color,
        True
    )

    draw_text(
        f"Enemy: {info['enemy']}",
        FONT,
        (
            WIDTH // 2,
            305
        ),
        WHITE,
        True
    )

    draw_text(
        f"NEW SKILL: {info['unlock']}",
        FONT,
        (
            WIDTH // 2,
            350
        ),
        GREEN,
        True
    )

    draw_text(
        info["tip"],
        SMALL,
        (
            WIDTH // 2,
            395
        ),
        WHITE,
        True
    )

    draw_text(
        "ENTER / SPACE  →  BEGIN LEVEL",
        FONT,
        (
            WIDTH // 2,
            475
        ),
        GOLD,
        True
    )

    draw_text(
        f"Campaign Progress: {level - 1}/8 completed",
        SMALL,
        (
            WIDTH // 2,
            525
        ),
        GREY,
        True
    )

def draw_level_clear():

    screen.fill(BLACK)

    draw_text(
        "LEVEL CLEARED!",
        HUGE,
        (
            WIDTH // 2,
            125
        ),
        GREEN,
        True
    )

    if level < 8:

        draw_text(
            f"{LEVELS[level - 1]['unlock']} MASTERED!",
            BIG,
            (
                WIDTH // 2,
                220
            ),
            GOLD,
            True
        )

        draw_text(
            f"NEXT: LEVEL {level + 1}",
            FONT,
            (
                WIDTH // 2,
                290
            ),
            CYAN,
            True
        )

        draw_text(
            LEVELS[level]["name"],
            FONT,
            (
                WIDTH // 2,
                325
            ),
            WHITE,
            True
        )

        draw_text(
            "ENTER / SPACE → NEXT LEVEL",
            FONT,
            (
                WIDTH // 2,
                410
            ),
            GOLD,
            True
        )

    else:

        draw_text(
            "FINAL BOSS DEFEATED!",
            BIG,
            (
                WIDTH // 2,
                230
            ),
            GOLD,
            True
        )

        draw_text(
            "YOU ARE A SUPERHERO MASTER!",
            FONT,
            (
                WIDTH // 2,
                300
            ),
            CYAN,
            True
        )

        draw_text(
            "ENTER → HERO MENU",
            FONT,
            (
                WIDTH // 2,
                400
            ),
            WHITE,
            True
        )

def draw_game_over():

    screen.fill(BLACK)

    draw_text(
        "DEFEATED!",
        HUGE,
        (
            WIDTH // 2,
            150
        ),
        RED,
        True
    )

    draw_text(
        f"LEVEL {level}",
        BIG,
        (
            WIDTH // 2,
            240
        ),
        WHITE,
        True
    )

    draw_text(
        "R → RETRY LEVEL",
        FONT,
        (
            WIDTH // 2,
            350
        ),
        GOLD,
        True
    )

    draw_text(
        "ESC → QUIT",
        SMALL,
        (
            WIDTH // 2,
            405
        ),
        GREY,
        True
    )

UPGRADE_STATE = "UPGRADES"

xp = 0
coins = 100
hero_rank = 1
boss_phase = 1
minions = []
minion_spawned = False
arena_flash = 0
sound_on = False
upgrade_levels = {"POWER": 0, "ARMOR": 0, "SPEED": 0, "ENERGY": 0}
stats = {"damage": 0, "defeated": 0}
message = ""
message_timer = 0


# Keep the original states but add an upgrade screen.


def award_xp(amount):
    global xp, hero_rank, coins
    xp += int(amount)
    coins += max(1, int(amount / 5))
    needed = hero_rank * 100
    while xp >= needed:
        xp -= needed
        hero_rank += 1
        coins += 25
        set_message(f"HERO RANK UP!  RANK {hero_rank}", 150)
        needed = hero_rank * 100


def set_message(text, frames=120):
    global message, message_timer
    message = text
    message_timer = frames


def save_game():
    data = {
        "level": level,
        "hero": hero_name,
        "xp": xp,
        "coins": coins,
        "rank": hero_rank,
        "upgrades": upgrade_levels,
    }
    try:
        with open("superhero_save.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def load_game():
    global level, hero_name, selected, xp, coins, hero_rank, upgrade_levels, unlocked
    try:
        with open("superhero_save.json", "r", encoding="utf-8") as f:
            d = json.load(f)
        level = max(1, min(8, int(d.get("level", 1))))
        hero_name = d.get("hero", "THUNDER")
        if hero_name not in HEROES:
            hero_name = "THUNDER"
        selected = HERO_NAMES.index(hero_name)
        xp = int(d.get("xp", 0))
        coins = int(d.get("coins", 0))
        hero_rank = max(1, int(d.get("rank", 1)))
        for k in upgrade_levels:
            upgrade_levels[k] = max(0, int(d.get("upgrades", {}).get(k, 0)))
        unlocked = set(UNLOCKS[level])
        return True
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False


def spawn_minion(kind, x, hp, atk, speed):
    minions.append({
        "kind": kind,
        "rect": pygame.Rect(x, 440, 52 if kind == "DRONE" else 62, 82),
        "hp": hp,
        "max_hp": hp,
        "atk": atk,
        "speed": speed,
        "cd": random.randint(30, 80),
        "color": CYAN if kind == "DRONE" else RED,
    })


def setup_minions():
    global minions, minion_spawned
    minions = []
    minion_spawned = True
    if level == 6:
        spawn_minion("DRONE", 690, 55, 10, 1.4)
        spawn_minion("DRONE", 760, 55, 10, 1.4)
    elif level == 7:
        spawn_minion("GUARD", 700, 85, 14, 1.2)
        spawn_minion("DRONE", 790, 60, 11, 1.5)
    elif level == 8:
        spawn_minion("GUARD", 690, 105, 16, 1.3)
        spawn_minion("DRONE", 770, 65, 12, 1.6)
        spawn_minion("DRONE", 835, 65, 12, 1.6)


_base_reset_level = reset_level

def reset_level():
    global boss_phase, arena_flash, message, message_timer, hero_max, hero_hp, hero_energy
    _base_reset_level()
    hero_max = int(HEROES[hero_name]["hp"] + upgrade_levels["ARMOR"] * 15)
    hero_hp = hero_max
    hero_energy = min(100 + upgrade_levels["ENERGY"] * 10, 200)
    boss_phase = 1
    arena_flash = 0
    message = ""
    message_timer = 0
    setup_minions()
    HEROES[hero_name]["speed"] = HEROES[hero_name].get("base_speed", HEROES[hero_name]["speed"]) + upgrade_levels["SPEED"] * 0.25


_base_damage_enemy = damage_enemy

def damage_enemy(amount, color=RED):
    _base_damage_enemy(amount, color)
    award_xp(max(1, amount))

    if level >= 3 and random.random() < 0.045:
        pickups.append({"x": float(enemy.centerx), "y": float(enemy.centery), "kind": random.choice(["HP", "ENERGY", "POWER"]), "life": 600})


def damage_minion(minion, amount, color):
    global coins
    minion["hp"] = max(0, minion["hp"] - amount)
    damage_number(minion["rect"].centerx, minion["rect"].top - 12, amount, color)
    burst(minion["rect"].centerx, minion["rect"].centery, color, 8)
    award_xp(max(1, amount // 2))
    if minion["hp"] <= 0:
        burst(minion["rect"].centerx, minion["rect"].centery, GOLD, 25)
        stats["defeated"] += 1
        coins += 10


def nearest_minion(max_distance=145):
    living = [m for m in minions if m["hp"] > 0]
    if not living:
        return None
    living.sort(key=lambda m: abs(m["rect"].centerx - hero.centerx))
    m = living[0]
    return m if abs(m["rect"].centerx - hero.centerx) <= max_distance else None


_base_hero_attack = hero_attack

def hero_attack():

    m = nearest_minion(125)
    if m is not None and abs(m["rect"].centery - hero.centery) < 90:
        global attack_cd, attack_anim_timer
        if "ATTACK" not in unlocked or attack_cd > 0:
            return
        attack_cd = 22
        attack_anim_timer = 10
        damage_minion(m, HEROES[hero_name]["attack"] + upgrade_levels["POWER"] * 4, HEROES[hero_name]["color"])
        return
    _base_hero_attack()


_base_hero_special = hero_special

def hero_special():
    m = nearest_minion(170)
    if m is not None and abs(m["rect"].centery - hero.centery) < 100:
        global special_cd, hero_energy, special_anim_timer
        if "SPECIAL" not in unlocked or special_cd > 0 or hero_energy < 30:
            return
        special_cd = 80
        hero_energy -= 30
        special_anim_timer = 25
        damage = HEROES[hero_name]["special"] + upgrade_levels["POWER"] * 7
        damage_minion(m, damage, HEROES[hero_name]["color"])
        burst(m["rect"].centerx, m["rect"].centery, HEROES[hero_name]["color"], 30)
        return
    _base_hero_special()


def update_minions():
    global minions
    for m in minions:
        if m["hp"] <= 0:
            continue
        r = m["rect"]
        dx = hero.centerx - r.centerx
        if abs(dx) > 80:
            r.x += 1 if dx > 0 else -1
            if abs(dx) > 250 and m["kind"] == "DRONE" and m["cd"] <= 0:
                direction = 1 if dx > 0 else -1
                spawn_enemy_projectile_from_minion(m, direction)
                m["cd"] = 100
        else:
            if m["cd"] <= 0:
                damage_player(m["atk"])
                m["cd"] = 70 if m["kind"] == "DRONE" else 85
        m["cd"] -= 1
        r.x = max(300, min(WIDTH - 70, r.x))
    minions = [m for m in minions if m["hp"] > 0]


def spawn_enemy_projectile_from_minion(m, direction):
    r = m["rect"]
    enemy_projectiles.append({"kind": "ENERGY", "x": float(r.centerx), "y": float(r.centery - 10), "direction": direction, "damage": m["atk"], "color": CYAN if m["kind"] == "DRONE" else RED, "speed": 6, "size": 9, "life": 100})


def boss_phase_logic():
    global boss_phase, enemy_atk, arena_flash
    if level != 8:
        return
    ratio = enemy_hp / max(1, enemy_max)
    new_phase = 1 if ratio > 0.72 else 2 if ratio > 0.48 else 3 if ratio > 0.23 else 4
    if new_phase > boss_phase:
        boss_phase = new_phase
        arena_flash = 20
        if boss_phase == 2:
            spawn_minion("DRONE", 760, 70, 14, 1.8)
            spawn_minion("GUARD", 680, 110, 18, 1.5)
            set_message("PHASE 2 — OVERLORD SUMMONS THE ARMY!", 180)
        elif boss_phase == 3:
            spawn_minion("DRONE", 820, 75, 16, 2.0)
            set_message("PHASE 3 — RAGE UNLEASHED!", 180)
        else:
            spawn_minion("GUARD", 730, 130, 20, 1.7)
            set_message("FINAL PHASE — DARK APOCALYPSE!", 180)
        burst(enemy.centerx, enemy.centery, RED, 45)


def _ultimate_update_battle():
    global arena_flash, message_timer

    update_battle_original()
    if state != BATTLE:
        return
    update_minions()
    boss_phase_logic()
    if arena_flash > 0:
        arena_flash -= 1
    if message_timer > 0:
        message_timer -= 1
update_battle_original = update_battle
update_battle = _ultimate_update_battle


def draw_minions():
    for m in minions:
        r = m["rect"]
        c = m["color"]
        pygame.draw.rect(screen, (15, 18, 28), r, border_radius=10)
        pygame.draw.rect(screen, c, r, 3, border_radius=10)
        if m["kind"] == "DRONE":
            pygame.draw.circle(screen, c, (r.centerx, r.top + 25), 15)
            pygame.draw.circle(screen, WHITE, (r.centerx, r.top + 25), 5)
        else:
            pygame.draw.rect(screen, c, (r.x + 12, r.y + 15, r.w - 24, 42), border_radius=7)
            pygame.draw.circle(screen, WHITE, (r.centerx - 8, r.y + 30), 4)
            pygame.draw.circle(screen, WHITE, (r.centerx + 8, r.y + 30), 4)

        pygame.draw.rect(screen, BLACK, (r.x, r.y - 10, r.w, 6))
        pygame.draw.rect(screen, GREEN, (r.x, r.y - 10, int(r.w * m["hp"] / m["max_hp"]), 6))


_base_draw_background = draw_background

def draw_background():
   
    arena_index = min(5, (level - 1) // 2)
    _, top, bottom = ARENAS[arena_index]
    screen.fill(top)
    pygame.draw.rect(screen, bottom, (0, 390, WIDTH, 260))
    for x in range(0, WIDTH, 55):
        pygame.draw.line(screen, (50, 55, 75), (x, 390), (x, 650), 1)
    for y in range(400, 650, 45):
        pygame.draw.line(screen, (50, 55, 75), (0, y), (WIDTH, y), 1)
    
    for x in range(-20, WIDTH, 90):
        h = 70 + ((x * 7 + level * 13) % 100)
        pygame.draw.rect(screen, DARK, (x, 390 - h, 70, h))
        for wy in range(400 - h, 380, 22):
            pygame.draw.rect(screen, GOLD if (x + wy) % 3 == 0 else GREY, (x + 12, wy, 8, 5))
    pygame.draw.rect(screen, (12, 14, 22), (0, 520, WIDTH, 130))
    pygame.draw.line(screen, GOLD, (0, 520), (WIDTH, 520), 3)
    if level == 8:
        for i in range(8):
            pygame.draw.circle(screen, (80, 20, 50), ((i * 157 + 70) % WIDTH, 90 + (i * 37) % 210), 35, 2)


_base_draw_battle = draw_battle

def draw_battle():
    draw_background()
    info = LEVELS[level - 1]
    draw_character(hero, HEROES[hero_name]["color"], hero_name)
    draw_character(enemy, RED if level < 8 else PINK, info["enemy"], True)
    draw_minions()
    draw_projectiles()
    draw_enemy_projectiles()
    draw_special_effect()

    draw_bar(25, 20, 330, 28, hero_hp, hero_max, GREEN, hero_name + " HP")
    draw_bar(745, 20, 330, 28, enemy_hp, enemy_max, RED, info["enemy"] + " HP")
    energy_max_display = 100 + upgrade_levels["ENERGY"] * 10
    draw_bar(25, 55, 270, 22, hero_energy, energy_max_display, CYAN, "ENERGY")
    draw_text(f"RANK {hero_rank}   XP {xp}/{hero_rank * 100}   COINS {coins}", SMALL, (25, 85), GOLD)
    draw_text(f"LEVEL {level}/8", FONT, (WIDTH // 2, 55), GOLD, True)
    draw_text(f"ARENA: {ARENAS[min(5, (level - 1) // 2)][0]}", SMALL, (WIDTH // 2, 82), CYAN, True)

    if level == 8:
        draw_text(f"BOSS PHASE {boss_phase}/4", FONT, (WIDTH // 2, 112), PINK, True)
    if rage:
        draw_text("⚠ RAGE MODE ⚠", FONT, (WIDTH // 2, 140), RED, True)
    if combo > 1:
        draw_text(f"COMBO x{combo}", BIG, (WIDTH // 2, 175), GOLD, True)
    if blocking:
        draw_text("BLOCKING", FONT, (WIDTH // 2, 500), CYAN, True)
    if message_timer > 0:
        draw_text(message, FONT, (WIDTH // 2, 205), GOLD, True)

    controls = "← → MOVE | UP JUMP | SPACE ATTACK | E SPECIAL | SHIFT BLOCK | F DASH"
    draw_text(controls, SMALL, (WIDTH // 2, 615), WHITE, True)
    if arena_flash > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 40, 70, min(100, arena_flash * 5)))
        screen.blit(overlay, (0, 0))


def draw_upgrades():
    screen.fill(BLACK)
    draw_text("HERO UPGRADE LAB", HUGE, (WIDTH // 2, 70), GOLD, True)
    draw_text(f"COINS: {coins}    RANK: {hero_rank}    XP: {xp}/{hero_rank * 100}", FONT, (WIDTH // 2, 135), CYAN, True)
    items = [("POWER", "Damage +4", 1), ("ARMOR", "Max HP +15", 2), ("SPEED", "Movement +0.25", 3), ("ENERGY", "Max Energy +10", 4)]
    for i, (name, desc, key) in enumerate(items):
        x = 90 + i * 250
        lvl = upgrade_levels[name]
        rect = pygame.Rect(x, 220, 210, 220)
        pygame.draw.rect(screen, DARK, rect, border_radius=15)
        pygame.draw.rect(screen, HEROES[hero_name]["color"] if lvl else GREY, rect, 3, border_radius=15)
        draw_text(str(key), HUGE, (x + 30, 250), GOLD, True)
        draw_text(name, MED, (x + 105, 270), WHITE, True)
        draw_text(desc, SMALL, (x + 105, 320), GREY, True)
        draw_text(f"LEVEL {lvl}/5", FONT, (x + 105, 365), GREEN, True)
        cost = 25 + lvl * 20
        draw_text(f"COST {cost}", SMALL, (x + 105, 400), GOLD, True)
    draw_text("1-4 → BUY UPGRADE   |   ENTER → CONTINUE   |   U → OPEN ANYTIME", FONT, (WIDTH // 2, 510), WHITE, True)
    draw_text("Each upgrade is permanent and saved automatically.", SMALL, (WIDTH // 2, 545), GREY, True)


def buy_upgrade(key):
    global coins
    names = ["POWER", "ARMOR", "SPEED", "ENERGY"]
    name = names[key - 1]
    lvl = upgrade_levels[name]
    cost = 25 + lvl * 20
    if lvl >= 5:
        set_message("MAX LEVEL REACHED", 90)
    elif coins >= cost:
        coins -= cost
        upgrade_levels[name] += 1
        set_message(f"{name} UPGRADED TO LEVEL {upgrade_levels[name]}", 100)
        save_game()
    else:
        set_message("NOT ENOUGH COINS", 90)


def draw_clear_ultimate():
    screen.fill(BLACK)
    draw_text("LEVEL CLEARED!", HUGE, (WIDTH // 2, 105), GREEN, True)
    draw_text(f"+XP  |  COINS EARNED  |  DAMAGE {stats['damage']}", FONT, (WIDTH // 2, 190), GOLD, True)
    if level < 8:
        draw_text(f"NEXT: LEVEL {level + 1} — {LEVELS[level]["name"]}", BIG, (WIDTH // 2, 275), CYAN, True)
        draw_text("ENTER → NEXT LEVEL", FONT, (WIDTH // 2, 380), WHITE, True)
        draw_text("U → OPEN UPGRADE LAB", FONT, (WIDTH // 2, 425), GOLD, True)
        draw_text("Progress is saved automatically.", SMALL, (WIDTH // 2, 475), GREY, True)
    else:
        draw_text("DARK OVERLORD DEFEATED!", BIG, (WIDTH // 2, 250), PINK, True)
        draw_text("YOU ARE A SUPERHERO MASTER!", MED, (WIDTH // 2, 315), CYAN, True)
        draw_text("ENTER → HERO MENU", FONT, (WIDTH // 2, 410), WHITE, True)
        draw_text("Your campaign progress has been saved.", SMALL, (WIDTH // 2, 455), GREY, True)

running = True

async def main():
    global running

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state == MENU:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        globals()["selected"] = (selected - 1) % len(HERO_NAMES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        globals()["selected"] = (selected + 1) % len(HERO_NAMES)
                    elif event.key == pygame.K_c:
                        if load_game():
                            reset_level()
                            globals()["state"] = LEVEL_INTRO
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        globals()["hero_name"] = HERO_NAMES[selected]
                        start_game()
                elif state == LEVEL_INTRO:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        globals()["state"] = BATTLE
                        start_battle_music()
                elif state == BATTLE:
                    if event.key == pygame.K_u:
                        globals()["state"] = UPGRADE_STATE
                    elif event.key == pygame.K_SPACE:
                        hero_attack()
                    elif event.key == pygame.K_e:
                        hero_special()
                    elif event.key == pygame.K_f:
                        hero_dash()
                elif state == LEVEL_CLEAR:
                    if event.key == pygame.K_u:
                        globals()["state"] = UPGRADE_STATE
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if level < 8:
                            stop_battle_music()
                            load_level(level + 1)
                        else:
                            stop_battle_music()
                            globals()["state"] = MENU
                elif state == UPGRADE_STATE:
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        buy_upgrade(int(event.unicode))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if level < 8:
                            stop_battle_music()
                            load_level(level + 1)
                        else:
                            stop_battle_music()
                            globals()["state"] = MENU
                elif state == GAME_OVER:
                    if event.key == pygame.K_r:
                        reset_level()
                        globals()["state"] = BATTLE
                        start_battle_music()
                    elif event.key == pygame.K_m:
                        stop_battle_music()
                        globals()["state"] = MENU

        if state == BATTLE:
            update_battle()
            if enemy_hp <= 0 and state == BATTLE:
                stop_battle_music()
                globals()["state"] = LEVEL_CLEAR
                save_game()
            elif hero_hp <= 0 and state == BATTLE:
                stop_battle_music()
                globals()["state"] = GAME_OVER

        update_effects()

        if state == MENU:
            draw_menu()
            draw_text("C → CONTINUE SAVED CAMPAIGN", SMALL, (WIDTH // 2, 600), GOLD, True)
        elif state == LEVEL_INTRO:
            draw_intro()
        elif state == BATTLE:
            draw_battle()
        elif state == LEVEL_CLEAR:
            draw_clear_ultimate()
        elif state == UPGRADE_STATE:
            draw_upgrades()
        elif state == GAME_OVER:
            draw_game_over()

        draw_effects()
        pygame.display.flip()

        await asyncio.sleep(0)

        clock.tick(FPS)

    stop_battle_music()

asyncio.run(main())
