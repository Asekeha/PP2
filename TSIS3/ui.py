"""
ui.py
All pygame screens: Main Menu, Username entry, Settings,
Game Over, Leaderboard.
No external UI libraries — pure pygame drawing.
"""

import pygame
import math

SCR_W, SCR_H = 800, 600

# ── colour constants ──────────────────────────────────────────────────────────
C_BG1   = (14,  18,  40)
C_BG2   = (30,  40,  80)
C_GOLD  = (255, 210, 60)
C_WHITE = (240, 240, 240)
C_GREY  = (130, 130, 150)
C_GREEN = (60,  210, 80)
C_RED   = (220, 55,  55)

CAR_COLORS = {
    "cyan":   (0,   220, 220),
    "red":    (220,  40,  40),
    "orange": (255, 140,   0),
    "lime":   ( 80, 220,  50),
    "violet": (160,  50, 240),
}


# ── Button ────────────────────────────────────────────────────────────────────
class Btn:
    def __init__(self, rect, text, base=(50,55,80), hover=(90,100,140),
                 text_color=C_WHITE, fnt_size=30):
        self.rect       = pygame.Rect(rect)
        self.text       = text
        self.base       = base
        self.hover      = hover
        self.text_color = text_color
        self._fnt       = pygame.font.SysFont(None, fnt_size)
        self._hovered   = False

    def draw(self, surf: pygame.Surface, highlight=False):
        col = self.hover if (self._hovered or highlight) else self.base
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        border_col = C_GOLD if highlight else (100, 110, 150)
        pygame.draw.rect(surf, border_col, self.rect, 2, border_radius=8)
        txt = self._fnt.render(self.text, True, self.text_color)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, ev) -> bool:
        if ev.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                return True
        return False


