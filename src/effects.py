import pygame
import random
import math

BLACK = (0, 0, 0)

_vignette_cache = {}


def _get_vignette(w, h, intensity=1.0):
    key = (w, h, intensity)
    if key not in _vignette_cache:
        vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        for x in range(w):
            dx = (x - cx) / cx if cx != 0 else 0
            for y in range(h):
                dy = (y - cy) / cy if cy != 0 else 0
                dist = (dx * dx + dy * dy) ** 0.5
                alpha = min(255, int(255 * max(0, (dist - 0.3) / 0.7 * intensity)))
                vignette.set_at((x, y), (0, 0, 0, alpha))
        _vignette_cache[key] = vignette
    return _vignette_cache[key].copy()


def add_flickering_light(screen):
    t = pygame.time.get_ticks() * 0.003
    brightness = 0.7 + math.sin(t) * 0.15 + random.uniform(-0.05, 0.05)
    brightness = max(0.4, min(1.0, brightness))
    if brightness < 0.95:
        dark = pygame.Surface(screen.get_size())
        dark.set_alpha(int((1 - brightness) * 200))
        dark.fill(BLACK)
        screen.blit(dark, (0, 0))


def add_vhs_effect(screen):
    w, h = screen.get_size()
    if random.random() < 0.05:
        for _ in range(random.randint(5, 15)):
            y = random.randint(0, h)
            pygame.draw.rect(screen, BLACK, (0, y, w, random.randint(2, 8)))
    if random.random() < 0.03:
        shifted = screen.copy()
        offset = random.randint(-5, 5)
        screen.fill(BLACK)
        screen.blit(shifted, (offset, 0))


def add_pixel_glitch(surface, block_size=20, intensity=180):
    glitch = pygame.Surface(surface.get_size())
    glitch.set_alpha(intensity)
    w, h = surface.get_width(), surface.get_height()
    for _ in range(random.randint(30, 80)):
        x = random.randint(0, w - block_size)
        y = random.randint(0, h - block_size)
        color = random.choice([BLACK, (30, 30, 30), (50, 50, 50), (80, 80, 80), (120, 120, 120)])
        pygame.draw.rect(glitch, color, (x, y, block_size, block_size))
    return glitch


def create_vignette(w, h, intensity=0.5):
    return _get_vignette(w, h, 0.8)


def apply_full_effects(surface, vignette_param=None, crt_enabled=True, glitch_enabled=False, computer_image=None, **kwargs):
    w, h = surface.get_size()

    if random.random() < 0.05:
        for _ in range(random.randint(5, 15)):
            y = random.randint(0, h)
            pygame.draw.rect(surface, BLACK, (0, y, w, random.randint(2, 8)))

    if random.random() < 0.03:
        shifted = surface.copy()
        offset = random.randint(-5, 5)
        surface.fill(BLACK)
        surface.blit(shifted, (offset, 0))

    if crt_enabled:
        low = pygame.transform.scale(surface, (w // 3, h // 3))
        surface = pygame.transform.scale(low, (w, h))
        pos = (pygame.time.get_ticks() // 50) % 6
        for y in range(pos, h, 6):
            pygame.draw.line(surface, BLACK, (0, y), (w, y), 1)

    if vignette_param is not None:
        surface.blit(vignette_param, (0, 0))
    else:
        vignette = _get_vignette(w, h, 0.8)
        surface.blit(vignette, (0, 0))

    return surface