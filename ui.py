import sys

import pygame

from resources import load_image, load_font


class UI:
    def __init__(self, screen, settings, font, game_manager):
        self.screen = screen
        self.settings = settings
        self.font = font
        self.menu_font = load_font(self.settings.font_path, self.settings.menu_font_size)
        self.game_manager = game_manager

        self.state = "menu"
        self.input_text = ""

        self.mode_buttons = []
        self.option_buttons = []
        self.exit_button = None
        self.create_menu_buttons()

        self.button_scales = {btn[0]: 0.0 for btn in self.mode_buttons + self.option_buttons}
        if self.exit_button:
            self.button_scales["exit"] = 0.0
        self.option_colors = {
            "numbers": list(self.settings.option_disabled_color),
            "punctuation": list(self.settings.option_disabled_color)
        }
        self.cursor_alpha = 255

        self.icons = {}
        for mode in ["time", "words", "quote", "zen", "numbers", "punctuation", "language", "custom", "exit"]:
            path = self.settings.icon_paths.get(mode)
            if path:
                icon = load_image(path)
                if icon:
                    icon = pygame.transform.smoothscale(icon, (40, 40))
                    self.icons[mode] = icon

        self.configuring_mode = None
        self.parameter_buttons = []
        self.panel_y = self.screen.get_height() // 2 - 100
        self.panel_target_y = self.screen.get_height() // 2 - 100

    def create_menu_buttons(self):
        modes = ["time", "words", "quote", "zen", "language", "custom"]
        options = ["numbers", "punctuation"]
        buttons_per_row = 3
        mode_rows = (len(modes) + buttons_per_row - 1) // buttons_per_row
        total_rows = mode_rows + 1
        height = self.settings.menu_button_height
        spacing = self.settings.menu_vertical_spacing
        total_height = total_rows * height + (total_rows - 1) * spacing
        start_y = (self.screen.get_height() - total_height) // 2

        total_width = buttons_per_row * self.settings.menu_button_width + (
                buttons_per_row - 1) * self.settings.menu_horizontal_spacing
        start_x = (self.screen.get_width() - total_width) // 2

        self.mode_buttons = []
        for index, mode_name in enumerate(modes):
            row = index // buttons_per_row
            col = index % buttons_per_row
            x = start_x + col * (self.settings.menu_button_width + self.settings.menu_horizontal_spacing)
            y = start_y + row * (height + spacing)
            rect = pygame.Rect(x, y, self.settings.menu_button_width, height)
            self.mode_buttons.append((mode_name, rect))

        option_start_y = start_y + mode_rows * (height + spacing)
        option_spacing = (total_width - 3 * self.settings.menu_button_width) // 2
        numbers_x = start_x
        exit_x = start_x + self.settings.menu_button_width + option_spacing
        punctuation_x = start_x + 2 * self.settings.menu_button_width + 2 * option_spacing

        self.option_buttons = []
        numbers_rect = pygame.Rect(numbers_x, option_start_y, self.settings.menu_button_width, height)
        self.option_buttons.append(("numbers", numbers_rect))

        exit_rect = pygame.Rect(exit_x, option_start_y, self.settings.menu_button_width, height)
        self.exit_button = ("exit", exit_rect)

        punctuation_rect = pygame.Rect(punctuation_x, option_start_y, self.settings.menu_button_width, height)
        self.option_buttons.append(("punctuation", punctuation_rect))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "game":
                if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_SHIFT):
                    self.game_manager.restart_session()
                elif event.key == pygame.K_RETURN:
                    self.game_manager.handle_input("\r")
                elif event.key == pygame.K_SPACE:
                    self.game_manager.handle_input(" ")
                elif event.key == pygame.K_BACKSPACE:
                    self.game_manager.handle_backspace()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                else:
                    char = event.unicode
                    self.game_manager.handle_input(char)
            elif self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.state = "game"
            elif self.state == "custom_setup":
                if event.key == pygame.K_RETURN:
                    self.parse_custom_input()
                    self.state = "game"
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode
            elif self.state == "parameter_selection":
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.state == "menu":
                    self.handle_menu_click(event.pos)
                elif self.state == "parameter_selection":
                    for btn in self.parameter_buttons:
                        if btn[0] != "label":
                            actual_rect = btn[1].copy()
                            actual_rect.y += self.panel_y
                            if actual_rect.collidepoint(event.pos):
                                option = int(btn[0])
                                if self.configuring_mode == "time":
                                    self.game_manager.set_mode("time", option)
                                elif self.configuring_mode == "words":
                                    self.game_manager.set_mode("words", option)
                                self.state = "game"
                                return

    def handle_menu_click(self, mouse_pos):
        for mode_name, rect in self.mode_buttons:
            if rect.collidepoint(mouse_pos):
                if mode_name in ["time", "words"]:
                    self.configuring_mode = mode_name
                    self.state = "parameter_selection"
                    self.create_parameter_buttons()
                    self.panel_y = self.panel_target_y
                elif mode_name == "custom":
                    self.state = "custom_setup"
                else:
                    self.game_manager.set_mode(mode_name)
                    self.state = "game"
                return
        for option_name, rect in self.option_buttons:
            if rect.collidepoint(mouse_pos):
                if option_name == "numbers":
                    self.settings.numbers_enabled = not self.settings.numbers_enabled
                elif option_name == "punctuation":
                    self.settings.punctuation_enabled = not self.settings.punctuation_enabled
                return
        if self.exit_button and self.exit_button[1].collidepoint(mouse_pos):
            pygame.quit()
            sys.exit()

    def create_parameter_buttons(self):
        self.parameter_buttons = []
        if self.configuring_mode == "time":
            options = self.settings.time_modes
            label = "Выберите время (секунды):"
        elif self.configuring_mode == "words":
            options = self.settings.word_modes
            label = "Выберите количество слов:"
        else:
            return

        label_surface = self.menu_font.render(label, True, self.settings.text_color)
        label_width, label_height = label_surface.get_size()
        label_left = (self.screen.get_width() - label_width) // 2
        label_top = 20
        label_rect = pygame.Rect(label_left, label_top, label_width, label_height)
        self.parameter_buttons.append(("label", label_rect, label_surface))

        button_width = 100
        button_height = 50
        total_width = len(options) * button_width + (len(options) - 1) * 20
        start_x = (self.screen.get_width() - total_width) // 2
        buttons_start_y = label_top + label_height + 10
        for i, option in enumerate(options):
            x = start_x + i * (button_width + 20)
            rect = pygame.Rect(x, buttons_start_y, button_width, button_height)
            self.parameter_buttons.append((str(option), rect))

    def update(self):
        for btn_name in self.button_scales:
            if self.state == "menu" and self.button_scales[btn_name] < 1.0:
                self.button_scales[btn_name] += self.settings.button_scale_speed
                if self.button_scales[btn_name] > 1.0:
                    self.button_scales[btn_name] = 1.0
            elif self.state != "menu":
                self.button_scales[btn_name] = 0.0

        for opt in ["numbers", "punctuation"]:
            target_color = (
                self.settings.option_enabled_color if (opt == "numbers" and self.settings.numbers_enabled) or
                                                      (opt == "punctuation" and self.settings.punctuation_enabled)
                else self.settings.option_disabled_color)
            for i in range(3):
                diff = target_color[i] - self.option_colors[opt][i]
                if abs(diff) > 1:
                    self.option_colors[opt][i] += diff * self.settings.color_transition_speed

        self.cursor_alpha = 255 if (pygame.time.get_ticks() % 1000 < 500) else max(0, self.cursor_alpha - 10)

        if self.state == "parameter_selection":
            self.panel_y = self.panel_target_y

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game":
            self.draw_game()
        elif self.state == "custom_setup":
            self.draw_custom_setup()
        elif self.state == "parameter_selection":
            self.draw_parameter_selection()

    def draw_menu(self):
        for mode_name, rect in self.mode_buttons:
            bg_color = self.settings.menu_button_color
            if rect.collidepoint(pygame.mouse.get_pos()):
                bg_color = self.settings.menu_button_hover_color
            scale = self.button_scales[mode_name]
            scaled_rect = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))
            pygame.draw.rect(self.screen, bg_color, scaled_rect, border_radius=8)
            icon = self.icons.get(mode_name)
            if icon:
                text_surface = self.menu_font.render(mode_name.upper(), True, self.settings.menu_button_text_color)
                total_width = icon.get_width() + 10 + text_surface.get_width()
                start_x = scaled_rect.left + (scaled_rect.width - total_width) // 2
                icon_rect = icon.get_rect(left=start_x, centery=scaled_rect.centery)
                self.screen.blit(icon, icon_rect)
                text_rect = text_surface.get_rect(left=icon_rect.right + 10, centery=scaled_rect.centery)
                self.screen.blit(text_surface, text_rect)

        for option_name, rect in self.option_buttons:
            bg_color = tuple(int(c) for c in self.option_colors[option_name])
            scale = self.button_scales[option_name]
            scaled_rect = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))
            pygame.draw.rect(self.screen, bg_color, scaled_rect, border_radius=8)
            icon = self.icons.get(option_name)
            if icon:
                text_surface = self.menu_font.render(option_name.upper(), True, self.settings.menu_button_text_color)
                total_width = icon.get_width() + 10 + text_surface.get_width()
                start_x = scaled_rect.left + (scaled_rect.width - total_width) // 2
                icon_rect = icon.get_rect(left=start_x, centery=scaled_rect.centery)
                self.screen.blit(icon, icon_rect)
                text_rect = text_surface.get_rect(left=icon_rect.right + 10, centery=scaled_rect.centery)
                self.screen.blit(text_surface, text_rect)

        if self.exit_button:
            rect = self.exit_button[1]
            bg_color = self.settings.menu_button_color
            if rect.collidepoint(pygame.mouse.get_pos()):
                bg_color = self.settings.menu_button_hover_color
            scale = self.button_scales["exit"]
            scaled_rect = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))
            pygame.draw.rect(self.screen, bg_color, scaled_rect, border_radius=8)
            text_surface = self.menu_font.render("EXIT", True, self.settings.menu_button_text_color)
            if self.icons.get("exit"):
                icon = self.icons.get("exit")
                total_width = icon.get_width() + 10 + text_surface.get_width()
                start_x = scaled_rect.left + (scaled_rect.width - total_width) // 2
                icon_rect = icon.get_rect(left=start_x, centery=scaled_rect.centery)
                self.screen.blit(icon, icon_rect)
                text_rect = text_surface.get_rect(left=icon_rect.right + 10, centery=scaled_rect.centery)
            else:
                text_rect = text_surface.get_rect(center=scaled_rect.center)
            self.screen.blit(text_surface, text_rect)

    def draw_game(self):
        mode = self.game_manager.selected_mode
        if not mode:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        space_width = self.font.render(" ", True, self.settings.text_color).get_width()
        max_line_width = screen_width - 100
        lines = []
        current_line = []
        current_line_width = 0

        for i, word in enumerate(mode.words):
            if i < mode.current_word_index:
                color = self.settings.correct_color if mode.finished_word_results[i] else self.settings.error_color
                surfaces = [self.font.render(c, True, color) for c in word]
            elif i == mode.current_word_index:
                surfaces = []
                for j, c in enumerate(word):
                    if j < len(mode.user_input):
                        color = self.settings.correct_color if mode.user_input[j] == c else self.settings.error_color
                    else:
                        color = self.settings.text_color
                    surfaces.append(self.font.render(c, True, color))
            else:
                surfaces = [self.font.render(c, True, self.settings.text_color) for c in word]

            word_width = sum(s.get_width() for s in surfaces)
            if current_line and current_line_width + space_width + word_width > max_line_width:
                lines.append((current_line, current_line_width))
                current_line = []
                current_line_width = 0
            if current_line:
                current_line_width += space_width
            current_line.append((word, surfaces, i))
            current_line_width += word_width
        if current_line:
            lines.append((current_line, current_line_width))

        total_text_height = len(lines) * (self.settings.font_size + 15)
        start_y = (screen_height - total_text_height) // 2

        for line, line_width in lines:
            start_x = (screen_width - line_width) // 2
            x = start_x
            for word, surfaces, idx in line:
                for surf in surfaces:
                    self.screen.blit(surf, (x, start_y))
                    x += surf.get_width()
                x += space_width
            start_y += self.settings.font_size + 15

        for line, line_width in lines:
            for word, surfaces, idx in line:
                if idx == mode.current_word_index:
                    start_x = (screen_width - line_width) // 2
                    for w, surfs, jdx in line:
                        if jdx == mode.current_word_index:
                            break
                        start_x += sum(s.get_width() for s in surfs) + space_width
                    typed_width = 0
                    current_word = mode.words[mode.current_word_index]
                    for j in range(len(mode.user_input)):
                        if j < len(current_word):
                            ch_surf = self.font.render(current_word[j], True,
                                                       self.settings.correct_color if mode.user_input[j] ==
                                                                                      current_word[
                                                                                          j] else self.settings.error_color)
                            typed_width += ch_surf.get_width()
                    cursor_x = start_x + typed_width
                    line_index = lines.index((line, line_width))
                    cursor_y = (screen_height - total_text_height) // 2 + line_index * (self.settings.font_size + 15)
                    cursor_surface = pygame.Surface((3, self.settings.font_size), pygame.SRCALPHA)
                    cursor_surface.fill((self.settings.text_color[0], self.settings.text_color[1],
                                         self.settings.text_color[2], self.cursor_alpha))
                    self.screen.blit(cursor_surface, (cursor_x, cursor_y))
                    break

        if hasattr(mode, 'time_limit') and mode.time_limit > 0:
            remaining_time = max(0, mode.time_limit - mode.time_elapsed)
            timer_text = f"Time left: {int(remaining_time)}s"
            timer_surface = self.menu_font.render(timer_text, True, self.settings.text_color)
            self.screen.blit(timer_surface, (screen_width - 200, 20))

        if hasattr(mode, 'word_count') and mode.word_count > 0:
            remaining_words = max(0, mode.word_count - mode.current_word_index)
            words_text = f"Words left: {remaining_words}"
            words_surface = self.menu_font.render(words_text, True, self.settings.text_color)
            self.screen.blit(words_surface, (screen_width - 200, 50))

        restart_text = "Shift + Enter для перезапуска"
        restart_surface = self.menu_font.render(restart_text, True, (100, 100, 100))
        self.screen.blit(restart_surface, (50, screen_height - 50))
        esc_text = "Нажмите ESC для выхода в меню"
        esc_surface = self.menu_font.render(esc_text, True, (100, 100, 100))
        self.screen.blit(esc_surface, (50, screen_height - 100))

    def draw_custom_setup(self):
        prompt_text = "Введите настройки для Custom Mode (например: time=30 words=50) и нажмите Enter:"
        prompt_surface = self.menu_font.render(prompt_text, True, self.settings.text_color)
        self.screen.blit(prompt_surface, (50, 150))
        input_surface = self.menu_font.render(self.input_text, True, (255, 255, 0))
        self.screen.blit(input_surface, (50, 220))

    def draw_parameter_selection(self):
        panel_rect = pygame.Rect(0, self.panel_y, self.screen.get_width(), 200)
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect, border_radius=8)

        for btn in self.parameter_buttons:
            if btn[0] == "label":
                self.screen.blit(btn[2], (btn[1].left, self.panel_y + btn[1].top))
            else:
                rect = btn[1]
                actual_rect = rect.copy()
                actual_rect.y += self.panel_y
                bg_color = self.settings.menu_button_color
                if actual_rect.collidepoint(pygame.mouse.get_pos()):
                    bg_color = self.settings.menu_button_hover_color
                pygame.draw.rect(self.screen, bg_color, actual_rect, border_radius=8)
                text_surface = self.menu_font.render(btn[0], True, self.settings.menu_button_text_color)
                text_rect = text_surface.get_rect(center=actual_rect.center)
                self.screen.blit(text_surface, text_rect)

    def parse_custom_input(self):
        time_limit = 0
        word_count = 0
        parts = self.input_text.split()
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                try:
                    if key == "time":
                        time_limit = int(value)
                    elif key == "words":
                        word_count = int(value)
                except ValueError:
                    pass
        self.game_manager.set_mode("custom", time_limit, word_count)
        self.input_text = ""
