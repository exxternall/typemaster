import sys

import pygame

from game_modes import GameManager
from resources import load_font
from scoreboard import Scoreboard
from settings import Settings
from ui import UI


def main():
    pygame.init()
    pygame.display.set_caption("Typemaster")
    settings = Settings()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

    base_font = load_font(settings.font_path, settings.font_size)
    game_manager = GameManager(settings, base_font)
    ui = UI(screen, settings, base_font, game_manager)
    scoreboard = Scoreboard(screen, settings, base_font)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ui.handle_event(event)
            new_state = scoreboard.handle_event(event)
            if new_state:
                ui.state = new_state

        game_manager.update()
        ui.update()

        if game_manager.session_finished and ui.state == "game":
            ui.state = "scoreboard"
            scoreboard.update_score(game_manager)

        screen.fill(settings.bg_color)
        if ui.state == "scoreboard":
            scoreboard.draw()
        else:
            ui.draw()
        pygame.display.flip()
        clock.tick(settings.fps)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
