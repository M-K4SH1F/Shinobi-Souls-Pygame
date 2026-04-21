"""
Shinobi Souls - A Survival Game

@author Mohammed Kashif Ahmed 3744797
CS2613 Exploration Activity Sample Program

Controls:
  Arrow Keys / WASD - Move
  SPACE             - Attack
  ESC               - Quit
"""

import pygame
import random
import sys
import math

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shinobi Souls")
clock = pygame.time.Clock()

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (220,  50,  50)
DARK_RED   = (140,  20,  20)
BLUE       = ( 70, 130, 220)
DARK_BLUE  = ( 30,  60, 120)
PURPLE     = (140,  60, 200)
GOLD       = (255, 200,  50)
ORANGE     = (255, 140,  20)
GRAY       = (120, 120, 120)
DARK_GRAY  = ( 40,  40,  50)
BG_SKY     = ( 15,  15,  30)
BG_GROUND  = ( 25,  20,  40)
ACCENT     = (180, 100, 255)
HP_GREEN   = ( 80, 200, 80)
HP_RED     = (200,  50, 50)

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_large  = pygame.font.SysFont("consolas", 52, bold=True)
font_medium = pygame.font.SysFont("consolas", 30, bold=True)
font_small  = pygame.font.SysFont("consolas", 20)
font_tiny   = pygame.font.SysFont("consolas", 15)

# ── Helper: draw text with drop shadow ────────────────────────────────────────
def draw_text(surf, text, font, colour, x, y, shadow=True, center=False):
    rendered = font.render(text, True, colour)
    if shadow:
        shadow_surf = font.render(text, True, BLACK)
        shadow_rect = shadow_surf.get_rect()
        if center:
            shadow_rect.center = (x + 2, y + 2)
        else:
            shadow_rect.topleft = (x + 2, y + 2)
        surf.blit(shadow_surf, shadow_rect)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surf.blit(rendered, rect)

# ── Particle system ───────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, colour, vx=None, vy=None):
        self.x  = x
        self.y  = y
        self.colour = colour
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-4, -1)
        self.life     = random.randint(20, 45)
        self.max_life = self.life
        self.radius   = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15          
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        r = max(1, int(self.radius * (self.life / self.max_life)))
        colour = (*self.colour, alpha)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, colour, (r, r), r)
        surf.blit(s, (int(self.x) - r, int(self.y) - r))

