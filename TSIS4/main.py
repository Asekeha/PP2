import pygame
import sys
import json
import os
import db
from game import run_game, WIDTH, HEIGHT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 4: Advanced Snake")

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"snake_color": [0, 255, 0], "grid": True, "sound": True}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def draw_text(surface, text, size, color, center_pos):
    font = pygame.font.SysFont("Verdana", size)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, rect)

class Button:
    def __init__(self, y, text):
        self.rect = pygame.Rect(WIDTH//2 - 100, y, 200, 40)
        self.text = text

    def draw(self, surface):
        color = (150, 150, 150) if self.rect.collidepoint(pygame.mouse.get_pos()) else (100, 100, 100)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        draw_text(surface, self.text, 18, (255, 255, 255), self.rect.center)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def get_username():
    name = ""
    clock = pygame.time.Clock()
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "ENTER USERNAME:", 24, (255, 255, 255), (WIDTH//2, HEIGHT//2 - 50))
        draw_text(screen, name + "_", 32, (255, 255, 0), (WIDTH//2, HEIGHT//2 + 10))
        draw_text(screen, "Press ENTER to start", 14, (200, 200, 200), (WIDTH//2, HEIGHT//2 + 80))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip(): return name.strip()
                elif event.key == pygame.K_BACKSPACE: name = name[:-1]
                elif len(name) < 15 and event.unicode.isprintable(): name += event.unicode
        pygame.display.flip()
        clock.tick(30)

def settings_screen(settings):
    colors = {"Green": [0, 255, 0], "Blue": [0, 0, 255], "Purple": [128, 0, 128]}
    color_names = list(colors.keys())
    current_color_idx = 0
    for i, c in enumerate(colors.values()):
        if c == settings["snake_color"]: current_color_idx = i

    btn_color = Button(200, f"Color: {color_names[current_color_idx]}")
    btn_grid = Button(260, f"Grid: {'ON' if settings['grid'] else 'OFF'}")
    btn_sound = Button(320, f"Sound: {'ON' if settings['sound'] else 'OFF'}")
    btn_back = Button(400, "Save & Back")

    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "SETTINGS", 36, (255, 255, 255), (WIDTH//2, 100))
        
        for btn in [btn_color, btn_grid, btn_sound, btn_back]: btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_color.is_clicked(event):
                current_color_idx = (current_color_idx + 1) % len(colors)
                settings["snake_color"] = colors[color_names[current_color_idx]]
                btn_color.text = f"Color: {color_names[current_color_idx]}"
            if btn_grid.is_clicked(event):
                settings["grid"] = not settings["grid"]
                btn_grid.text = f"Grid: {'ON' if settings['grid'] else 'OFF'}"
            if btn_sound.is_clicked(event):
                settings["sound"] = not settings["sound"]
                btn_sound.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
            if btn_back.is_clicked(event):
                save_settings(settings)
                return

        pygame.display.flip()

def leaderboard_screen():
    lb = db.get_leaderboard()
    btn_back = Button(500, "Back")

    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "TOP 10 PLAYERS", 36, (255, 255, 0), (WIDTH//2, 50))

        y = 120
        for i, row in enumerate(lb):
            # row: username, score, level, date
            text = f"{i+1}. {row[0]} | Score: {row[1]} | Lvl: {row[2]}"
            draw_text(screen, text, 18, (255, 255, 255), (WIDTH//2, y))
            y += 35

        btn_back.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_back.is_clicked(event):
                return

        pygame.display.flip()

def game_over_screen(username, score, level, settings):
    db.save_session(username, score, level) # Авто-сохранение
    pb = db.get_personal_best(username)

    btn_retry = Button(350, "Retry")
    btn_menu = Button(410, "Main Menu")

    while True:
        screen.fill((50, 0, 0))
        draw_text(screen, "GAME OVER", 48, (255, 0, 0), (WIDTH//2, 100))
        draw_text(screen, f"Player: {username}", 24, (255, 255, 255), (WIDTH//2, 180))
        draw_text(screen, f"Score: {score} | Level: {level}", 24, (255, 255, 255), (WIDTH//2, 220))
        draw_text(screen, f"Personal Best: {pb}", 24, (255, 255, 0), (WIDTH//2, 260))

        btn_retry.draw(screen)
        btn_menu.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.is_clicked(event):
                s, l = run_game(screen, username, settings)
                game_over_screen(username, s, l, settings)
                return
            if btn_menu.is_clicked(event):
                return

        pygame.display.flip()

def main_menu():
    settings = load_settings()
    
    btn_play = Button(200, "Play")
    btn_lb = Button(260, "Leaderboard")
    btn_set = Button(320, "Settings")
    btn_quit = Button(380, "Quit")

    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "ADVANCED SNAKE", 40, (0, 255, 0), (WIDTH//2, 100))

        for btn in [btn_play, btn_lb, btn_set, btn_quit]: btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if btn_play.is_clicked(event):
                username = get_username()
                score, level = run_game(screen, username, settings)
                game_over_screen(username, score, level, settings)
            
            if btn_lb.is_clicked(event): leaderboard_screen()
            if btn_set.is_clicked(event): settings_screen(settings)
            if btn_quit.is_clicked(event): pygame.quit(); sys.exit()

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()