import pygame
import sys
import datetime
from collections import deque

pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2: Advanced Paint")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 18)
text_font = pygame.font.SysFont("Arial", 24) # Шрифт для инструмента "Текст"

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 220)
YELLOW = (255, 215, 0)
PURPLE = (128, 0, 128)
GRAY = (200, 200, 200)

colors = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE]
color_rects = []
for i, c in enumerate(colors):
    rect = pygame.Rect(10 + i * 50, 10, 40, 40)
    color_rects.append((rect, c))

# Холст для рисования (чтобы предпросмотр не портил основной рисунок)
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# Состояние приложения
tool = "brush"      # brush, line, rect, circle, eraser, fill, text
color = BLACK
brush_size = 5      # 2 (small), 5 (medium), 10 (large)
drawing = False
start_pos = None
last_pos = None

# Состояние для текста
typing = False
text_input = ""
text_pos = None

def flood_fill(surface, pos, fill_color):
    """Алгоритм заливки области (Flood-Fill)"""
    target_color = surface.get_at(pos)
    if target_color == fill_color:
        return
    
    # Используем очередь для обхода пикселей (BFS)
    q = deque([pos])
    surface.set_at(pos, fill_color)
    
    while q:
        x, y = q.popleft()
        # Проверяем соседние пиксели (верх, низ, лево, право)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 60 <= ny < HEIGHT: # Учитываем панель инструментов (60px)
                if surface.get_at((nx, ny)) == target_color:
                    surface.set_at((nx, ny), fill_color)
                    q.append((nx, ny))

def draw_ui():
    """Отрисовка верхней панели с кнопками и подсказками"""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 60))
    for rect, c in color_rects:
        pygame.draw.rect(screen, c, rect)
        if color == c:
            pygame.draw.rect(screen, BLACK, rect, 3) # Выделяем активный цвет
            
    instructions = f"Tool: {tool} | Size: {brush_size} | Tools: B(rush), L(ine), R(ect), C(ircle), E(raser), F(ill), T(ext)"
    text_surf = font.render(instructions, True, BLACK)
    screen.blit(text_surf, (320, 10))
    
    saves_instr = "Sizes: 1, 2, 3 | Save: Ctrl+S"
    saves_surf = font.render(saves_instr, True, BLACK)
    screen.blit(saves_surf, (320, 35))

# ГЛАВНЫЙ ЦИКЛ
while True:
    screen.blit(canvas, (0, 0)) # Кадрируем холст на экран
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # ОБРАБОТКА ИНСТРУМЕНТА "ТЕКСТ"
        if typing:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Подтверждаем текст (рисуем на холст)
                    rendered_text = text_font.render(text_input, True, color)
                    canvas.blit(rendered_text, text_pos)
                    typing = False
                    text_input = ""
                elif event.key == pygame.K_ESCAPE:
                    # Отменяем ввод
                    typing = False
                    text_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode
            continue

        # НАЖАТИЕ КНОПОК КЛАВИАТУРЫ
        if event.type == pygame.KEYDOWN:
            # Выбор инструмента
            if event.key == pygame.K_b: tool = "brush"
            elif event.key == pygame.K_l: tool = "line"
            elif event.key == pygame.K_r: tool = "rect"
            elif event.key == pygame.K_c: tool = "circle"
            elif event.key == pygame.K_e: tool = "eraser"
            elif event.key == pygame.K_f: tool = "fill"
            elif event.key == pygame.K_t: tool = "text"
            
            # Выбор размера кисти
            elif event.key == pygame.K_1: brush_size = 2
            elif event.key == pygame.K_2: brush_size = 5
            elif event.key == pygame.K_3: brush_size = 10
            
            # Сохранение Ctrl+S
            elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"canvas_{timestamp}.png"
                pygame.image.save(canvas, filename)
                print(f"Saved as {filename}")

        # НАЖАТИЕ МЫШИ
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Левая кнопка
                mx, my = event.pos
                clicked_ui = False
                
                # Проверка клика по палитре
                for rect, c in color_rects:
                    if rect.collidepoint(mx, my):
                        color = c
                        clicked_ui = True
                        break
                
                # Если кликнули по холсту
                if not clicked_ui and my > 60:
                    if tool == "fill":
                        flood_fill(canvas, event.pos, color)
                    elif tool == "text":
                        typing = True
                        text_pos = event.pos
                        text_input = ""
                    else:
                        drawing = True
                        start_pos = event.pos
                        last_pos = event.pos

        # ДВИЖЕНИЕ МЫШИ
        if event.type == pygame.MOUSEMOTION and drawing:
            if tool == "brush":
                pygame.draw.line(canvas, color, last_pos, event.pos, brush_size * 2)
                last_pos = event.pos
            elif tool == "eraser":
                pygame.draw.line(canvas, WHITE, last_pos, event.pos, brush_size * 4) # Ластик чуть больше
                last_pos = event.pos

        # ОТПУСКАНИЕ МЫШИ
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                end_pos = event.pos
                
                # Рисуем фигуры на постоянном холсте
                if tool == "line":
                    pygame.draw.line(canvas, color, start_pos, end_pos, brush_size)
                elif tool == "rect":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                    pygame.draw.rect(canvas, color, rect, brush_size)
                elif tool == "circle":
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    radius = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
                    pygame.draw.circle(canvas, color, start_pos, radius, brush_size)

    # ОТРИСОВКА ПРЕДПРОСМОТРА (временные фигуры поверх основного холста)
    if drawing:
        current_pos = pygame.mouse.get_pos()
        if tool == "line":
            pygame.draw.line(screen, color, start_pos, current_pos, brush_size)
        elif tool == "rect":
            x1, y1 = start_pos
            x2, y2 = current_pos
            rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(screen, color, rect, brush_size)
        elif tool == "circle":
            x1, y1 = start_pos
            x2, y2 = current_pos
            radius = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
            pygame.draw.circle(screen, color, start_pos, radius, brush_size)

    # ОТРИСОВКА НАБИРАЕМОГО ТЕКСТА (в реальном времени)
    if typing and text_pos:
        rendered_text = text_font.render(text_input + "|", True, color)
        screen.blit(rendered_text, text_pos)

    draw_ui()
    pygame.display.flip()
    clock.tick(60)