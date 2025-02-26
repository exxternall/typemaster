import random
import time

from resources import load_wordlist, load_quote_list


class GameMode:
    def __init__(self, settings, font):
        self.settings = settings
        self.font = font
        self.words = []
        self.current_word_index = 0
        self.current_char_index = 0
        self.start_time = 0
        self.end_time = 0
        self.time_elapsed = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        self.finished = False
        self.user_input = ""
        self.finished_word_results = []

    def start(self):
        self.current_word_index = 0
        self.current_char_index = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        self.finished = False
        self.end_time = 0
        self.time_elapsed = 0
        self.start_time = 0
        self.user_input = ""
        self.finished_word_results = []
        self.generate_words()

    def generate_words(self):
        pass

    def handle_input(self, char):
        if self.finished:
            return
        if char in (" ", "\r"):
            if self.user_input == "":
                return
            current_word = self.words[self.current_word_index]
            if self.user_input == current_word:
                self.finished_word_results.append(True)
            else:
                self.finished_word_results.append(False)
                if len(self.user_input) < len(current_word):
                    missing = len(current_word) - len(self.user_input)
                    self.errors += missing
                    self.total_chars += missing
            self.current_word_index += 1
            self.user_input = ""
            self.current_char_index = 0
            if self.current_word_index >= len(self.words):
                self.finish()
            return
        self.user_input += char
        if len(self.user_input) == 1 and self.start_time == 0:
            self.start_time = time.time()
        self.total_chars += 1
        current_word = self.words[self.current_word_index]
        if self.current_char_index < len(current_word):
            if char == current_word[self.current_char_index]:
                self.correct_chars += 1
            else:
                self.errors += 1
        else:
            self.errors += 1
        self.current_char_index += 1

    def handle_backspace(self):
        if self.user_input:
            last_index = len(self.user_input) - 1
            last_char = self.user_input[last_index]
            current_word = self.words[self.current_word_index]
            self.user_input = self.user_input[:-1]
            self.current_char_index -= 1
            self.total_chars -= 1
            if self.current_char_index < len(current_word):
                if last_char == current_word[self.current_char_index]:
                    self.correct_chars -= 1
                else:
                    self.errors -= 1

    def update_time(self):
        if not self.finished:
            if self.start_time != 0:
                self.time_elapsed = time.time() - self.start_time
            else:
                self.time_elapsed = 0

    def finish(self):
        self.finished = True
        self.end_time = time.time()
        self.time_elapsed = self.end_time - self.start_time

    def get_stats(self):
        time_in_minutes = self.time_elapsed / 60.0 if self.time_elapsed else 1
        wpm = (self.correct_chars / 5) / time_in_minutes
        accuracy = (self.correct_chars / self.total_chars) * 100 if self.total_chars > 0 else 0
        return {
            "wpm": wpm,
            "accuracy": accuracy,
            "errors": self.errors,
            "time_elapsed": self.time_elapsed,
            "chars_typed": self.total_chars
        }

    def restart_session(self):
        self.start()


class TimeMode(GameMode):
    def __init__(self, settings, font, time_limit=60):
        super().__init__(settings, font)
        self.time_limit = time_limit
        self.words_to_add = 50
        self.max_display_words = 100

    def generate_words(self):
        self.words = self.create_word_list(self.words_to_add)

    def add_more_words(self):
        new_words = self.create_word_list(self.words_to_add)
        self.words += new_words
        if len(self.words) > self.max_display_words:
            self.words = self.words[-self.max_display_words:]

    def create_word_list(self, count):
        wordlist = load_wordlist(self.settings.wordlist_path)
        numbers_list = load_wordlist(self.settings.numbers_path) if self.settings.numbers_enabled else []
        punctuation_list = load_wordlist(self.settings.punctuation_path) if self.settings.punctuation_enabled else []

        if self.settings.numbers_enabled and self.settings.punctuation_enabled:
            num_special_total = (5 * count) // 10
            num_numbers = num_special_total // 2
            num_punctuation = num_special_total - num_numbers
            num_words = count - num_numbers - num_punctuation
        elif self.settings.numbers_enabled:
            num_numbers = (2 * count) // 5
            num_punctuation = 0
            num_words = count - num_numbers
        elif self.settings.punctuation_enabled:
            num_punctuation = (2 * count) // 5
            num_numbers = 0
            num_words = count - num_punctuation
        else:
            num_words = count
            num_numbers = 0
            num_punctuation = 0

        selected_words = random.sample(wordlist, min(len(wordlist), num_words))
        selected_numbers = random.sample(numbers_list, min(len(numbers_list), num_numbers)) if numbers_list else []
        selected_punctuation = random.sample(punctuation_list,
                                             min(len(punctuation_list), num_punctuation)) if punctuation_list else []

        full_list = selected_words + selected_numbers + selected_punctuation
        random.shuffle(full_list)
        return full_list

    def handle_input(self, char):
        super().handle_input(char)
        if len(self.words) - self.current_word_index < 10:
            self.add_more_words()

    def update_time(self):
        super().update_time()
        if self.time_elapsed >= self.time_limit and not self.finished:
            self.finish()