# ── Projectile (kunai ) ─────────────────────────────────────────────
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner="player"):
        super().__init__()
        self.owner     = owner
        self.direction = direction
        self.speed     = 14 if owner == "player" else 6
        self.damage    = 20 if owner == "player" else 12
        w, h = (18, 8) if owner == "player" else (14, 14)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        if owner == "player":
            points = [(0, 4), (14, 2), (18, 4), (14, 6)]
            pygame.draw.polygon(self.image, GOLD,   points)
            pygame.draw.polygon(self.image, ORANGE, points, 1)
        else:
            # enemy orb
            pygame.draw.circle(self.image, PURPLE, (7, 7), 7)
            pygame.draw.circle(self.image, WHITE,  (7, 7), 7, 1)
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# ── Player ────────────────────────────────────────────────────────────────────
GROUND_Y = HEIGHT - 100   

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.w, self.h = 40, 60
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self._draw_sprite()
        self.rect        = self.image.get_rect()
        self.rect.midbottom = (WIDTH // 4, GROUND_Y)
        self.vel_y       = 0
        self.on_ground   = False
        self.hp          = 100
        self.max_hp      = 100
        self.score       = 0
        self.facing      = 1          # 1=right, -1=left
        self.attack_cd   = 0
        self.shoot_cd    = 0
        self.hurt_timer  = 0
        self.kill_count  = 0
        self.invincible  = 0          

    def _draw_sprite(self, colour=BLUE):
        self.image.fill((0, 0, 0, 0))
        # body
        pygame.draw.rect(self.image, colour, (10, 20, 20, 30), border_radius=4)
        # head
        pygame.draw.circle(self.image, (220, 175, 130), (20, 14), 12)
        # headband
        pygame.draw.rect(self.image, RED, (8, 8, 24, 6), border_radius=2)
        # eyes
        pygame.draw.circle(self.image, BLACK, (15, 13), 3)
        pygame.draw.circle(self.image, BLACK, (25, 13), 3)
        pygame.draw.circle(self.image, WHITE, (14, 12), 1)
        pygame.draw.circle(self.image, WHITE, (24, 12), 1)
        # arms
        pygame.draw.rect(self.image, colour, (0,  22, 10, 6), border_radius=2)
        pygame.draw.rect(self.image, colour, (30, 22, 10, 6), border_radius=2)
        # legs
        pygame.draw.rect(self.image, DARK_BLUE, (10, 48, 8, 12), border_radius=2)
        pygame.draw.rect(self.image, DARK_BLUE, (22, 48, 8, 12), border_radius=2)

    def handle_input(self, keys, projectiles, particles):
        # ── horizontal movement ──
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.rect.x -= 5
            self.facing  = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += 5
            self.facing  = 1
        self.rect.left  = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)

        # ── jump ──
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y    = -18
            self.on_ground = False

        # ── shoot ──
        if keys[pygame.K_SPACE] and self.shoot_cd <= 0:
            p = Projectile(self.rect.centerx, self.rect.centery, self.facing, "player")
            projectiles.add(p)
            self.shoot_cd = 20
            for _ in range(6):
                particles.append(Particle(self.rect.centerx, self.rect.centery, GOLD))

    def update(self):
        # gravity
        self.vel_y += 0.8
        self.rect.y += int(self.vel_y)
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y       = 0
            self.on_ground   = True

        if self.shoot_cd   > 0: self.shoot_cd   -= 1
        if self.hurt_timer > 0: self.hurt_timer  -= 1
        if self.invincible > 0: self.invincible   -= 1

        # flash when hurt
        if self.hurt_timer > 0:
            self._draw_sprite(RED if self.hurt_timer % 6 < 3 else BLUE)
        else:
            self._draw_sprite()

    def take_damage(self, amount):
        if self.invincible > 0:
            return
        self.hp        -= amount
        self.hurt_timer = 20
        self.invincible = 40

    def draw_hud(self, surf):
        # HP bar
        bar_w = 220
        pygame.draw.rect(surf, DARK_GRAY, (20, 18, bar_w, 22), border_radius=5)
        ratio = max(0, self.hp / self.max_hp)
        col   = HP_GREEN if ratio > 0.5 else ORANGE if ratio > 0.25 else HP_RED
        pygame.draw.rect(surf, col, (20, 18, int(bar_w * ratio), 22), border_radius=5)
        pygame.draw.rect(surf, WHITE, (20, 18, bar_w, 22), 2, border_radius=5)
        draw_text(surf, f"HP  {self.hp}/{self.max_hp}", font_tiny, WHITE, 28, 22, shadow=False)

        # score / kills
        draw_text(surf, f"SCORE  {self.score}", font_small, GOLD, WIDTH - 220, 18)
        draw_text(surf, f"KILLS  {self.kill_count}", font_small, ACCENT, WIDTH - 220, 42)

