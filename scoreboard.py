import pygame


class Scoreboard:
    def __init__(self, screen, settings, font):
        self.screen = screen
        self.settings = settings
        self.font = font
        self.show_score = False
        self.stats = {}

    def update_score(self, game_manager):
        self.stats = game_manager.get_stats()
        self.show_score = True

    def draw(self):
        if not self.show_score:
            return

        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        wpm_text = f"WPM: {int(self.stats.get('wpm', 0))}"
        accuracy_text = f"Accuracy: {int(self.stats.get('accuracy', 0))}%"
        errors_text = f"Errors: {self.stats.get('errors', 0)}"
        total_seconds = int(self.stats.get('time_elapsed', 0))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = f"Time: {minutes}m {seconds}s"

        lines = [wpm_text, accuracy_text, errors_text, time_text]
        x = self.screen.get_width() // 2
        y = self.screen.get_height() // 2 - 100

        for line in lines:
            surf = self.font.render(line, True, (255, 255, 255))
            rect = surf.get_rect(center=(x, y))
            self.screen.blit(surf, rect)
            y += 60

        instr_text = "Нажмите пробел, чтобы вернуться в меню."
        instr_surf = self.font.render(instr_text, True, (200, 200, 200))
        instr_rect = instr_surf.get_rect(center=(x, y + 60))
        self.screen.blit(instr_surf, instr_rect)

    def handle_event(self, event):
        if self.show_score and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.show_score = False
            return "menu"
        return None