class WordsMode(GameMode):
    def __init__(self, settings, font, word_count=25):
        super().__init__(settings, font)
        self.word_count = word_count

    def generate_words(self):
        self.words = self.create_word_list(self.word_count)

    def create_word_list(self, count):
        wordlist = load_wordlist(self.settings.wordlist_path)
        numbers_list = load_wordlist(self.settings.numbers_path) if self.settings.numbers_enabled else []
        punctuation_list = load_wordlist(self.settings.punctuation_path) if self.settings.punctuation_enabled else []

        if self.settings.numbers_enabled and self.settings.punctuation_enabled:
            num_special_total = (5 * count) // 10
            num_numbers = num_special_total // 2
            num_punctuation = num_special_total - num_numbers
            num_words = count - num_numbers - num_punctuation
        elif self.settings.numbers_enabled:
            num_numbers = (2 * count) // 5
            num_punctuation = 0
            num_words = count - num_numbers
        elif self.settings.punctuation_enabled:
            num_punctuation = (2 * count) // 5
            num_numbers = 0
            num_words = count - num_punctuation
        else:
            num_words = count
            num_numbers = 0
            num_punctuation = 0

        selected_words = random.sample(wordlist, min(len(wordlist), num_words))
        selected_numbers = random.sample(numbers_list, min(len(numbers_list), num_numbers)) if numbers_list else []
        selected_punctuation = random.sample(punctuation_list,
                                             min(len(punctuation_list), num_punctuation)) if punctuation_list else []

        full_list = selected_words + selected_numbers + selected_punctuation
        random.shuffle(full_list)
        return full_list


class QuoteMode(GameMode):
    def generate_words(self):
        quote_list = load_quote_list(self.settings.quote_source)
        if quote_list:
            quote = random.choice(quote_list)
            self.words = quote.split()
        else:
            self.words = ["No", "quotes", "found"]


class ZenMode(GameMode):
    def generate_words(self):
        self.words = self.create_word_list(self.settings.max_zen_words)

    def create_word_list(self, count):
        wordlist = load_wordlist(self.settings.wordlist_path)
        numbers_list = load_wordlist(self.settings.numbers_path) if self.settings.numbers_enabled else []
        punctuation_list = load_wordlist(self.settings.punctuation_path) if self.settings.punctuation_enabled else []

        if self.settings.numbers_enabled and self.settings.punctuation_enabled:
            num_special_total = (5 * count) // 10
            num_numbers = num_special_total // 2
            num_punctuation = num_special_total - num_numbers
            num_words = count - num_numbers - num_punctuation
        elif self.settings.numbers_enabled:
            num_numbers = (2 * count) // 5
            num_punctuation = 0
            num_words = count - num_numbers
        elif self.settings.punctuation_enabled:
            num_punctuation = (2 * count) // 5
            num_numbers = 0
            num_words = count - num_punctuation
        else:
            num_words = count
            num_numbers = 0
            num_punctuation = 0

        selected_words = random.sample(wordlist, min(len(wordlist), num_words))
        selected_numbers = random.sample(numbers_list, min(len(numbers_list), num_numbers)) if numbers_list else []
        selected_punctuation = random.sample(punctuation_list,
                                             min(len(punctuation_list), num_punctuation)) if punctuation_list else []

        full_list = selected_words + selected_numbers + selected_punctuation
        random.shuffle(full_list)
        return full_list


class LanguageMode(GameMode):
    def generate_words(self):
        full_lang = load_wordlist(self.settings.languages_path)
        random.shuffle(full_lang)
        self.words = full_lang[:25]