# ── Enemy ─────────────────────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    TYPES = ["demon", "mage", "samurai"]

    def __init__(self, wave=1):
        super().__init__()
        self.etype     = random.choice(self.TYPES)
        self.hp        = random.randint(30, 50) + wave * 10
        self.max_hp    = self.hp
        self.speed     = random.uniform(1.5, 2.5) + wave * 0.2
        self.w, self.h = 38, 58
        self.image     = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self._draw_sprite()
        side           = random.choice([-1, 1])
        start_x        = -60 if side == 1 else WIDTH + 60
        self.rect      = self.image.get_rect(midbottom=(start_x, GROUND_Y))
        self.direction = side
        self.vel_y     = 0
        self.on_ground = False
        self.shoot_cd  = random.randint(60, 180)
        self.hurt_timer = 0

    def _colour(self):
        return {
            "demon":   (180, 40, 40),
            "mage":    (100, 40, 180),
            "samurai": (40, 80, 160),
        }[self.etype]

    def _draw_sprite(self, override=None):
        self.image.fill((0, 0, 0, 0))
        c = override if override else self._colour()
        # body
        pygame.draw.rect(self.image, c, (9, 20, 20, 28), border_radius=4)
        # head
        pygame.draw.circle(self.image, (180, 130, 100), (19, 13), 11)
        # details per type
        if self.etype == "demon":
            # horns
            pygame.draw.polygon(self.image, DARK_RED, [(10, 5), (13, 0), (16, 5)])
            pygame.draw.polygon(self.image, DARK_RED, [(22, 5), (25, 0), (28, 5)])
            pygame.draw.circle(self.image, RED, (14, 13), 3)
            pygame.draw.circle(self.image, RED, (24, 13), 3)
        elif self.etype == "mage":
            # pointy hat
            pygame.draw.polygon(self.image, PURPLE, [(19, -5), (8, 8), (30, 8)])
            pygame.draw.circle(self.image, ACCENT, (14, 13), 3)
            pygame.draw.circle(self.image, ACCENT, (24, 13), 3)
        else:
            # samurai headband
            pygame.draw.rect(self.image, DARK_GRAY, (8, 7, 22, 5), border_radius=2)
            pygame.draw.circle(self.image, DARK_GRAY, (14, 12), 3)
            pygame.draw.circle(self.image, DARK_GRAY, (24, 12), 3)
        # arms
        pygame.draw.rect(self.image, c, (0,  22, 9, 5), border_radius=2)
        pygame.draw.rect(self.image, c, (29, 22, 9, 5), border_radius=2)
        # legs
        dc = tuple(max(0, v - 40) for v in c)
        pygame.draw.rect(self.image, dc, (9,  46, 8, 12), border_radius=2)
        pygame.draw.rect(self.image, dc, (21, 46, 8, 12), border_radius=2)

    def update(self, player, projectiles):
        # move toward player
        if player.rect.centerx > self.rect.centerx:
            self.rect.x   += self.speed
            self.direction = 1
        else:
            self.rect.x   -= self.speed
            self.direction = -1

        self.rect.left  = max(-10, self.rect.left)
        self.rect.right = min(WIDTH + 10, self.rect.right)

        self.vel_y += 0.8
        self.rect.y += int(self.vel_y)
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y       = 0
            self.on_ground   = True

        # shoot (mage only)
        if self.etype == "mage":
            self.shoot_cd -= 1
            if self.shoot_cd <= 0:
                p = Projectile(self.rect.centerx, self.rect.centery, self.direction, "enemy")
                projectiles.add(p)
                self.shoot_cd = random.randint(90, 200)

        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self._draw_sprite(WHITE if self.hurt_timer % 4 < 2 else None)
        else:
            self._draw_sprite()

    def take_damage(self, amount):
        self.hp -= amount
        self.hurt_timer = 12
        return self.hp <= 0

    def draw_hp_bar(self, surf):
        bw = self.w
        pygame.draw.rect(surf, DARK_GRAY, (self.rect.x, self.rect.top - 10, bw, 6))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, HP_GREEN if ratio > 0.5 else HP_RED,
                         (self.rect.x, self.rect.top - 10, int(bw * ratio), 6))
        pygame.draw.rect(surf, WHITE, (self.rect.x, self.rect.top - 10, bw, 6), 1)

