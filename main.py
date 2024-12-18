import pygame
import sys
import random

pygame.init()

screen_width = 800
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption("OpenGalaga")

player_image = pygame.image.load("ship.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (player_image.get_width() // 4, player_image.get_height() // 4))
player_rect = player_image.get_rect()
player_rect.midbottom = (screen_width // 2, screen_height)

projectile_image = pygame.image.load("projectile.png").convert_alpha()
projectile_image = pygame.transform.scale(projectile_image, (projectile_image.get_width() // 8, projectile_image.get_height() // 8))

shooting_sound = pygame.mixer.Sound("shoot.mp3")
intro_sound = pygame.mixer.Sound("intro.mp3")
intro_sound.play()

pygame.font.init()
font = pygame.font.Font("pixel.ttf", 24)

player_speed = 0.3
player_accumulated_movement = 0.0

num_stars = 100
stars = []
for _ in range(num_stars):
    x = random.randint(0, screen_width - 1)
    y = random.randint(0, screen_height - 1)
    color = (255, 255, 255)
    stars.append([x, y, color])

star_speed = 1 / 6

projectiles = []
projectile_speed = 4 / 3
shoot_cooldown = 200
last_shot_time = 0

enemy_image = pygame.image.load("enemy1.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (enemy_image.get_width() // 8, enemy_image.get_height() // 8))

class EnemyRow:
    def __init__(self, y, direction):
        self.enemies = []
        self.y = y
        self.direction = direction
        self.speed = 0.3

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def update(self):
        shift = self.speed * self.direction
        for enemy in self.enemies:
            enemy.rect.x += shift
        if any(enemy.rect.left <= 0 or enemy.rect.right >= screen_width for enemy in self.enemies):
            self.direction *= -1
            for enemy in self.enemies:
                enemy.rect.y += 20

    def draw(self, surface):
        for enemy in self.enemies:
            surface.blit(enemy.image, enemy.rect)

enemy_rows = []
rows = 4
cols = 7
for row in range(rows):
    direction = 1 if row % 2 == 0 else -1
    enemy_row = EnemyRow(50 + row * 100, direction)
    for col in range(cols):
        enemy = pygame.sprite.Sprite()
        enemy.image = enemy_image
        enemy.rect = enemy_image.get_rect(midtop=(screen_width - 100 - col * 100, 50 + row * 100))
        enemy_row.add_enemy(enemy)
    enemy_rows.append(enemy_row)

explosion_sound = pygame.mixer.Sound("galaga_destroyed.wav")
explosion_duration = 300
explosion_start_time = None
explosion_rect = None

def draw_explosion(surface, center, current_time, start_time, duration):
    elapsed_time = current_time - start_time
    if elapsed_time < duration:
        radius = int(30 * (elapsed_time / duration))
        pygame.draw.circle(surface, (255, 0, 0), center, radius)
        pygame.draw.circle(surface, (255, 165, 0), center, radius - 10)
        pygame.draw.circle(surface, (255, 255, 0), center, radius - 20)

running = True
intro_playing = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not pygame.mixer.get_busy():
        intro_playing = False

    keys = pygame.key.get_pressed()
    if not intro_playing:
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_accumulated_movement -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < screen_width:
            player_accumulated_movement += player_speed
        if keys[pygame.K_z] and current_time - last_shot_time > shoot_cooldown:
            projectile_rect = projectile_image.get_rect(center=(player_rect.centerx, player_rect.top))
            projectiles.append(projectile_rect)
            shooting_sound.play()
            last_shot_time = current_time

    if abs(player_accumulated_movement) >= 1.0:
        player_rect.x += int(player_accumulated_movement)
        player_accumulated_movement -= int(player_accumulated_movement)

    for star in stars:
        star[1] += star_speed
        if star[1] >= screen_height:
            star[1] = 0
            star[0] = random.randint(0, screen_width - 1)
        star[2] = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    for projectile in projectiles[:]:
        projectile.y -= projectile_speed
        if projectile.bottom < 0:
            projectiles.remove(projectile)
        else:
            for enemy_row in enemy_rows:
                for enemy in enemy_row.enemies:
                    if projectile.colliderect(enemy.rect):
                        projectiles.remove(projectile)
                        explosion_sound.play()
                        explosion_start_time = current_time
                        explosion_rect = enemy.rect
                        enemy_row.enemies.remove(enemy)
                        break

    for enemy_row in enemy_rows:
        enemy_row.update()

    screen.fill((0, 0, 0))

    for star in stars:
        pygame.draw.rect(screen, star[2], (star[0], star[1], 6, 6))

    screen.blit(player_image, player_rect)

    for projectile in projectiles:
        screen.blit(projectile_image, projectile)

    for enemy_row in enemy_rows:
        enemy_row.draw(screen)

    if explosion_start_time and current_time - explosion_start_time < explosion_duration:
        draw_explosion(screen, explosion_rect.center, current_time, explosion_start_time, explosion_duration)
    else:
        explosion_start_time = None
        explosion_rect = None

    if intro_playing:
        player1_text = font.render("PLAYER 1", True, (255, 255, 255))
        start_text = font.render("START", True, (255, 255, 255))
        screen.blit(player1_text, (screen_width // 2 - player1_text.get_width() // 2, screen_height // 2 - 50))
        screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, screen_height // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()
