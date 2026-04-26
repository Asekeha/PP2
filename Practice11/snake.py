import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11: Snake")
clock = pygame.time.Clock()

WHITE, BLACK, GREEN, RED, GOLD = (255,255,255), (0,0,0), (0,255,0), (255,0,0), (255,215,0)

class Food:
    def __init__(self):
        self.respawn()

    def respawn(self):
        self.pos = (random.randrange(0, WIDTH, CELL), random.randrange(0, HEIGHT, CELL))
        # Разный вес еды
        self.weight = random.choices([1, 3], weights=[70, 30])[0] 
        self.color = RED if self.weight == 1 else GOLD
        # Фиксация времени появления (таймер для исчезновения)
        self.spawn_time = pygame.time.get_ticks() 

    def update(self):
        # Еда (если она золотая) исчезает через 5000 мс (5 секунд)
        if self.weight == 3 and pygame.time.get_ticks() - self.spawn_time > 5000:
            self.respawn()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.pos[0], self.pos[1], CELL, CELL))

snake = [(300, 300)]
dx, dy = CELL, 0
food = Food()
score = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and dy == 0: dx, dy = 0, -CELL
            if event.key == pygame.K_DOWN and dy == 0: dx, dy = 0, CELL
            if event.key == pygame.K_LEFT and dx == 0: dx, dy = -CELL, 0
            if event.key == pygame.K_RIGHT and dx == 0: dx, dy = CELL, 0

    food.update() # Проверяем таймер еды

    # Движение змеи
    head = (snake[0][0] + dx, snake[0][1] + dy)
    snake.insert(0, head)

    # Поедание пищи
    if head == food.pos:
        score += food.weight # Добавляем очки в зависимости от веса
        food.respawn()
    else:
        snake.pop() # Удаляем хвост, если не поели

    # Проверка столкновений
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in snake[1:]:
        pygame.quit(); sys.exit()

    screen.fill(BLACK)
    food.draw(screen)
    for part in snake:
        pygame.draw.rect(screen, GREEN, (part[0], part[1], CELL, CELL))
        
    font = pygame.font.SysFont("Arial", 20)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

    pygame.display.update()
    clock.tick(10)