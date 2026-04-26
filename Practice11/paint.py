import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11: Paint")

WHITE, BLACK, BLUE = (255, 255, 255), (0, 0, 0), (0, 0, 255)
screen.fill(WHITE)

tool = "square" # Базовый инструмент
drawing = False
start_pos = (0, 0)

font = pygame.font.SysFont("Verdana", 16)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        # Выбор фигур
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: tool = "square"
            if event.key == pygame.K_2: tool = "right_triangle"
            if event.key == pygame.K_3: tool = "eq_triangle"
            if event.key == pygame.K_4: tool = "rhombus"

        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos
            
            # Вычисление ширины и высоты рамки выделения
            x = min(start_pos[0], end_pos[0])
            y = min(start_pos[1], end_pos[1])
            w = abs(end_pos[0] - start_pos[0])
            h = abs(end_pos[1] - start_pos[1])

            # 1. Нарисуйте квадрат (используем максимальную сторону для ровности)
            if tool == "square":
                side = max(w, h)
                pygame.draw.rect(screen, BLUE, (x, y, side, side), 3)

            # 2. Нарисуйте прямоугольный треугольник
            elif tool == "right_triangle":
                points = [(x, y), (x, y + h), (x + w, y + h)]
                pygame.draw.polygon(screen, BLUE, points, 3)

            # 3. Нарисуйте равносторонний треугольник (приблизительно вписанный в рамку)
            elif tool == "eq_triangle":
                points = [(x + w // 2, y), (x, y + h), (x + w, y + h)]
                pygame.draw.polygon(screen, BLUE, points, 3)

            # 4. Нарисуйте ромб
            elif tool == "rhombus":
                points = [(x + w // 2, y), (x + w, y + h // 2), (x + w // 2, y + h), (x, y + h // 2)]
                pygame.draw.polygon(screen, BLUE, points, 3)

    # Отрисовка UI
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 30))
    text = font.render(f"Tool: {tool} | Keys: 1-Square, 2-Right Tri, 3-Eq Tri, 4-Rhombus", True, BLACK)
    screen.blit(text, (10, 5))

    pygame.display.update()