# ── background helper ─────────────────────────────────────────────────────────
def _draw_bg(surf: pygame.Surface, tick: int = 0):
    """Animated gradient + scrolling stars."""
    for y in range(SCR_H):
        t = y / SCR_H
        r = int(C_BG1[0] + (C_BG2[0]-C_BG1[0])*t)
        g = int(C_BG1[1] + (C_BG2[1]-C_BG1[1])*t)
        b = int(C_BG1[2] + (C_BG2[2]-C_BG1[2])*t)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCR_W, y))

    # simple star field
    import random
    rng = random.Random(42)
    for _ in range(60):
        sx = rng.randint(0, SCR_W-1)
        sy = (rng.randint(0, SCR_H-1) + tick // 3) % SCR_H
        br = rng.randint(120, 220)
        pygame.draw.circle(surf, (br, br, br), (sx, sy), 1)


# ── ScreenManager (all screens) ───────────────────────────────────────────────
class ScreenManager:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock  = clock
        self._tick  = 0
        self._fnt_title = pygame.font.SysFont(None, 72)
        self._fnt_med   = pygame.font.SysFont(None, 36)
        self._fnt_small = pygame.font.SysFont(None, 26)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _bg(self):
        _draw_bg(self.screen, self._tick)
        self._tick += 1

    def _title(self, text: str, y=70, color=C_GOLD):
        surf = self._fnt_title.render(text, True, color)
        # shadow
        shadow = self._fnt_title.render(text, True, (30,30,30))
        self.screen.blit(shadow, shadow.get_rect(center=(SCR_W//2+3, y+3)))
        self.screen.blit(surf,   surf.get_rect(center=(SCR_W//2, y)))

    def _label(self, text, y, color=C_WHITE, center=True, x=None, fnt=None):
        fnt  = fnt or self._fnt_med
        surf = fnt.render(text, True, color)
        if center:
            self.screen.blit(surf, surf.get_rect(center=(SCR_W//2, y)))
        else:
            self.screen.blit(surf, (x, y))

    # ── MAIN MENU ─────────────────────────────────────────────────────────────
    def main_menu(self) -> str:
        btns = {
            "play":        Btn((300, 240, 200, 52), "▶  PLAY"),
            "leaderboard": Btn((300, 308, 200, 52), "🏆  LEADERBOARD"),
            "settings":    Btn((300, 376, 200, 52), "⚙  SETTINGS"),
            "quit":        Btn((300, 444, 200, 52), "✕  QUIT", base=(80,30,30), hover=(130,40,40)),
        }

        while True:
            self._bg()
            self._title("SPEED RUSH")
            self._label("Arcade Racer", 120, C_GREY)

            # animated car silhouette
            t = self._tick
            cx = SCR_W//2 + int(30 * math.sin(t * 0.02))
            self._draw_mini_car(cx, 185, (0,200,220))

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit"
                for key, btn in btns.items():
                    if btn.handle(ev):
                        return key

            for btn in btns.values():
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    # ── USERNAME ENTRY ────────────────────────────────────────────────────────
    def get_username(self) -> str | None:
        text = ""
        box  = pygame.Rect(240, 280, 320, 48)

        while True:
            self._bg()
            self._title("ENTER YOUR NAME", 120)
            self._label("This name will appear on the leaderboard.", 195, C_GREY,
                        fnt=self._fnt_small)

            # input box
            pygame.draw.rect(self.screen, (30,30,50), box, border_radius=6)
            pygame.draw.rect(self.screen, C_GOLD,     box, 2, border_radius=6)
            txt_surf = self._fnt_med.render(text, True, C_WHITE)
            self.screen.blit(txt_surf, (box.x+10, box.y+10))
            # cursor blink
            if self._tick % 70 < 35:
                cx = box.x + 10 + txt_surf.get_width() + 2
                pygame.draw.line(self.screen, C_WHITE, (cx, box.y+8), (cx, box.y+38), 2)

            self._label("ENTER  to start   |   ESC  to cancel", 360, C_GREY,
                        fnt=self._fnt_small)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        name = text.strip()
                        return name if name else "Player"
                    elif ev.key == pygame.K_ESCAPE:
                        return None
                    elif ev.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif ev.unicode.isprintable() and len(text) < 18:
                        text += ev.unicode

            pygame.display.flip()
            self.clock.tick(60)
            self._tick += 1

    # ── GAME OVER ─────────────────────────────────────────────────────────────
    def game_over_screen(self, data: dict | None) -> str:
        btn_retry = Btn((220, 460, 150, 50), "RETRY",     base=(40,80,40), hover=(60,130,60))
        btn_menu  = Btn((430, 460, 150, 50), "MAIN MENU", base=(50,50,80), hover=(80,80,130))

        finished = data and data.get("finished", False)
        title_text  = "FINISH!" if finished else "GAME OVER"
        title_color = C_GREEN  if finished else C_RED

        while True:
            self._bg()
            self._title(title_text, 90, title_color)

            if data:
                # stats panel
                panel = pygame.Surface((380, 220), pygame.SRCALPHA)
                panel.fill((0, 0, 0, 170))
                self.screen.blit(panel, (210, 200))

                rows = [
                    ("Player",   data.get("username",  "?")),
                    ("Score",    str(data.get("score",    0))),
                    ("Distance", f"{data.get('distance', 0)} m"),
                    ("Coins",    str(data.get("coins",    0))),
                ]
                for i, (k, v) in enumerate(rows):
                    y = 220 + i*50
                    self._label(k+":",  y, C_GREY,   center=False, x=230)
                    self._label(v,      y, C_GOLD,   center=False, x=390)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "menu"
                if btn_retry.handle(ev): return "retry"
                if btn_menu.handle(ev):  return "menu"

            btn_retry.draw(self.screen)
            btn_menu.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
            self._tick += 1

    # ── LEADERBOARD ───────────────────────────────────────────────────────────
    def leaderboard_screen(self, board: list) -> None:
        btn_back = Btn((310, 545, 180, 44), "← BACK")

        cols = [50, 130, 370, 520, 650]
        headers = ["#", "Name", "Score", "Dist.", "Coins"]

        while True:
            self._bg()
            self._title("LEADERBOARD", 55)

            # header row
            for hx, h in zip(cols, headers):
                s = self._fnt_small.render(h, True, C_GOLD)
                self.screen.blit(s, (hx, 110))
            pygame.draw.line(self.screen, C_GREY, (40, 132), (760, 132), 1)

            for i, entry in enumerate(board[:10]):
                y = 146 + i * 36
                col = C_GOLD if i == 0 else (C_WHITE if i%2==0 else C_GREY)
                vals = [
                    str(i+1),
                    entry.get("username","?")[:14],
                    str(entry.get("score",0)),
                    str(entry.get("distance",0))+"m",
                    str(entry.get("coins",0)),
                ]
                for hx, v in zip(cols, vals):
                    s = self._fnt_small.render(v, True, col)
                    self.screen.blit(s, (hx, y))

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                if btn_back.handle(ev):
                    return

            btn_back.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
            self._tick += 1

    # ── SETTINGS ─────────────────────────────────────────────────────────────
    def settings_screen(self, cfg: dict) -> dict:
        cfg = dict(cfg)    # work on a copy

        # sound toggle
        def sound_text(): return "Sound:  ON" if cfg.get("sound", True) else "Sound:  OFF"
        btn_sound = Btn((290, 195, 220, 46), sound_text())

        # car colors
        color_keys = list(CAR_COLORS.keys())
        color_btns = []
        for i, ck in enumerate(color_keys):
            r = (130 + i*100, 290, 88, 44)
            color_btns.append((Btn(r, ck.capitalize(), base=CAR_COLORS[ck],
                                   hover=CAR_COLORS[ck]), ck))

        # difficulty
        diffs = ["easy", "normal", "hard"]
        diff_btns = []
        for i, d in enumerate(diffs):
            r = (185 + i*140, 390, 128, 44)
            diff_btns.append((Btn(r, d.upper()), d))

        btn_save = Btn((295, 490, 210, 48), "SAVE & RETURN",
                       base=(40,80,40), hover=(60,130,60))

        while True:
            self._bg()
            self._title("SETTINGS", 70)

            self._label("Audio",       165, C_GREY, fnt=self._fnt_small)
            self._label("Car Colour",  265, C_GREY, fnt=self._fnt_small)
            self._label("Difficulty",  365, C_GREY, fnt=self._fnt_small)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return cfg
                if btn_sound.handle(ev):
                    cfg["sound"] = not cfg.get("sound", True)
                    btn_sound.text = sound_text()
                for btn, ck in color_btns:
                    if btn.handle(ev):
                        cfg["car_color"] = ck
                for btn, d in diff_btns:
                    if btn.handle(ev):
                        cfg["difficulty"] = d
                if btn_save.handle(ev):
                    return cfg

            btn_sound.draw(self.screen, highlight=True)
            for btn, ck in color_btns:
                btn.draw(self.screen, highlight=(cfg.get("car_color") == ck))
            for btn, d in diff_btns:
                btn.draw(self.screen, highlight=(cfg.get("difficulty") == d))
            btn_save.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
            self._tick += 1

    # ── tiny car silhouette for menu ──────────────────────────────────────────
    def _draw_mini_car(self, cx: int, cy: int, color):
        w, h = 28, 44
        x, y = cx - w//2, cy - h//2
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=6)
        pygame.draw.rect(self.screen, (140, 210, 240), (x+4, y+6, w-8, 10), border_radius=3)
        for wx_, wy_ in [(x-3,y+6),(x+w-1,y+6),(x-3,y+28),(x+w-1,y+28)]:
            pygame.draw.rect(self.screen, (20,20,20), (wx_, wy_, 5, 10), border_radius=2)
