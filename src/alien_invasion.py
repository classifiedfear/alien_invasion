import sys
from pathlib import Path
from time import sleep
import json

import pygame

from setting import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion():
    """класс для управления ресурсами и поведением игры"""
    def __init__(self):
        """Инициализирует игру и создаёт игровые ресурсы."""
        pygame.init()
        self.settings = Settings()
        #вызов pygame.display.set_mode()
#создает окно, в котором прорисовываются все графические элементы игры. Аргумент (1200, 800) представляет собой кортеж, определяющий размеры игрового 
#окна. 
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(ai_game= self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self._create_fleet()
        self.easy_button = Button(self, "Easy", easy = True)
        self.medium_button = Button(self, "Medium", medium= True)
        self.hard_button = Button(self, "Hard", hard=True)
        self.path = Path('../save record/record.json')
        self._load_record(path=self.path)

    def run_game(self):
         """Запуск основного цикла игры"""
         while True:
            """Отслеживание событий клавиатуры и мыши"""
            self._check_events()
            if self.stats.ganm_active:
                self.ship.update()
                self._update_aliens()
                self._update_bullets()
            self._update_screen()
            self.clock.tick(60)
            

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
        self._check_bullet_alien_collision()
    

    def _check_bullet_alien_collision(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        self._start_new_level()
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()


    def _start_new_level(self):
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
            

    def _check_events(self):
        """Обрабатывает нажатия клавиш и события мыши."""
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)


    def _check_keydown_events(self, event):
        """реагирует на нажатие клавиш"""
        if event.key == pygame.K_d:
            self.ship.moving_right = True
        elif event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            self._save_record(record=self.stats.high_score, path=self.path)
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            pygame.mouse.set_visible(True)
            self.stats.ganm_active = False
            

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _check_keyup_events(self, event):   
        """реагирует на отпускание клавиш"""             
        if event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_a:
            self.ship.moving_left = False
                    
    
    def _update_screen(self):
        # При каждом проходе цикла перерисовывается экран
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.stats.ganm_active:
            self.easy_button.draw_button()
            self.medium_button.draw_button()
            self.hard_button.draw_button()
        """Отображение последнего прорисованного экрана."""
        pygame.display.flip()


    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 4 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height 


    def _create_alien(self, x_position, y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)


    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        # Проверка коллизий "пришелец — корабль"
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Проверить, добрались ли пришельцы до нижнего края экрана.
        self._check_aliens_bottom()


    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    

    def _change_fleet_direction(self):
        """Опускает весь флот и меняет направление флота."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        

    def _ship_hit(self):
        """Обрабатывает столкновение корабля с пришельцем."""
        # Уменьшение ships_left.
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Очистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()
            # Создание нового флота и размещение корабля в центре.
            self._create_fleet()
            self.ship.center_ship()
            # Пауза.
            sleep(0.5)
        else: 
            self.stats.ganm_active= False
            pygame.mouse.set_visible(True)


    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break


    def _check_play_button(self, mouse_pos):
        """Запускает новую игру при нажатии кнопки Play."""
        button_easy_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        button_medium_clicked = self.medium_button.rect.collidepoint(mouse_pos)
        button_hard_clicked = self.hard_button.rect.collidepoint(mouse_pos)
        if button_easy_clicked and not self.stats.ganm_active:
            self._check_difficulty(easy=True)
        if button_medium_clicked and not self.stats.ganm_active:  
            self._check_difficulty(medium=True)
        if button_hard_clicked and not self.stats.ganm_active:
            self._check_difficulty(hard=True)


    def _check_difficulty(self, easy=False, medium=False, hard=False):
        if easy:
            self.settings.initialize_dynamic_settings()
            self.settings.speedup_scale += 0.1
            self.start_game()
        if medium:
            self.settings.initialize_dynamic_settings()
            self.settings.speedup_scale += 0.2
            self.start_game()
        if hard:
            self.settings.initialize_dynamic_settings()
            self.settings.speedup_scale += 0.3
            self.start_game()


    def start_game(self):
        # Сброс игровой статистики.
            self.stats.reset_stats()
            self.stats.ganm_active = True
            self.sb.prep_image()
        # Очистка списков пришельцев и снарядов.
            self.aliens.empty()
            self.bullets.empty()

        #Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)


    def _save_record(self,record,path):
        contents = json.dumps(record)
        path.write_text(contents)


    def _load_record(self,path):
        if self.path.exists():
            contents = path.read_text()
            record = json.loads(contents)
            self.stats.high_score = record
            self.sb.prep_high_score()
            

if __name__=="__main__":
    #создание экземлпяра и запуск игры.
    ai = AlienInvasion()
    ai.run_game()