class CustomMode(GameMode):
    def __init__(self, settings, font, time_limit=0, word_count=0):
        super().__init__(settings, font)
        self.time_limit = time_limit
        self.word_count = word_count
        self.words_to_add = 50 if time_limit > 0 else 0
        self.max_display_words = 100 if time_limit > 0 else word_count

    def generate_words(self):
        if self.word_count > 0:
            self.words = self.create_word_list(self.word_count)
        else:
            self.words = self.create_word_list(self.words_to_add)

    def add_more_words(self):
        new_words = self.create_word_list(self.words_to_add)
        self.words += new_words
        if len(self.words) > self.max_display_words:
            self.words = self.words[-self.max_display_words:]

    def create_word_list(self, count):
        wordlist = load_wordlist(self.settings.wordlist_path)
        numbers_list = load_wordlist(self.settings.numbers_path) if self.settings.numbers_enabled else []
        punctuation_list = load_wordlist(self.settings.punctuation_path) if self.settings.punctuation_enabled else []

        if self.settings.numbers_enabled and self.settings.punctuation_enabled:
            num_special_total = (5 * count) // 10
            num_numbers = num_special_total // 2
            num_punctuation = num_special_total - num_numbers
            num_words = count - num_numbers - num_punctuation
        elif self.settings.numbers_enabled:
            num_numbers = (2 * count) // 5
            num_punctuation = 0
            num_words = count - num_numbers
        elif self.settings.punctuation_enabled:
            num_punctuation = (2 * count) // 5
            num_numbers = 0
            num_words = count - num_punctuation
        else:
            num_words = count
            num_numbers = 0
            num_punctuation = 0

        selected_words = random.sample(wordlist, min(len(wordlist), num_words))
        selected_numbers = random.sample(numbers_list, min(len(numbers_list), num_numbers)) if numbers_list else []
        selected_punctuation = random.sample(punctuation_list,
                                             min(len(punctuation_list), num_punctuation)) if punctuation_list else []

        full_list = selected_words + selected_numbers + selected_punctuation
        random.shuffle(full_list)
        return full_list

    def handle_input(self, char):
        super().handle_input(char)
        if self.time_limit > 0 and len(self.words) - self.current_word_index < 10:
            self.add_more_words()

    def update_time(self):
        super().update_time()
        if 0 < self.time_limit <= self.time_elapsed and not self.finished:
            self.finish()


class GameManager:
    def __init__(self, settings, font):
        self.settings = settings
        self.font = font
        self.current_mode = None
        self.session_finished = False
        self.selected_mode_name = "time"
        self.selected_mode = TimeMode(self.settings, self.font, self.settings.default_time_mode)
        self.selected_mode.start()

    def set_mode(self, mode_name, parameter=None, parameter2=None):
        if mode_name == "time":
            time_limit = parameter if parameter else self.settings.default_time_mode
            self.selected_mode = TimeMode(self.settings, self.font, time_limit)
        elif mode_name == "words":
            word_count = parameter if parameter else self.settings.default_words_mode
            self.selected_mode = WordsMode(self.settings, self.font, word_count)
        elif mode_name == "quote":
            self.selected_mode = QuoteMode(self.settings, self.font)
        elif mode_name == "zen":
            self.selected_mode = ZenMode(self.settings, self.font)
        elif mode_name == "language":
            self.selected_mode = LanguageMode(self.settings, self.font)
        elif mode_name == "custom":
            time_limit = parameter if parameter else 0
            word_count = parameter2 if parameter2 else 0
            self.selected_mode = CustomMode(self.settings, self.font, time_limit, word_count)
        else:
            print(f"Режим {mode_name} не найден.")
            return

        self.selected_mode_name = mode_name
        self.selected_mode.start()
        self.session_finished = False

    def update(self):
        if self.selected_mode:
            self.selected_mode.update_time()
            if self.selected_mode.finished:
                self.session_finished = True

    def handle_input(self, char):
        if self.selected_mode and not self.selected_mode.finished:
            self.selected_mode.handle_input(char)

    def handle_backspace(self):
        if self.selected_mode and not self.selected_mode.finished:
            self.selected_mode.handle_backspace()

    def get_stats(self):
        if self.selected_mode:
            return self.selected_mode.get_stats()
        return {}

    def restart_session(self):
        if self.selected_mode:
            self.selected_mode.start()
            self.session_finished = False
