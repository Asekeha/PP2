import pygame
import random
import sys

pygame.init()

# Настройки экрана и игры
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11: Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)

# Цвета
WHITE, BLACK, RED, BLUE, YELLOW, GOLD = (255,255,255), (0,0,0), (255,0,0), (0,0,255), (255,255,0), (255,215,0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 70))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), -50))
        self.speed = 5 # Базовая скорость врага

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(40, WIDTH-40), -50)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 70))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 100))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += 5

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Случайная генерация монет с разным весом (1 или 3 очка)
        self.weight = random.choices([1, 3], weights=[80, 20])[0] 
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        color = YELLOW if self.weight == 1 else GOLD
        pygame.draw.circle(self.image, color, (10, 10), 10)
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), -50))

    def update(self):
        self.rect.y += 4
        if self.rect.top > HEIGHT:
            self.kill()

player = Player()
enemy = Enemy()
coins = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(player, enemy)

# Событие спавна монет
SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 2000)

score = 0
speed_threshold = 10 # Порог очков для увеличения скорости врага

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == SPAWN_COIN:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)

    all_sprites.update()

    # Проверка сбора монет
    collected_coins = pygame.sprite.spritecollide(player, coins, True)
    for c in collected_coins:
        score += c.weight
        # Увеличение скорости врага при достижении порога N монет (очков)
        if score >= speed_threshold:
            enemy.speed += 1 
            speed_threshold += 10 # Следующий порог

    # Проверка столкновения с врагом
    if pygame.sprite.collide_rect(player, enemy):
        pygame.quit(); sys.exit()

    screen.fill(WHITE)
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    # Отображение счета
    score_text = font.render(f"Score: {score} | Enemy Speed: {enemy.speed}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)