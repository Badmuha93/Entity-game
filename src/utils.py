import pygame
import os

FONT_PATH = "assets/fonts/BlackOpsOne-Regular.ttf"

def load_font(size):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except:
        return pygame.font.Font(None, size)

def load_background(image_path, width, height):
    try:
        if os.path.exists(image_path):
            background = pygame.image.load(image_path)
            background = pygame.transform.scale(background, (width, height))
            return background
        else:
            return None
    except Exception:
        return None

def draw_button(screen, text, x, y, w, h, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    is_hover = (x + w > mouse[0] > x and y + h > mouse[1] > y)
    
    if is_hover:
        if click[0] == 1 and action is not None:
            action()
        font = load_font(int(h * 0.5))
        text_surf = font.render(text, True, (150, 150, 150))
    else:
        font = load_font(int(h * 0.5))
        text_surf = font.render(text, True, (255, 255, 255))
    
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surf, text_rect)

def draw_text_button(screen, text, x, y, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    font = load_font(int(pygame.display.get_surface().get_height() * 0.04))
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(x, y))
    
    is_hover = text_rect.collidepoint(mouse)
    
    if is_hover:
        hover_font = load_font(int(pygame.display.get_surface().get_height() * 0.04))
        hover_text = hover_font.render(text, True, (150, 150, 150))
        text_rect = hover_text.get_rect(center=(x, y))
        screen.blit(hover_text, text_rect)
        if click[0] == 1 and action is not None:
            action()
    else:
        screen.blit(text_surf, text_rect)