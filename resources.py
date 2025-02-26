import os

import pygame


def load_image(path):
    if not os.path.exists(path):
        print(f"Не удалось найти файл изображения: {path}")
        return None
    image = pygame.image.load(path)
    return image.convert_alpha()


def load_font(path, size):
    if not os.path.exists(path):
        print(f"Не удалось найти файл шрифта: {path}")
        return pygame.font.SysFont(None, size)
    return pygame.font.Font(path, size)


def load_wordlist(path):
    if not os.path.exists(path):
        print(f"Не удалось найти файл со словами: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        words = f.read().split()
    return words


def load_quote_list(path):
    if not os.path.exists(path):
        print(f"Не удалось найти файл с цитатами: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        quotes = f.readlines()
    quotes = [q.strip() for q in quotes if q.strip()]
    return quotes
