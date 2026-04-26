"""
game_objects.py
All drawable / collidable entities for the racer.
"""

import pygame
import random
import math

# ── colour palette ────────────────────────────────────────────────────────────
CAR_PALETTE = {
    "cyan":    (0,   220, 220),
    "red":     (220,  40,  40),
    "orange":  (255, 140,   0),
    "lime":    ( 80, 220,  50),
    "violet":  (160,  50, 240),
}

# 5 lane centres (road spans x=160..640, width=480, lane width=96)
LANES      = [208, 304, 400, 496, 592]
ROAD_LEFT  = 160
ROAD_RIGHT = 640
SCR_H      = 600
SCR_W      = 800


# ── helpers ───────────────────────────────────────────────────────────────────
def lane_x(idx: int) -> int:
    return LANES[max(0, min(4, idx))]


# ── PlayerCar ─────────────────────────────────────────────────────────────────
class PlayerCar:
    W, H = 42, 68

    def __init__(self, color=(0, 220, 220)):
        self.lane   = 2
        self.x      = float(lane_x(2))
        self.y      = 490.0
        self.color  = color
        self.shield = False
        # smooth slide
        self._target_x = self.x
        self._slide    = 0.0          # 0..1 animation

    # ── movement ──────────────────────────────────────────────────────────────
    def move(self, direction: str):
        if direction == "left"  and self.lane > 0: self.lane -= 1
        if direction == "right" and self.lane < 4: self.lane += 1
        self._target_x = float(lane_x(self.lane))

    def update(self):
        dx = self._target_x - self.x
        self.x += dx * 0.25          # lerp

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface):
        ix = int(self.x)
        iy = int(self.y)
        c  = self.color

        # body
        pygame.draw.rect(surf, c,        (ix,      iy,      self.W, self.H), border_radius=9)
        # roof
        pygame.draw.rect(surf, _darken(c, 0.65),
                         (ix+7,  iy+8,   self.W-14, 22),    border_radius=5)
        # windshield (front = top of sprite)
        pygame.draw.rect(surf, (140, 210, 240),
                         (ix+8,  iy+6,   self.W-16, 14),    border_radius=4)
        # rear window
        pygame.draw.rect(surf, (140, 210, 240),
                         (ix+8,  iy+32,  self.W-16, 10),    border_radius=3)
        # headlights
        for hx in (ix+5, ix+self.W-11):
            pygame.draw.rect(surf, (255, 255, 180), (hx, iy+2,  6, 4), border_radius=2)
        # tail lights
        for hx in (ix+5, ix+self.W-11):
            pygame.draw.rect(surf, (220, 40,  40),  (hx, iy+62, 6, 4), border_radius=2)
        # wheels
        for wx, wy in [(ix-4, iy+8), (ix+self.W-2, iy+8),
                       (ix-4, iy+48),(ix+self.W-2, iy+48)]:
            pygame.draw.rect(surf, (30, 30, 30), (wx, wy, 8, 14), border_radius=3)

        # shield aura
        if self.shield:
            aura = pygame.Surface((self.W+16, self.H+16), pygame.SRCALPHA)
            t = pygame.time.get_ticks()
            alpha = int(80 + 60 * math.sin(t * 0.006))
            pygame.draw.ellipse(aura, (80, 160, 255, alpha),
                                (0, 0, self.W+16, self.H+16), 3)
            surf.blit(aura, (ix-8, iy-8))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)


