import pygame
import random
import os

from utils import load_font, load_background, draw_button, draw_text_button
from effects import add_flickering_light, add_vhs_effect, apply_full_effects
from computer_menu import load_computer_interface, computer_cache
from sound_manager import SoundManager
from settings import SOUNDS, TEXTURES, WINDOW_TITLE, DEFAULT_VOLUME, GLITCH_CHANCE, GLITCH_DURATION


class MainMenuUI:
    def __init__(self, app):
        self.app = app
        self.sound_manager = SoundManager()
        
        self.volume = DEFAULT_VOLUME
        self.settings_active = False
        
        self.setup_assets()
        
        self.bg_x = 0
        self.bg_vel = 0
        self.state = 0
        self.pause_timer = 0
        self.bg_acc = 0.02
        self.bg_max = 1
        self.pause_dur = 120
        self.direction = 1
        
        self.glitch_active = False
        self.glitch_timer = 0
        self.cur_glitch = None
        self.glitch_chance = GLITCH_CHANCE
        self.glitch_dur = GLITCH_DURATION
        
    def setup_assets(self):
        if os.path.exists(SOUNDS["menu_music"]):
            self.sound_manager.play_music(SOUNDS["menu_music"], loop=-1)
        
        sound_files = [
            ("monitoropen", SOUNDS["monitor_open"]),
            ("monitorclose", SOUNDS["monitor_close"])
        ]
        for name, path in sound_files:
            if os.path.exists(path):
                self.sound_manager.load(name, path)
        
        self.sound_manager.set_music_volume(self.volume)
        self.sound_manager.set_sfx_volume(self.volume)
        
        load_computer_interface(self.app.screen)
        
        if computer_cache["loaded"] and computer_cache["vignette"] is not None:
            temp_surf = pygame.Surface((self.app.width, self.app.height))
            temp_surf.fill((0, 0, 0))
            apply_full_effects(temp_surf, computer_cache["vignette"], True, False, None)
        
        self.orig_bg = load_background(TEXTURES["background"], self.app.width, self.app.height)
        self.bg = pygame.transform.scale(self.orig_bg, (int(self.app.width * 1.2), self.app.height)) if self.orig_bg else None
        self.bg_w = self.bg.get_width() if self.bg else self.app.width
        self.l_bound, self.r_bound = 0, self.bg_w - self.app.width
        
        self.glitch_bgs = []
        for f in [TEXTURES["glitch_1"], TEXTURES["glitch_2"]]:
            bg = load_background(f, self.app.width, self.app.height)
            if bg:
                self.glitch_bgs.append(bg)
        
    def set_volume(self, volume):
        self.volume = volume
        self.sound_manager.set_music_volume(self.volume)
        self.sound_manager.set_sfx_volume(self.volume)
        
    def transition_effect(self):
        w, h = self.app.screen.get_size()
        for _ in range(5):
            self.app.screen.fill((0, 0, 0))
            pygame.display.flip()
            pygame.time.delay(10)
        for _ in range(8):
            self.app.screen.fill((0, 0, 0))
            for _ in range(random.randint(8, 20)):
                y = random.randint(0, h)
                pygame.draw.line(self.app.screen, (255, 255, 255), (0, y), (w, y), random.randint(2, 6))
            pygame.display.flip()
            pygame.time.delay(15)
        self.app.screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(50)
        
    def start_game(self):
        self.sound_manager.stop_music(300)
        self.transition_effect()
        from game_player import run_game
        if not run_game(self.app.screen, self.sound_manager):
            self.app.quit()
        if os.path.exists(SOUNDS["menu_music"]):
            self.sound_manager.play_music(SOUNDS["menu_music"], loop=-1)
    
    def update_background(self):
        if not self.bg:
            return
            
        if self.state == 0:
            self.bg_vel += (self.bg_acc if self.direction == 1 else -self.bg_acc)
            self.bg_vel = max(-self.bg_max, min(self.bg_max, self.bg_vel))
            self.bg_x += self.bg_vel
            if self.bg_x >= self.r_bound:
                self.bg_x, self.bg_vel, self.state, self.pause_timer = self.r_bound, 0, 2, 0
            elif self.bg_x <= self.l_bound:
                self.bg_x, self.bg_vel, self.state, self.pause_timer = self.l_bound, 0, 1, 0
        elif self.state in (1, 2):
            self.pause_timer += 1
            if self.pause_timer >= self.pause_dur:
                old_state = self.state
                self.state = 0
                self.direction = 1 if old_state == 1 else -1
                self.bg_vel = 0
                
    def draw_background(self):
        skip = False
        if self.glitch_bgs:
            if not self.glitch_active and random.random() < self.glitch_chance:
                self.glitch_active = True
                self.glitch_timer = self.glitch_dur
                self.cur_glitch = random.choice(self.glitch_bgs)
            elif self.glitch_active:
                self.glitch_timer -= 1
                if self.glitch_timer <= 0:
                    self.glitch_active = False
                    self.cur_glitch = None
            if self.glitch_active and self.cur_glitch:
                self.app.screen.blit(pygame.transform.scale(self.cur_glitch, (self.bg_w, self.app.height)), (-int(self.bg_x), 0))
                skip = True
                
        if not skip and self.bg:
            self.app.screen.blit(self.bg, (-int(self.bg_x), 0))
        elif not self.bg:
            self.app.screen.fill((0, 0, 0))
            
    def apply_effects(self):
        add_flickering_light(self.app.screen)
        add_vhs_effect(self.app.screen)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.settings_active:
                mx, my = pygame.mouse.get_pos()
                bw, bh = int(self.app.width * 0.18), int(self.app.height * 0.06)
                bx = self.app.width - bw - 10
                by_start = int(self.app.height * 0.5)
                b_space = int(self.app.height * 0.04)
                
                play_rect = pygame.Rect(bx, by_start, bw, bh)
                settings_rect = pygame.Rect(bx, by_start + bh + b_space, bw, bh)
                exit_rect = pygame.Rect(bx, by_start + (bh + b_space) * 2, bw, bh)
                
                if play_rect.collidepoint(mx, my):
                    self.start_game()
                elif settings_rect.collidepoint(mx, my):
                    self.settings_active = True
                elif exit_rect.collidepoint(mx, my):
                    self.app.quit()
            else:
                mx, my = pygame.mouse.get_pos()
                pw, ph = int(self.app.width * 0.5), int(self.app.height * 0.5)
                px = self.app.width // 2 - pw // 2
                py = self.app.height // 2 - ph // 2
                
                back_rect = pygame.Rect(self.app.width // 2 - 50, py + ph - 60, 100, 40)
                if back_rect.collidepoint(mx, my):
                    self.settings_active = False
                    
    def update(self):
        self.update_background()
        
    def draw(self, screen):
        self.draw_background()
        self.apply_effects()
        
        if not self.settings_active:
            self.draw_main_menu(screen)
        else:
            self.draw_settings_menu(screen)
            
    def draw_main_menu(self, screen):
        bw, bh = int(self.app.width * 0.18), int(self.app.height * 0.06)
        bx = self.app.width - bw - 10
        by_start = int(self.app.height * 0.5)
        b_space = int(self.app.height * 0.04)
        
        font = load_font(int(self.app.height * 0.1))
        title = font.render(WINDOW_TITLE, True, (255, 255, 255))
        tx = self.app.width // 2 - title.get_width() // 2
        ty = int(self.app.height * 0.12)
        
        shadow = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        shadow.blit(font.render(WINDOW_TITLE, True, (0, 0, 0)), (0, 0))
        shadow.set_alpha(50)
        screen.blit(shadow, (tx + 3, ty + 3))
        
        title_surf = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        title_surf.fill((0, 0, 0, 0))
        title_surf.blit(title, (0, 0))
        title_surf.set_alpha(204)
        screen.blit(title_surf, (tx, ty))
        
        draw_button(screen, "PLAY", bx, by_start, bw, bh, None)
        draw_button(screen, "SETTINGS", bx, by_start + bh + b_space, bw, bh, None)
        draw_button(screen, "EXIT", bx, by_start + (bh + b_space) * 2, bw, bh, None)
        
    def draw_settings_menu(self, screen):
        pw, ph = int(self.app.width * 0.5), int(self.app.height * 0.5)
        px = self.app.width // 2 - pw // 2
        py = self.app.height // 2 - ph // 2
        
        panel = pygame.Surface((pw, ph))
        panel.set_alpha(200)
        panel.fill((0, 0, 0))
        screen.blit(panel, (px, py))
        
        settings_font = load_font(int(self.app.height * 0.06))
        title = settings_font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, (self.app.width // 2 - title.get_width() // 2, py + 40))
        
        label_font = load_font(int(self.app.height * 0.04))
        vol_text = label_font.render("Volume", True, (255, 255, 255))
        screen.blit(vol_text, (self.app.width // 2 - vol_text.get_width() // 2, py + 100))
        
        sw, sh = int(self.app.width * 0.3), 10
        sx, sy = self.app.width // 2 - sw // 2, py + 170
        knob_x = max(sx, min(sx + sw, sx + int(self.volume * sw)))
        
        pygame.draw.rect(screen, (80, 80, 80), (sx, sy, sw, sh))
        if knob_x > sx:
            pygame.draw.rect(screen, (150, 150, 150), (sx, sy, knob_x - sx, sh))
        pygame.draw.circle(screen, (200, 200, 200), (knob_x, sy + sh // 2), 12)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, sy + sh // 2), 9)
        
        percent_text = label_font.render(f"{int(self.volume * 100)}%", True, (255, 255, 255))
        screen.blit(percent_text, (self.app.width // 2 - percent_text.get_width() // 2, sy + 35))
        
        draw_text_button(screen, "BACK", self.app.width // 2, py + ph - 60, None)
        
        mx, my = pygame.mouse.get_pos()
        if sx <= mx <= sx + sw and sy - 10 <= my <= sy + sh + 10:
            if pygame.mouse.get_pressed()[0]:
                self.volume = (max(sx, min(sx + sw, mx)) - sx) / sw
                self.set_volume(self.volume)