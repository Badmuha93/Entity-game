import pygame
import random
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_background
from computer_menu import run_computer_interface
from sound_manager import SoundManager
from effects import create_vignette, add_pixel_glitch
from settings import SOUNDS, PLAYER_MENU_BG, PLAYER_MENU_HOVER, FADE_DURATION

BLACK = (0, 0, 0)


def run_game(screen, sound_manager=None):
    WIDTH, HEIGHT = screen.get_size()
    clock = pygame.time.Clock()

    if sound_manager is None:
        sound_manager = SoundManager()
        try:
            sound_manager.load("monitoropen", SOUNDS["monitor_open"])
            sound_manager.load("monitorclose", SOUNDS["monitor_close"])
        except:
            pass

    def load_bg(path, fallback_color=(50, 0, 0)):
        img = load_background(path, WIDTH, HEIGHT)
        return img if img else pygame.Surface((WIDTH, HEIGHT)).fill(fallback_color)

    bg_normal_original = load_bg(PLAYER_MENU_BG, BLACK)
    hover_originals = [load_bg(PLAYER_MENU_HOVER.format(i), (50, 0, 0)) for i in range(2, 6)]

    PAN_RANGE = 0.5
    bg_width = int(WIDTH * (1 + PAN_RANGE))
    bg_height = int(HEIGHT * (1 + PAN_RANGE))

    bg_normal = pygame.transform.scale(bg_normal_original, (bg_width, bg_height))
    hover_frames = [pygame.transform.scale(orig, (bg_width, bg_height)) for orig in hover_originals]

    max_offset_x = bg_width - WIDTH
    center_offset_x = max_offset_x // 2
    max_offset_y = bg_height - HEIGHT
    center_offset_y = max_offset_y // 2

    current_offset_x, current_offset_y = center_offset_x, center_offset_y
    computer_world_x, computer_world_y = bg_width // 2, bg_height // 2
    computer_width, computer_height = 300, 200

    anim_idx, anim_timer, anim_delay, was_hover = 0, 0, 6, False

    computer_open = False
    transitioning = False
    trans_alpha, trans_dir = 0, 0
    trans_pixels, pixel_timer, pixel_size = False, 0, 20

    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill(BLACK)
    fade_start = pygame.time.get_ticks()
    fade_duration = FADE_DURATION

    game_running = True
    edge_zone = WIDTH * 0.25
    max_speed, inertia = 15, 0.15

    vignette = create_vignette(WIDTH, HEIGHT)

    particles = [{
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'vx': random.uniform(-0.2, 0.2),
        'vy': random.uniform(-0.2, 0.2),
        'alpha': random.randint(30, 100)
    } for _ in range(80)]

    breath, breath_dir, breath_speed = 0, 1, 0.3
    flicker_state, flicker_dur = 0, 0
    sway_amp, sway_speed = 4, 0.8

    def start_transition(direction):
        nonlocal transitioning, trans_dir, trans_alpha, trans_pixels, pixel_timer
        transitioning, trans_dir, trans_alpha, trans_pixels, pixel_timer = True, direction, 0, True, 15

    while game_running:
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not computer_open:
                game_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if mouse_clicked and not computer_open and not transitioning:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            comp_screen_x = computer_world_x - current_offset_x
            comp_screen_y = computer_world_y - current_offset_y
            comp_rect = pygame.Rect(
                comp_screen_x - computer_width // 2,
                comp_screen_y - computer_height // 2,
                computer_width, computer_height
            )
            if comp_rect.collidepoint(mouse_x, mouse_y):
                if sound_manager:
                    sound_manager.play("monitoropen")
                start_transition(1)

        if transitioning:
            if trans_dir == 1:
                trans_alpha += 25
                if trans_alpha >= 255:
                    trans_alpha, transitioning, trans_pixels = 255, False, False
                    computer_open = True
            else:
                trans_alpha -= 25
                if trans_alpha <= 0:
                    trans_alpha, transitioning, trans_pixels = 0, False, False
                    computer_open = False
        if trans_pixels:
            pixel_timer -= 1
            if pixel_timer <= 0:
                trans_pixels = False

        if computer_open:
            result = run_computer_interface(screen, sound_manager)
            if result:
                computer_open = False

        mouse_x, _ = pygame.mouse.get_pos()
        if mouse_x < edge_zone:
            target = 0
        elif mouse_x > WIDTH - edge_zone:
            target = max_offset_x
        else:
            target = center_offset_x

        diff = target - current_offset_x
        if abs(diff) > 0.5:
            speed = max(-max_speed, min(max_speed, diff * inertia))
            current_offset_x += speed
            if (target - current_offset_x) * diff < 0:
                current_offset_x = target
        else:
            current_offset_x = target
        current_offset_x = max(0, min(max_offset_x, current_offset_x))

        sway = math.sin(pygame.time.get_ticks() * 0.002 * sway_speed) * sway_amp
        final_y = max(0, min(max_offset_y, center_offset_y + sway))

        comp_screen_x = computer_world_x - current_offset_x
        comp_screen_y = computer_world_y - final_y
        comp_rect = pygame.Rect(
            comp_screen_x - computer_width // 2,
            comp_screen_y - computer_height // 2,
            computer_width, computer_height
        )
        is_hover = comp_rect.collidepoint(pygame.mouse.get_pos())

        if was_hover and not is_hover:
            anim_idx, anim_timer = 0, 0
        was_hover = is_hover

        if is_hover and not computer_open and not transitioning:
            anim_timer += 1
            if anim_timer >= anim_delay:
                anim_timer = 0
                anim_idx = (anim_idx + 1) % len(hover_frames)
            current_bg = hover_frames[anim_idx]
        else:
            current_bg = bg_normal

        screen.blit(current_bg, (-current_offset_x, -final_y))

        for p in particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['x'] < -5:
                p['x'] = WIDTH + 5
            if p['x'] > WIDTH + 5:
                p['x'] = -5
            if p['y'] < -5:
                p['y'] = HEIGHT + 5
            if p['y'] > HEIGHT + 5:
                p['y'] = -5
            if p['alpha'] > 0:
                point = pygame.Surface((2, 2), pygame.SRCALPHA)
                point.fill((255, 255, 255, int(p['alpha'])))
                screen.blit(point, (int(p['x']), int(p['y'])))

        breath += breath_dir * breath_speed
        if breath >= 35:
            breath, breath_dir = 35, -1
        elif breath <= 0:
            breath, breath_dir = 0, 1
        breath_surf = pygame.Surface((WIDTH, HEIGHT))
        breath_surf.set_alpha(breath)
        breath_surf.fill(BLACK)
        screen.blit(breath_surf, (0, 0))

        if flicker_state == 0 and random.random() < 0.005:
            flicker_state, flicker_dur = 1, random.randint(5, 15)
        elif flicker_state == 1:
            flicker_dur -= 1
            if flicker_dur <= 0:
                flicker_state = 0
        if flicker_state == 1:
            dark = pygame.Surface((WIDTH, HEIGHT))
            dark.set_alpha(160)
            dark.fill(BLACK)
            screen.blit(dark, (0, 0))

        screen.blit(vignette, (0, 0))

        if transitioning and trans_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(trans_alpha)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            if trans_pixels:
                size = max(8, min(40, pixel_size + (15 - pixel_timer) // 2))
                glitch = add_pixel_glitch(screen, size, 180)
                screen.blit(glitch, (0, 0))

        elapsed = pygame.time.get_ticks() - fade_start
        if elapsed < fade_duration:
            alpha = int(255 * (1 - elapsed / fade_duration))
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    return True