# ── TrafficCar ────────────────────────────────────────────────────────────────
class TrafficCar:
    W, H = 42, 68
    _COLORS = [
        (180, 60,  60),  (60,  60, 180), (60, 180,  60),
        (180, 120, 60),  (120, 60, 180), (180, 180, 60),
    ]

    def __init__(self, lane: int, speed: float):
        self.lane  = lane
        self.x     = float(lane_x(lane))
        self.y     = float(-self.H - random.randint(0, 40))
        self.speed = speed
        self.color = random.choice(self._COLORS)

    def update(self, scroll: float):
        self.y += scroll + self.speed

    def draw(self, surf: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        c = self.color
        pygame.draw.rect(surf, c,              (ix, iy, self.W, self.H),     border_radius=8)
        pygame.draw.rect(surf, _darken(c,.6),  (ix+7, iy+8, self.W-14, 20), border_radius=5)
        pygame.draw.rect(surf, (100, 130, 160),(ix+8, iy+6, self.W-16, 14), border_radius=3)
        pygame.draw.rect(surf, (100, 130, 160),(ix+8, iy+32,self.W-16, 10), border_radius=3)
        for hx in (ix+5, ix+self.W-11):
            pygame.draw.rect(surf, (255, 100, 100),(hx, iy+2,  6, 4), border_radius=2)
        for wx,wy in [(ix-4,iy+8),(ix+self.W-2,iy+8),
                      (ix-4,iy+48),(ix+self.W-2,iy+48)]:
            pygame.draw.rect(surf, (30,30,30),(wx,wy,8,14), border_radius=3)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def off_screen(self) -> bool:
        return self.y > SCR_H + 20


# ── Obstacle ──────────────────────────────────────────────────────────────────
_OBS_CFG = {
    "cone":    dict(color=(255, 110,  0), label="CONE",     pts=-10, slow=0.0),
    "oil":     dict(color=( 40,  40, 40), label="OIL",      pts=-15, slow=0.3),
    "pothole": dict(color=( 70,  70, 70), label="POTHOLE",  pts=-20, slow=0.2),
    "barrier": dict(color=(160,  60,  0), label="BARRIER",  pts=-30, slow=0.0),
    "nitro_pad": dict(color=(0,  220, 220),label="NITRO",   pts= 20, slow=0.0),
}

class Obstacle:
    SIZE = 38

    def __init__(self, lane: int, kind: str):
        self.lane  = lane
        self.kind  = kind
        cfg        = _OBS_CFG[kind]
        self.color = cfg["color"]
        self.label = cfg["label"]
        self.pts   = cfg["pts"]
        self.slow  = cfg["slow"]          # speed reduction factor (0 = no slow)
        self.x     = float(lane_x(lane))
        self.y     = float(-self.SIZE - 10)
        self._tick = 0

    def update(self, scroll: float):
        self.y    += scroll
        self._tick += 1

    def draw(self, surf: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        s  = self.SIZE
        ht = self._tick

        if self.kind == "cone":
            pts = [(ix+s//2, iy), (ix+4, iy+s-4), (ix+s-4, iy+s-4)]
            pygame.draw.polygon(surf, self.color, pts)
            pygame.draw.polygon(surf, (255,255,255), pts, 2)
            pygame.draw.rect(surf, (255,255,255), (ix+4, iy+s-12, s-8, 6))

        elif self.kind == "oil":
            for i in range(3):
                rx = ix + math.sin(ht*0.05 + i*1.2)*2
                pygame.draw.ellipse(surf, self.color, (rx+i*2, iy+i, s-i*4, s//2-i*2))
            pygame.draw.ellipse(surf, (80,80,80), (ix+6, iy+4, s-12, s//2-8), 1)

        elif self.kind == "pothole":
            pygame.draw.circle(surf, (55,55,55), (ix+s//2, iy+s//2), s//2)
            pygame.draw.circle(surf, (10,10,10), (ix+s//2, iy+s//2), s//2-6)

        elif self.kind == "barrier":
            pygame.draw.rect(surf, self.color, (ix, iy+s//3, s, s//3))
            # warning stripes
            for i in range(4):
                col = (255,220,0) if i%2==0 else (255,0,0)
                pygame.draw.rect(surf, col, (ix+i*(s//4), iy+s//3, s//4, s//3))

        elif self.kind == "nitro_pad":
            # glowing blue-cyan strip
            glow = int(80 + 70*math.sin(ht*0.12))
            pygame.draw.rect(surf, (*self.color, 200), (ix, iy, s, s//2))
            for k in range(3):
                lc = (0, 180+glow//3, 255)
                pygame.draw.line(surf, lc, (ix+5+k*10, iy+4), (ix+14+k*10, iy+s//2-4), 3)
            font = pygame.font.Font(None, 18)
            surf.blit(font.render("NITRO", True, (255,255,255)), (ix+2, iy+s//2+2))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.SIZE, self.SIZE)

    def off_screen(self) -> bool:
        return self.y > SCR_H + 10


# ── PowerUp ───────────────────────────────────────────────────────────────────
_PU_CFG = {
    "nitro":  dict(color=(0, 230, 255),  icon="N", duration=240),
    "shield": dict(color=(80, 100, 255), icon="S", duration=360),
    "repair": dict(color=(60, 220,  80), icon="R", duration=0),
}

class PowerUp:
    SIZE = 32
    TIMEOUT = 420          # frames before auto-despawn

    def __init__(self, lane: int, kind: str):
        self.lane   = lane
        self.kind   = kind
        cfg         = _PU_CFG[kind]
        self.color  = cfg["color"]
        self.icon   = cfg["icon"]
        self.effect_duration = cfg["duration"]
        self.x      = float(lane_x(lane))
        self.y      = float(-self.SIZE - 10)
        self._life  = self.TIMEOUT
        self._tick  = 0

    def update(self, scroll: float) -> bool:
        self.y    += scroll
        self._life -= 1
        self._tick += 1
        return self._life > 0 and self.y < SCR_H + 10

    def draw(self, surf: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        s  = self.SIZE
        t  = self._tick
        # pulsing outline
        pulse = int(2 + 3*abs(math.sin(t*0.08)))
        pygame.draw.rect(surf, self.color, (ix, iy, s, s), border_radius=7)
        pygame.draw.rect(surf, (255,255,255), (ix, iy, s, s), pulse, border_radius=7)
        font = pygame.font.Font(None, 26)
        txt  = font.render(self.icon, True, (255,255,255))
        surf.blit(txt, (ix + s//2 - txt.get_width()//2,
                        iy + s//2 - txt.get_height()//2))
        # timer bar beneath
        frac  = self._life / self.TIMEOUT
        bw    = int(s * frac)
        pygame.draw.rect(surf, (60,60,60),   (ix,   iy+s+2, s,  4))
        pygame.draw.rect(surf, self.color,   (ix,   iy+s+2, bw, 4))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.SIZE, self.SIZE)


# ── Coin (weighted) ───────────────────────────────────────────────────────────
_COIN_COLORS = {1: (180, 120, 40), 2: (180, 180, 180), 3: (220, 180, 0)}

class Coin:
    R = 13

    def __init__(self, lane: int):
        w = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        self.value = w
        self.color = _COIN_COLORS[w]
        self.x     = float(lane_x(lane))
        self.y     = float(-self.R*2 - 5)
        self._tick = random.randint(0, 60)

    def update(self, scroll: float):
        self.y    += scroll
        self._tick += 1

    def draw(self, surf: pygame.Surface):
        ix = int(self.x) + self.R
        iy = int(self.y) + self.R
        r  = self.R + int(2*abs(math.sin(self._tick*0.1)))
        pygame.draw.circle(surf, self.color, (ix, iy), r)
        pygame.draw.circle(surf, (255,255,255), (ix, iy), r, 2)
        font = pygame.font.Font(None, 20)
        surf.blit(font.render(str(self.value), True, (30,30,30)),
                  (ix-5, iy-7))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.R*2, self.R*2)

    def off_screen(self) -> bool:
        return self.y > SCR_H + 10


# ── Road background renderer ──────────────────────────────────────────────────
class RoadRenderer:
    DASH_H    = 28
    DASH_GAP  = 22
    CYCLE     = DASH_H + DASH_GAP

    def __init__(self):
        self._offset = 0.0

    def update(self, scroll: float):
        self._offset = (self._offset + scroll) % self.CYCLE

    def draw(self, surf: pygame.Surface):
        # grass / sky sides
        surf.fill((30, 90, 30))
        # road surface
        pygame.draw.rect(surf, (55, 55, 55), (ROAD_LEFT, 0, ROAD_RIGHT-ROAD_LEFT, SCR_H))

        # lane separators (white dashes)
        for lane_idx in range(1, 5):
            lx = ROAD_LEFT + lane_idx * ((ROAD_RIGHT-ROAD_LEFT) // 5)
            y  = -self.CYCLE + self._offset
            while y < SCR_H:
                pygame.draw.rect(surf, (220, 220, 220), (lx-2, int(y), 4, self.DASH_H))
                y += self.CYCLE

        # hard edge lines
        pygame.draw.line(surf, (240, 200, 0), (ROAD_LEFT,  0), (ROAD_LEFT,  SCR_H), 5)
        pygame.draw.line(surf, (240, 200, 0), (ROAD_RIGHT, 0), (ROAD_RIGHT, SCR_H), 5)

        # kerb stripes on edges
        stripe_h = 24
        num = SCR_H // stripe_h + 2
        for i in range(num):
            ky = int(-self._offset % (stripe_h*2)) + i * stripe_h
            col = (220, 40, 40) if i % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(surf, col, (ROAD_LEFT-12,  ky, 12, stripe_h))
            pygame.draw.rect(surf, col, (ROAD_RIGHT,    ky, 12, stripe_h))


# ── internal helpers ─────────────────────────────────────────────────────────
def _darken(color, factor=0.6):
    return tuple(max(0, int(c * factor)) for c in color)
