import pygame.font
from pygame.sprite import Group
from ship import Ship

class Scoreboard():
    """Класс для вывода игровой информации"""
    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.settings = ai_game.settings
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.stats = ai_game.stats
       

        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)
        self.prep_image()

    def prep_image(self):
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self):
        """Преобразует текущий счет в графическое изображение."""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_color, self.settings.bg_color)
        # Вывод счета в правой верхней части экрана.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        rounded_score_high = round(self.stats.high_score, -1)
        score_high_str = "{:,}".format(rounded_score_high)
        self.high_score_image = self.font.render(score_high_str, True, self.text_color, self.settings.bg_color)
        self.score_high_rect = self.high_score_image.get_rect()
        self.score_high_rect.centerx = self.screen_rect.centerx 
        self.score_high_rect.top = self.score_rect.top

    def show_score(self):
        """Выводит счет на экран"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.score_high_rect)
        self.screen.blit(self.level_image, self.level_image_rect)
        self.ships.draw(self.screen)

    def check_high_score(self):
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def prep_level(self):
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str, True, self.text_color, self.settings.bg_color)
        self.level_image_rect = self.level_image.get_rect()
        self.level_image_rect.right = self.screen_rect.right 
        self.level_image_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        self.ships = Group()
        for ship_number in range (self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)
    