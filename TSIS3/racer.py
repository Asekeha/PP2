"""
racer.py
Core gameplay loop: spawning, collisions, difficulty scaling, HUD.
"""

import pygame
import random
import math

from audio import AudioManager
from game_objects import (
    PlayerCar, TrafficCar, Obstacle, PowerUp, Coin, RoadRenderer,
    LANES, SCR_H, SCR_W, CAR_PALETTE, lane_x,
)

# ── difficulty presets ────────────────────────────────────────────────────────
_DIFF = {
    "easy":   dict(base_scroll=3.5, traffic_w=0.5, obs_w=0.5,  coin_bonus=1.3),
    "normal": dict(base_scroll=5.0, traffic_w=1.0, obs_w=1.0,  coin_bonus=1.0),
    "hard":   dict(base_scroll=7.0, traffic_w=1.6, obs_w=1.5,  coin_bonus=0.8),
}

TARGET_DIST  = 5000        # distance units to finish a run
POWERUP_TYPES  = ["nitro", "shield", "repair"]
OBSTACLE_KINDS = ["cone", "oil", "pothole", "barrier", "nitro_pad"]
OBS_WEIGHTS    = [        30,   25,       20,        15,         10]


class RacerGame:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 settings: dict, username: str):
        self.screen   = screen
        self.clock    = clock
        self.settings = settings
        self.username = username

        diff_key = settings.get("difficulty", "normal")
        diff     = _DIFF.get(diff_key, _DIFF["normal"])
        self._base_scroll  = diff["base_scroll"]
        self._traffic_w    = diff["traffic_w"]
        self._obs_w        = diff["obs_w"]
        self._coin_bonus   = diff["coin_bonus"]

        color_name = settings.get("car_color", "cyan")
        color      = CAR_PALETTE.get(color_name, (0, 220, 220))

        # entities
        self.road    = RoadRenderer()
        self.player  = PlayerCar(color)
        self.traffic : list[TrafficCar] = []
        self.obstacles: list[Obstacle]  = []
        self.powerups : list[PowerUp]   = []
        self.coins    : list[Coin]      = []

        # state
        self.scroll       = self._base_scroll
        self.distance     = 0.0
        self.score        = 0
        self.coins_got    = 0
        self.game_over    = False
        self.finished     = False
        self.paused       = False

        # active power-up
        self._pu_kind  : str | None = None
        self._pu_timer : int        = 0

        # speed slowdown timer (from obstacle hits)
        self._slow_timer  = 0
        self._slow_factor = 1.0

        # spawning
        self._spawn_tick  = 0
        self._spawn_every = 55    # frames between spawn attempts

        # fonts
        self._fnt_med   = pygame.font.SysFont(None, 32)
        self._fnt_big   = pygame.font.SysFont(None, 52)
        self._fnt_small = pygame.font.SysFont(None, 24)

        AudioManager.start_engine()

    # ── public run loop ───────────────────────────────────────────────────────
    def run(self) -> dict | None:
        """Runs the game; returns score-dict on exit (or None on window close)."""
        running = True
        while running:
            dt = self.clock.tick(60)

            # ── events ────────────────────────────────────────────────────────
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if not self.paused and not self.game_over:
                        if ev.key == pygame.K_LEFT:
                            self.player.move("left")
                        if ev.key == pygame.K_RIGHT:
                            self.player.move("right")

            if self.paused:
                self._draw_pause()
                pygame.display.flip()
                continue

            if not self.game_over:
                self._update()

            self._draw()
            pygame.display.flip()

            if self.game_over or self.finished:
                AudioManager.stop_engine()
                pygame.time.wait(400)
                running = False

        return self._score_data()

    # ── update ────────────────────────────────────────────────────────────────
    def _update(self):
        progress = self.distance / TARGET_DIST

        # scale up scroll speed over run
        self.scroll = self._base_scroll + progress * 4.0

        # apply nitro
        effective_scroll = self.scroll
        if self._pu_kind == "nitro":
            effective_scroll *= 1.9

        # apply slow debuff
        if self._slow_timer > 0:
            effective_scroll *= self._slow_factor
            self._slow_timer -= 1
        else:
            self._slow_factor = 1.0

        # advance power-up timer
        if self._pu_kind and self._pu_kind in ("nitro", "shield"):
            self._pu_timer -= 1
            if self._pu_timer <= 0:
                self._deactivate_pu()

        # distance & score trickle
        self.distance += effective_scroll / 10.0
        self.score    += int(effective_scroll * 0.4)

        if self.distance >= TARGET_DIST:
            self.score    += 1000     # finish bonus
            self.finished  = True
            AudioManager.play_finish()
            return

        # road scroll
        self.road.update(effective_scroll)
        self.player.update()
        AudioManager.set_engine_pitch(effective_scroll / (self._base_scroll * 2.5))

        # spawn
        self._spawn_tick += 1
        interval = max(18, self._spawn_every - int(progress * 28))
        if self._spawn_tick >= interval:
            self._spawn_tick = 0
            self._do_spawn(progress)

        # move entities
        for tc in self.traffic:  tc.update(effective_scroll)
        for ob in self.obstacles: ob.update(effective_scroll)
        for pu in self.powerups:  pu.update(effective_scroll)
        for cn in self.coins:     cn.update(effective_scroll)

        # cull off-screen
        self.traffic   = [t for t in self.traffic   if not t.off_screen()]
        self.obstacles = [o for o in self.obstacles  if not o.off_screen()]
        self.powerups  = [p for p in self.powerups
                          if not (p.y > SCR_H+10)]

        self.coins = [c for c in self.coins if not c.off_screen()]

        # collisions
        if self._check_collisions():
            self.game_over = True

    # ── spawning ──────────────────────────────────────────────────────────────
    def _do_spawn(self, progress: float):
        density = 0.6 + progress * 0.9

        # traffic
        if random.random() < 0.42 * density * self._traffic_w:
            self._spawn_traffic()

        # obstacle
        if random.random() < 0.30 * density * self._obs_w:
            self._spawn_obstacle()

        # coin
        if random.random() < 0.50:
            self._spawn_coin()

        # power-up (rare)
        if random.random() < 0.025 and len(self.powerups) < 2:
            self._spawn_powerup()

    def _spawn_traffic(self):
        lane = random.randint(0, 4)
        spd  = random.uniform(1.8, 3.2) * self._traffic_w
        tc   = TrafficCar(lane, spd)
        # safety check: don't overlap existing traffic at top
        for existing in self.traffic:
            if existing.lane == lane and existing.y < 60:
                return
        self.traffic.append(tc)

    def _spawn_obstacle(self):
        lane = random.randint(0, 4)
        # don't spawn on player lane if player is nearby (y > 350)
        if lane == self.player.lane and self.player.y > 350:
            lane = (lane + random.choice([-1,1])) % 5
        kind = random.choices(OBSTACLE_KINDS, weights=OBS_WEIGHTS)[0]
        self.obstacles.append(Obstacle(lane, kind))

    def _spawn_coin(self):
        lane = random.randint(0, 4)
        self.coins.append(Coin(lane))

    def _spawn_powerup(self):
        lane = random.randint(0, 4)
        kind = random.choice(POWERUP_TYPES)
        self.powerups.append(PowerUp(lane, kind))

    # ── collisions ────────────────────────────────────────────────────────────
    def _check_collisions(self) -> bool:
        pr = self.player.rect()

        # traffic → fatal (unless shield)
        for tc in self.traffic[:]:
            if pr.colliderect(tc.rect()):
                if self.player.shield:
                    self._deactivate_pu()
                    self.traffic.remove(tc)
                    self.score -= 50
                else:
                    AudioManager.play_crash()
                    return True      # game over

        # obstacles
        for ob in self.obstacles[:]:
            if pr.colliderect(ob.rect()):
                if ob.kind == "nitro_pad":
                    self.score += ob.pts
                    self._activate_pu_direct("nitro", 120)
                    AudioManager.play_nitro()
                    self.obstacles.remove(ob)
                elif self.player.shield:
                    self._deactivate_pu()
                    self.obstacles.remove(ob)
                    self.score += ob.pts
                else:
                    AudioManager.play_obstacle()
                    self.score += ob.pts
                    if ob.slow > 0:
                        self._slow_timer  = 90
                        self._slow_factor = ob.slow
                    if ob.kind == "barrier":
                        AudioManager.play_crash()
                        return True
                    self.obstacles.remove(ob)

        # coins
        for cn in self.coins[:]:
            if pr.colliderect(cn.rect()):
                bonus = cn.value * int(10 * self._coin_bonus)
                self.score     += bonus
                self.coins_got += 1
                AudioManager.play_coin()
                self.coins.remove(cn)

        # power-ups
        for pu in self.powerups[:]:
            if pr.colliderect(pu.rect()):
                AudioManager.play_powerup()
                self._collect_powerup(pu)
                self.powerups.remove(pu)

        return False

    # ── power-up logic ────────────────────────────────────────────────────────
    def _collect_powerup(self, pu: PowerUp):
        if pu.kind == "nitro":
            self._activate_pu_direct("nitro", pu.effect_duration)
        elif pu.kind == "shield":
            self._activate_pu_direct("shield", pu.effect_duration)
        elif pu.kind == "repair":
            # instant: clear nearest obstacle or restore a score chunk
            if self.obstacles:
                self.obstacles.pop(0)
            self.score += 40

    def _activate_pu_direct(self, kind: str, duration: int):
        # only one active at a time
        self._deactivate_pu()
        self._pu_kind  = kind
        self._pu_timer = duration
        if kind == "shield":
            self.player.shield = True

    def _deactivate_pu(self):
        if self._pu_kind == "shield":
            self.player.shield = False
        self._pu_kind  = None
        self._pu_timer = 0

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        self.road.draw(self.screen)

        for ob in self.obstacles:  ob.draw(self.screen)
        for cn in self.coins:      cn.draw(self.screen)
        for pu in self.powerups:   pu.draw(self.screen)
        for tc in self.traffic:    tc.draw(self.screen)
        self.player.draw(self.screen)

        self._draw_hud()

        if self.game_over:
            self._draw_overlay("CRASH!", (220, 40, 40))
        elif self.finished:
            self._draw_overlay("FINISH!", (50, 220, 80))

    def _draw_hud(self):
        # semi-transparent panel
        panel = pygame.Surface((190, 210), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        self.screen.blit(panel, (8, 8))

        def label(text, y, color=(255,255,255)):
            surf = self._fnt_med.render(text, True, color)
            self.screen.blit(surf, (16, y))

        label(f"Score:  {self.score}",          16, (255, 220, 80))
        label(f"Coins:  {self.coins_got}",       46, (220, 180, 0))
        label(f"Dist:   {int(self.distance)}/{TARGET_DIST}", 76)
        label(f"Speed:  {int(self.scroll*18)} km/h", 106)

        # progress bar
        bar_w  = 170
        filled = int(bar_w * min(1.0, self.distance / TARGET_DIST))
        pygame.draw.rect(self.screen, (70, 70, 70),  (16, 136, bar_w, 12))
        pygame.draw.rect(self.screen, (60, 220, 80), (16, 136, filled, 12))

        # active power-up
        if self._pu_kind:
            pu_colors = {"nitro":(0,200,255), "shield":(80,100,255)}
            col = pu_colors.get(self._pu_kind, (60,220,80))
            label(f"[{self._pu_kind.upper()}]  {self._pu_timer//60}s", 158, col)

        # controls hint at bottom
        hint = self._fnt_small.render("← → Move  |  ESC Pause", True, (170,170,170))
        self.screen.blit(hint, (16, 582))

    def _draw_overlay(self, text: str, color):
        surf = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)
        surf.fill((0,0,0,120))
        self.screen.blit(surf, (0, 0))
        txt = self._fnt_big.render(text, True, color)
        r   = txt.get_rect(center=(SCR_W//2, SCR_H//2))
        self.screen.blit(txt, r)

    def _draw_pause(self):
        self._draw()
        surf = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)
        surf.fill((0,0,0,140))
        self.screen.blit(surf, (0,0))
        txt = self._fnt_big.render("PAUSED", True, (255,255,255))
        self.screen.blit(txt, txt.get_rect(center=(SCR_W//2, SCR_H//2-20)))
        sub = self._fnt_med.render("Press ESC to resume", True, (180,180,180))
        self.screen.blit(sub, sub.get_rect(center=(SCR_W//2, SCR_H//2+30)))

    # ── result ────────────────────────────────────────────────────────────────
    def _score_data(self) -> dict:
        return {
            "username": self.username,
            "score":    self.score,
            "distance": int(self.distance),
            "coins":    self.coins_got,
            "finished": self.finished,
        }
