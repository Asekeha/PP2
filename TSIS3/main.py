"""
main.py
Entry point for Speed Rush — Advanced Racer (TSIS 3).
"""

import sys
import pygame

import persistence
from racer import RacerGame
from ui    import ScreenManager
from audio import AudioManager


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Speed Rush — TSIS 3")
    clock  = pygame.time.Clock()

    ui  = ScreenManager(screen, clock)
    cfg = persistence.load_settings()

    # init audio based on saved settings
    AudioManager.init(enabled=cfg.get("sound", True),
                      volume=cfg.get("volume", 0.7))

    current   = "menu"
    username  = ""
    game      = None
    last_data : dict | None = None
    board     = persistence.load_leaderboard()

    while True:
        # ── MAIN MENU ─────────────────────────────────────────────────────────
        if current == "menu":
            action = ui.main_menu()
            if action == "quit":
                break
            elif action == "play":
                name = ui.get_username()
                if name:
                    username = name
                    game     = RacerGame(screen, clock, cfg, username)
                    current  = "game"
            elif action == "leaderboard":
                board = persistence.load_leaderboard()
                current = "leaderboard"
            elif action == "settings":
                current = "settings"

        # ── GAME ──────────────────────────────────────────────────────────────
        elif current == "game":
            result = game.run()       # blocks until game ends
            if result is None:        # window closed
                break
            last_data = result
            persistence.save_run(result)
            board = persistence.load_leaderboard()
            current = "game_over"

        # ── GAME OVER ─────────────────────────────────────────────────────────
        elif current == "game_over":
            action = ui.game_over_screen(last_data)
            if action == "retry":
                game    = RacerGame(screen, clock, cfg, username)
                current = "game"
            else:
                current = "menu"

        # ── LEADERBOARD ───────────────────────────────────────────────────────
        elif current == "leaderboard":
            ui.leaderboard_screen(board)
            current = "menu"

        # ── SETTINGS ──────────────────────────────────────────────────────────
        elif current == "settings":
            new_cfg = ui.settings_screen(cfg)
            cfg     = new_cfg
            persistence.save_settings(cfg)
            AudioManager.set_enabled(cfg.get("sound", True))
            current = "menu"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
