class Settings:
    def __init__(self):
        self.fps = 60

        self.bg_color = (20, 20, 20)
        self.text_color = (120, 120, 120)
        self.correct_color = (255, 255, 255)
        self.error_color = (255, 69, 58)
        self.option_enabled_color = (0, 255, 0)
        self.option_disabled_color = (255, 0, 0)

        self.font_path = "assets/fonts/Consolas.ttf"
        self.font_size = 48
        self.menu_font_size = 24

        self.time_modes = [15, 30, 60, 120]
        self.word_modes = [10, 25, 50, 100]
        self.default_time_mode = 30
        self.default_words_mode = 25

        self.numbers_enabled = False
        self.punctuation_enabled = False

        self.icon_paths = {
            "time": "assets/icons/time.png",
            "words": "assets/icons/words.png",
            "quote": "assets/icons/quote.png",
            "zen": "assets/icons/zen.png",
            "numbers": "assets/icons/numbers.png",
            "punctuation": "assets/icons/punctuation.png",
            "language": "assets/icons/language.png",
            "custom": "assets/icons/custom.png",
            "exit": "assets/icons/exit.png"
        }

        self.menu_button_width = 220
        self.menu_button_height = 60
        self.menu_top_offset = 80
        self.menu_horizontal_spacing = 30
        self.menu_vertical_spacing = 30
        self.menu_button_text_color = (255, 255, 255)
        self.menu_button_color = (40, 40, 40)
        self.menu_button_hover_color = (70, 70, 70)

        self.button_scale_speed = 0.1
        self.color_transition_speed = 0.05

        self.quote_source = "data/quotes.txt"
        self.wordlist_path = "data/words.txt"
        self.numbers_path = "data/numbers.txt"
        self.punctuation_path = "data/punctuation.txt"
        self.languages_path = "data/language_words.txt"

        self.max_zen_words = 50
