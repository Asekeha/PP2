import pygame
import random
import db

# Константы
WIDTH, HEIGHT = 600, 600
CELL = 20
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

def draw_text(surface, text, size, color, center_pos):
    font = pygame.font.SysFont("Verdana", size)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, rect)

def run_game(screen, username, settings):
    clock = pygame.time.Clock()
    
    # Личный рекорд
    personal_best = db.get_personal_best(username)

    # Настройки змейки
    snake_color = tuple(settings.get("snake_color", [0, 255, 0]))
    draw_grid = settings.get("grid", True)

    # Состояние игры
    snake = [(COLS//2, ROWS//2)]
    direction = (1, 0)
    next_direction = (1, 0)
    
    score = 0
    level = 1
    foods_eaten = 0
    base_speed = 8
    
    # Препятствия (появляются с 3 уровня)
    obstacles = set()

    # Еда
    food = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
    poison = None
    
    # Бонусы (Усиления)
    powerup = None
    powerup_type = None # "speed", "slow", "shield"
    powerup_spawn_time = 0
    
    # Активные эффекты
    speed_modifier = 0
    effect_end_time = 0
    shield_active = False

    def generate_pos():
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in snake and pos not in obstacles and pos != food and pos != poison:
                return pos

    def level_up():
        nonlocal level, base_speed
        level += 1
        base_speed += 1
        # Добавляем препятствия, начиная с 3 уровня
        if level >= 3:
            for _ in range(5): # По 5 новых блоков за уровень
                obstacles.add(generate_pos())

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, level
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1): next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1): next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0): next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0): next_direction = (1, 0)

        direction = next_direction
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Снятие временных эффектов
        if current_time > effect_end_time:
            speed_modifier = 0

        # Удаление бонуса, если его не подобрали за 8 секунд
        if powerup and current_time - powerup_spawn_time > 8000:
            powerup = None

        # Шанс появления яда или бонуса при каждом шаге (очень маленький, чтобы не спамило)
        if not poison and random.random() < 0.02:
            poison = generate_pos()
        if not powerup and random.random() < 0.01:
            powerup = generate_pos()
            powerup_type = random.choice(["speed", "slow", "shield"])
            powerup_spawn_time = current_time

        # Проверка коллизий со стенами или собой
        hit_wall = head[0] < 0 or head[0] >= COLS or head[1] < 0 or head[1] >= ROWS
        hit_self = head in snake
        hit_obstacle = head in obstacles

        if hit_wall or hit_self or hit_obstacle:
            if shield_active:
                shield_active = False # Щит спасает 1 раз
                # Отскакиваем (просто не двигаемся в этот кадр, игрок должен успеть повернуть)
                direction = (0, 0) 
                next_direction = (0, 0)
                head = snake[0]
            else:
                return score, level # Game Over

        if head != snake[0]: # Если мы сдвинулись
            snake.insert(0, head)
            
            # Поедание еды
            if head == food:
                score += 10
                foods_eaten += 1
                if foods_eaten % 5 == 0:
                    level_up()
                food = generate_pos()
            # Поедание яда
            elif head == poison:
                score = max(0, score - 5)
                snake.pop() # Обычный поп
                if len(snake) > 0: snake.pop() # И еще один (минус 2 длины)
                poison = None
                if len(snake) <= 1:
                    return score, level # Game Over от яда
            # Поедание бонуса
            elif head == powerup:
                if powerup_type == "speed":
                    speed_modifier = 5
                    effect_end_time = current_time + 5000
                elif powerup_type == "slow":
                    speed_modifier = -3
                    effect_end_time = current_time + 5000
                elif powerup_type == "shield":
                    shield_active = True
                powerup = None
            else:
                snake.pop() # Просто движение

        # Отрисовка
        screen.fill(BLACK)
        
        # Сетка
        if draw_grid:
            for x in range(0, WIDTH, CELL): pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Отрисовка еды, яда, бонусов, препятствий
        pygame.draw.rect(screen, YELLOW, (food[0]*CELL, food[1]*CELL, CELL, CELL))
        if poison:
            pygame.draw.rect(screen, DARK_RED, (poison[0]*CELL, poison[1]*CELL, CELL, CELL))
        if powerup:
            p_color = CYAN if powerup_type == "speed" else ORANGE if powerup_type == "slow" else BLUE
            pygame.draw.rect(screen, p_color, (powerup[0]*CELL, powerup[1]*CELL, CELL, CELL))
        for obs in obstacles:
            pygame.draw.rect(screen, GRAY, (obs[0]*CELL, obs[1]*CELL, CELL, CELL))

        # Отрисовка змеи
        for i, part in enumerate(snake):
            color = snake_color if i > 0 else WHITE # Голова белая
            pygame.draw.rect(screen, color, (part[0]*CELL, part[1]*CELL, CELL, CELL))
            if shield_active and i == 0:
                pygame.draw.rect(screen, BLUE, (part[0]*CELL, part[1]*CELL, CELL, CELL), 2) # Аура щита

        # UI
        draw_text(screen, f"Score: {score}  Level: {level}", 18, WHITE, (WIDTH//2, 15))
        draw_text(screen, f"Best: {personal_best}", 14, YELLOW, (WIDTH//2, 35))

        pygame.display.flip()
        
        current_speed = max(3, base_speed + speed_modifier)
        clock.tick(current_speed)

    return score, level