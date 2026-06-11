import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from effects import _get_vignette
from settings import WINDOW_TITLE, FULLSCREEN


class App:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.info = pygame.display.Info()
        self.width = self.info.current_w
        self.height = self.info.current_h
        self.fullscreen = FULLSCREEN
        
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN if FULLSCREEN else pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        
        self.crt_scanline_pos = 0
        self.current_ui = None
        self.running = True
        self.clock = pygame.time.Clock()
        
    def apply_crt_effect(self):
        w, h = self.screen.get_size()
        low = pygame.transform.scale(self.screen, (w // 3, h // 3))
        self.screen.blit(pygame.transform.scale(low, (w, h)), (0, 0))
        self.crt_scanline_pos = (self.crt_scanline_pos + 2) % 6
        for y in range(self.crt_scanline_pos, h, 6):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (w, y), 1)
    
    def apply_vignette(self):
        vignette = _get_vignette(self.width, self.height, 0.8)
        self.screen.blit(vignette, (0, 0))
    
    def switch_ui(self, ui_class):
        self.current_ui = ui_class(self)
    
    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def run(self):
        from main_menu import MainMenuUI
        self.current_ui = MainMenuUI(self)
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if self.current_ui:
                    self.current_ui.handle_event(event)
            
            if self.current_ui:
                self.current_ui.update()
                self.current_ui.draw(self.screen)
            
            self.apply_vignette()
            self.apply_crt_effect()
            
            pygame.display.flip()
            self.clock.tick(60)