# ── Background rendering ───────────────────────────────────────────────────────
def draw_background(surf, scroll_offset):
    # sky
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(15  + (40  - 15)  * t)
        g = int(15  + (20  - 15)  * t)
        b = int(30  + (50  - 30)  * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # moon
    pygame.draw.circle(surf, (220, 220, 180), (WIDTH - 120, 70), 45)
    pygame.draw.circle(surf, (200, 195, 160), (WIDTH - 105, 58), 40)

    # stars
    random.seed(42)
    for _ in range(80):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT // 2)
        r  = random.randint(1, 2)
        pygame.draw.circle(surf, WHITE, (sx, sy), r)
    random.seed()

    # distant mountains 
    ox = int(scroll_offset * 0.2) % WIDTH
    pts = []
    random.seed(99)
    for i in range(12):
        pts.append(((i * WIDTH // 10 - ox) % (WIDTH + 100) - 50,
                    HEIGHT - 150 - random.randint(60, 180)))
    random.seed()
    for i in range(len(pts) - 1):
        pygame.draw.polygon(surf, (35, 30, 60),
                            [pts[i],
                             pts[i + 1],
                             (pts[i + 1][0], HEIGHT - 100),
                             (pts[i][0],     HEIGHT - 100)])

    # ground
    pygame.draw.rect(surf, (30, 25, 50),   (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(surf, (50, 40, 80),   (0, GROUND_Y, WIDTH, 6))
    pygame.draw.rect(surf, (70, 55, 100),  (0, GROUND_Y, WIDTH, 2))

    # lanterns
    for lx in range(80, WIDTH, 200):
        lx2 = (lx - int(scroll_offset * 0.4)) % (WIDTH + 100)
        pygame.draw.line(surf, GRAY, (lx2, GROUND_Y - 120), (lx2, GROUND_Y - 80), 2)
        pygame.draw.rect(surf, GOLD, (lx2 - 12, GROUND_Y - 120, 24, 40),
                         border_radius=4)
        s = pygame.Surface((24, 40), pygame.SRCALPHA)
        pygame.draw.rect(s, (*GOLD, 60), (0, 0, 24, 40), border_radius=4)
        surf.blit(s, (lx2 - 12, GROUND_Y - 120))

# ── Wave announcer ─────────────────────────────────────────────────────────────
wave_announce_timer = 0
wave_announce_text  = ""

def announce_wave(wave_num):
    global wave_announce_timer, wave_announce_text
    wave_announce_timer = 120
    wave_announce_text  = f"WAVE  {wave_num}"

# ── Main menu ─────────────────────────────────────────────────────────────────
def main_menu():
    angle = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.fill(BG_SKY)
        draw_background(screen, angle)

        glow_r = int(160 + 20 * math.sin(angle * 0.05))
        glow_s = pygame.Surface((500, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_s, (*ACCENT, 40), (0, 0, 500, 100))
        screen.blit(glow_s, (WIDTH // 2 - 250, HEIGHT // 2 - 140))

        draw_text(screen, "SHINOBI  SOULS", font_large, GOLD,    WIDTH // 2, HEIGHT // 2 - 100, center=True)
        draw_text(screen, "A Survival Game",  font_small, ACCENT,  WIDTH // 2, HEIGHT // 2 - 50,  center=True)
        draw_text(screen, "PRESS  ENTER  TO  START", font_medium, WHITE,  WIDTH // 2, HEIGHT // 2 + 10,  center=True)
        draw_text(screen, "ESC = QUIT",              font_small,  GRAY,   WIDTH // 2, HEIGHT // 2 + 60,  center=True)

        draw_text(screen, "WASD / ARROWS = Move & Jump", font_tiny, WHITE, WIDTH // 2, HEIGHT - 80, center=True)
        draw_text(screen, "SPACE = Throw Kunai",         font_tiny, WHITE, WIDTH // 2, HEIGHT - 60, center=True)
        draw_text(screen, "Survive as many waves as you can!", font_tiny, GOLD, WIDTH // 2, HEIGHT - 40, center=True)

        angle += 1
        pygame.display.flip()
        clock.tick(FPS)

# ── Game over screen ──────────────────────────────────────────────────────────
def game_over_screen(score, kills, wave):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        screen.fill(BG_SKY)
        draw_background(screen, 0)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "YOU  DIED",         font_large,  RED,   WIDTH // 2, HEIGHT // 2 - 130, center=True)
        draw_text(screen, f"Score : {score}",  font_medium, GOLD,  WIDTH // 2, HEIGHT // 2 - 55,  center=True)
        draw_text(screen, f"Kills : {kills}",  font_medium, WHITE, WIDTH // 2, HEIGHT // 2 - 10,  center=True)
        draw_text(screen, f"Wave  : {wave}",   font_medium, ACCENT,WIDTH // 2, HEIGHT // 2 + 35,  center=True)
        draw_text(screen, "ENTER = Play Again",  font_small, WHITE, WIDTH // 2, HEIGHT // 2 + 100, center=True)
        draw_text(screen, "ESC   = Quit",        font_small, GRAY,  WIDTH // 2, HEIGHT // 2 + 130, center=True)

        pygame.display.flip()
        clock.tick(FPS)

# ── Main game loop ────────────────────────────────────────────────────────────
def game():
    global wave_announce_timer, wave_announce_text

    player      = Player()
    player_grp  = pygame.sprite.GroupSingle(player)
    enemies     = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    particles   = []

    wave            = 1
    enemies_per_wave = 5
    enemies_spawned  = 0
    spawn_timer      = 0
    spawn_interval   = 90
    scroll_offset    = 0

    announce_wave(wave)

    running = True
    while running:
        dt = clock.tick(FPS)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        # ── Input ──
        keys = pygame.key.get_pressed()
        player.handle_input(keys, projectiles, particles)
        player.update()

        # ── Spawning ──
        if enemies_spawned < enemies_per_wave:
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                enemies.add(Enemy(wave))
                enemies_spawned += 1
                spawn_timer = 0

        # ── Update enemies ──
        for e in list(enemies):
            e.update(player, projectiles)
            # melee damage
            if e.rect.colliderect(player.rect) and player.invincible <= 0:
                player.take_damage(8)
                particles += [Particle(player.rect.centerx, player.rect.top,
                                       RED) for _ in range(8)]

        # ── Update projectiles ──
        projectiles.update()

        # ── Collision: player projectiles ──
        for proj in list(projectiles):
            if proj.owner == "player":
                hit = pygame.sprite.spritecollideany(proj, enemies)
                if hit:
                    proj.kill()
                    killed = hit.take_damage(proj.damage)
                    particles += [Particle(hit.rect.centerx, hit.rect.centery,
                                           GOLD) for _ in range(10)]
                    if killed:
                        player.score     += 100 * wave
                        player.kill_count += 1
                        particles += [Particle(hit.rect.centerx, hit.rect.centery,
                                               ORANGE) for _ in range(20)]
                        hit.kill()

        # ── Collision: enemy projectiles ──
        for proj in list(projectiles):
            if proj.owner == "enemy" and proj.rect.colliderect(player.rect):
                proj.kill()
                player.take_damage(proj.damage)
                particles += [Particle(player.rect.centerx, player.rect.centery,
                                       PURPLE) for _ in range(8)]

        # ── Particles ──
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ── Next wave ──
        if enemies_spawned >= enemies_per_wave and len(enemies) == 0:
            wave            += 1
            enemies_per_wave = 5 + wave * 2
            enemies_spawned  = 0
            spawn_interval   = max(30, 90 - wave * 5)
            announce_wave(wave)
            player.score    += 500 * wave 

        # ── Scroll ──
        scroll_offset += 1

        # ── Draw ──
        draw_background(screen, scroll_offset)

        for p in particles:
            p.draw(screen)

        enemies.draw(screen)
        for e in enemies:
            e.draw_hp_bar(screen)

        player_grp.draw(screen)
        projectiles.draw(screen)

        # HUD
        player.draw_hud(screen)

        # wave announce
        if wave_announce_timer > 0:
            alpha = min(255, wave_announce_timer * 4)
            s     = font_large.render(wave_announce_text, True, GOLD)
            s.set_alpha(alpha)
            r     = s.get_rect(center=(WIDTH // 2, 100))
            screen.blit(s, r)
            wave_announce_timer -= 1

        # wave label (top centre, always)
        draw_text(screen, f"WAVE  {wave}", font_small, WHITE, WIDTH // 2, 60, center=True)

        pygame.display.flip()

        # ── Death check ──
        if player.hp <= 0:
            replay = game_over_screen(player.score, player.kill_count, wave)
            if replay:
                game()
            return

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main_menu()
    game()
    pygame.quit()
    sys.exit()
