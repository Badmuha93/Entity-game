import pygame
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_font
from effects import apply_full_effects, create_vignette, add_pixel_glitch
from settings import TEXTURES, SOUNDS, CAM_ORDER, ZONES, PAN_SPEED, GRID_SIZE, PAN_ACC, PAN_MAX, PAN_DURATION, PAN_PAD, ZONE_PAD, BUTTON_SIZE, TRANSITION_SPEED

BLACK = (0, 0, 0)

computer_cache = {"image": None, "vignette": None, "map_w": 0, "map_h": 0, "loaded": False}
camera_overlay = None


def load_camera_image(name, default=TEXTURES["background"]):
    path = default if name == "SERVER" else f"assets/textures/cameras/{name}.jpg"
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert()
    except:
        pass
    return None


def load_camera_overlay():
    global camera_overlay
    if camera_overlay is not None:
        return camera_overlay
    try:
        if os.path.exists(TEXTURES["camera_overlay"]):
            camera_overlay = pygame.image.load(TEXTURES["camera_overlay"]).convert_alpha()
        else:
            camera_overlay = None
    except:
        camera_overlay = None
    return camera_overlay


def load_computer_interface(screen):
    if computer_cache["loaded"]:
        return
        
    W, H = screen.get_size()
    img = pygame.image.load(TEXTURES["map"]).convert_alpha()
    if not img:
        img = pygame.Surface((W, H))
        img.fill((30, 30, 50))
        font = load_font(int(H * 0.05))
        txt = font.render("MAP (locat.png missing)", True, (255, 255, 255))
        img.blit(txt, txt.get_rect(center=(W // 2, H // 2)))
        
    computer_cache.update({
        "image": img,
        "vignette": create_vignette(W, H),
        "map_w": img.get_width(),
        "map_h": img.get_height(),
        "loaded": True
    })


def run_computer_interface(screen, sound_manager=None):
    if not computer_cache["loaded"]:
        load_computer_interface(screen)

    overlay = load_camera_overlay()
    if sound_manager is None:
        from sound_manager import SoundManager
        sound_manager = SoundManager()
        if os.path.exists(SOUNDS["monitor_close"]):
            sound_manager.load("monitorclose", SOUNDS["monitor_close"])

    W, H = screen.get_size()
    clock = pygame.time.Clock()

    computer_img = computer_cache["image"]
    vignette = computer_cache["vignette"]
    map_w, map_h = computer_cache["map_w"], computer_cache["map_h"]

    min_x, max_x = -PAN_PAD, map_w + PAN_PAD
    min_y, max_y = -PAN_PAD, map_h + PAN_PAD

    world_x = max(min_x, min(max_x - W, map_w // 2 - W // 2))
    world_y = max(min_y, min(max_y - H, map_h // 2 - H // 2))
    target_x, target_y = world_x, world_y

    ZONE_FONT = load_font(int(H * 0.03))

    cam_mode = False
    cur_image = None
    cur_scaled = None
    cur_name = None
    cam_index = 0
    pending_img, pending_idx = None, None

    trans_active, trans_alpha, trans_dir = False, 0, 0
    trans_pixels, pixel_timer = False, 0

    exiting_camera = False

    def make_action(name):
        return lambda: open_camera(name, load_camera_image(name))

    zones_with_actions = []
    for z in ZONES:
        zones_with_actions.append({
            "name": z["name"],
            "x": z["x"],
            "y": z["y"],
            "w": z["w"],
            "h": z["h"],
            "action": make_action(z["name"])
        })

    return_to_game = False

    pan_x = pan_v = pan_state = pan_timer = 0
    pan_dir = 1
    bg_w = bg_h = left = right = 0

    def open_camera(name, img):
        nonlocal trans_active, trans_dir, trans_alpha, trans_pixels, pixel_timer
        nonlocal pending_img, pending_idx, cur_image, cur_name, cam_mode
        if img is None:
            return
        pending_img = img
        cur_name = name
        pending_idx = CAM_ORDER.index(name) if name in CAM_ORDER else 0
        trans_active, trans_dir, trans_alpha, trans_pixels, pixel_timer = True, 1, 0, True, 5
        cur_image = img

    def switch_camera(delta):
        nonlocal cam_index, trans_active, trans_dir, trans_alpha, trans_pixels, pixel_timer, pending_img, pending_idx, cur_image, cur_name
        if not cam_mode:
            return
        new = (cam_index + delta) % len(CAM_ORDER)
        if new == cam_index:
            return
        new_img = load_camera_image(CAM_ORDER[new])
        if new_img:
            pending_img, pending_idx = new_img, new
            cur_name = CAM_ORDER[new]
            trans_active, trans_dir, trans_alpha, trans_pixels, pixel_timer = True, 1, 0, True, 5
            cur_image = new_img

    while True:
        mouse_click = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_click = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    if sound_manager:
                        sound_manager.play("monitorclose")
                    trans_active = True
                    trans_dir = 1
                    trans_alpha = 0
                    trans_pixels = True
                    pixel_timer = 10
                    while trans_active:
                        if trans_dir == 1:
                            trans_alpha += TRANSITION_SPEED
                            if trans_alpha >= 255:
                                trans_alpha = 255
                                trans_active = False
                                trans_pixels = False
                        if trans_alpha > 0:
                            overlay_surf = pygame.Surface((W, H))
                            overlay_surf.set_alpha(trans_alpha)
                            overlay_surf.fill(BLACK)
                            screen.blit(overlay_surf, (0, 0))
                            if trans_pixels:
                                current_pixel_size = 20 + (5 - pixel_timer) // 2 if pixel_timer else 20
                                current_pixel_size = max(8, min(40, current_pixel_size))
                                glitch_surf = add_pixel_glitch(screen, current_pixel_size, 180)
                                screen.blit(glitch_surf, (0, 0))
                        pygame.display.flip()
                        clock.tick(60)
                        if trans_pixels:
                            pixel_timer -= 1
                            if pixel_timer <= 0:
                                trans_pixels = False
                    return_to_game = True
                if e.key == pygame.K_e and cam_mode and not trans_active and not exiting_camera:
                    trans_active = True
                    trans_dir = 1
                    trans_alpha = 0
                    trans_pixels = True
                    pixel_timer = 5
                    exiting_camera = True
                if cam_mode:
                    if e.key == pygame.K_d:
                        switch_camera(1)
                    elif e.key == pygame.K_a:
                        switch_camera(-1)

        mx, my = pygame.mouse.get_pos()

        if exiting_camera and trans_active:
            if trans_dir == 1:
                trans_alpha += TRANSITION_SPEED
                if trans_alpha >= 255:
                    trans_alpha = 255
                    cam_mode = False
                    cur_image = None
                    cur_scaled = None
                    pending_img = None
                    trans_dir = -1
                    trans_pixels = True
                    pixel_timer = 5
            else:
                trans_alpha -= TRANSITION_SPEED
                if trans_alpha <= 0:
                    trans_alpha = 0
                    trans_active = False
                    trans_pixels = False
                    exiting_camera = False
            
            overlay_surf = pygame.Surface((W, H))
            overlay_surf.set_alpha(trans_alpha)
            overlay_surf.fill(BLACK)
            screen.blit(overlay_surf, (0, 0))
            if trans_pixels:
                current_pixel_size = 20 + (5 - pixel_timer) // 2 if pixel_timer else 20
                current_pixel_size = max(8, min(40, current_pixel_size))
                glitch_surf = add_pixel_glitch(screen, current_pixel_size, 180)
                screen.blit(glitch_surf, (0, 0))
            
            pygame.display.flip()
            clock.tick(60)
            continue

        if trans_active and not exiting_camera:
            if trans_dir == 1:
                trans_alpha += TRANSITION_SPEED
                if trans_alpha >= 255:
                    trans_alpha = 255
                    trans_active = False
                    trans_pixels = False
                    if pending_img is not None:
                        cur_image = pending_img
                        cam_index = pending_idx
                        pending_img = pending_idx = None
                        bg_w, bg_h = int(W * 1.5), int(H * 1.5)
                        cur_scaled = pygame.transform.scale(cur_image, (bg_w, bg_h))
                        left, right = 0, bg_w - W
                        pan_x, pan_v, pan_state, pan_timer, pan_dir = right // 2, 0, 0, 0, 1
                        cam_mode = True
                    trans_dir, trans_alpha, trans_pixels, pixel_timer = -1, 255, True, 5
                    trans_active = True
            else:
                trans_alpha -= TRANSITION_SPEED
                if trans_alpha <= 0:
                    trans_alpha = 0
                    trans_active = False
                    trans_pixels = False
            if trans_pixels:
                pixel_timer -= 1
                if pixel_timer <= 0:
                    trans_pixels = False

        if not cam_mode and not trans_active:
            edge = W * 0.2
            if mx < edge:
                target_x -= PAN_SPEED * ((edge - mx) / edge)
            elif mx > W - edge:
                target_x += PAN_SPEED * ((mx - (W - edge)) / edge)
            if my < edge:
                target_y -= PAN_SPEED * ((edge - my) / edge)
            elif my > H - edge:
                target_y += PAN_SPEED * ((my - (H - edge)) / edge)
            target_x = max(min_x, min(max_x - W, target_x))
            target_y = max(min_y, min(max_y - H, target_y))
            world_x += (target_x - world_x) * 0.1
            world_y += (target_y - world_y) * 0.1
            world_x = max(min_x, min(max_x - W, world_x))
            world_y = max(min_y, min(max_y - H, world_y))

        if not cam_mode:
            surf = pygame.Surface((W, H))
            surf.fill(BLACK)

            ox, oy = world_x % GRID_SIZE, world_y % GRID_SIZE
            start_x = -GRID_SIZE + int(ox)
            start_y = -GRID_SIZE + int(oy)
            for x in range(start_x, W + GRID_SIZE, GRID_SIZE):
                pygame.draw.line(surf, (40, 40, 40), (x, 0), (x, H), 1)
            for y in range(start_y, H + GRID_SIZE, GRID_SIZE):
                pygame.draw.line(surf, (40, 40, 40), (0, y), (W, y), 1)

            dx, dy = -world_x, -world_y
            surf.blit(computer_img, (dx, dy))

            for z in zones_with_actions:
                cx = z["x"] + z["w"] // 2
                cy = z["y"] + z["h"] // 2
                rect = pygame.Rect(dx + z["x"] - ZONE_PAD, dy + z["y"] - ZONE_PAD,
                                   z["w"] + ZONE_PAD * 2, z["h"] + ZONE_PAD * 2)
                hover = rect.collidepoint(mx, my)
                col = (180, 180, 180) if hover else (255, 255, 255)
                if hover and mouse_click:
                    z["action"]()
                txt = ZONE_FONT.render(z["name"], True, col)
                surf.blit(txt, txt.get_rect(center=(dx + cx, dy + cy)))

            btn_rect = pygame.Rect(W // 2 - BUTTON_SIZE // 2, H - 90, BUTTON_SIZE, BUTTON_SIZE)
            hover_x = btn_rect.collidepoint(mx, my)
            pygame.draw.rect(surf, BLACK, btn_rect)
            pygame.draw.rect(surf, (150, 150, 150) if hover_x else (100, 100, 100), btn_rect, 3 if hover_x else 2)
            close_col = (180, 180, 180) if hover_x else (255, 255, 255)
            close_font = load_font(int(BUTTON_SIZE * 0.7))
            close_txt = close_font.render("X", True, close_col)
            surf.blit(close_txt, close_txt.get_rect(center=btn_rect.center))
            if hover_x and mouse_click:
                if sound_manager:
                    sound_manager.play("monitorclose")
                return_to_game = True

            final = apply_full_effects(surf, vignette, True, False, computer_img)
            screen.blit(final, (0, 0))

        if cam_mode and cur_scaled is not None and not trans_active:
            if pan_state == 0:
                pan_v += PAN_ACC if pan_dir == 1 else -PAN_ACC
                pan_v = max(-PAN_MAX, min(PAN_MAX, pan_v))
                pan_x += pan_v
                if pan_x >= right:
                    pan_x, pan_v, pan_state, pan_timer = right, 0, 2, 0
                elif pan_x <= left:
                    pan_x, pan_v, pan_state, pan_timer = left, 0, 1, 0
            elif pan_state in (1, 2):
                pan_timer += 1
                if pan_timer >= PAN_DURATION:
                    pan_state, pan_dir, pan_v = 0, (1 if pan_state == 1 else -1), 0

            cam_surf = pygame.Surface((W, H))
            cam_surf.fill(BLACK)
            cam_surf.blit(cur_scaled, (-int(pan_x), 0))

            if overlay:
                cam_surf.blit(pygame.transform.scale(overlay, (W, H)), (0, 0))

            name = cur_name if cur_name else CAM_ORDER[cam_index]
            try:
                name_font = pygame.font.Font("assets/fonts/BlackOpsOne-Regular.ttf", int(H * 0.06))
            except:
                name_font = pygame.font.Font(None, int(H * 0.06))
            name_txt = name_font.render(name, True, (255, 255, 255))
            shadow = name_font.render(name, True, BLACK)
            cam_surf.blit(shadow, shadow.get_rect(center=(W // 2 + 2, H - 80 + 2)))
            cam_surf.blit(name_txt, name_txt.get_rect(center=(W // 2, H - 80)))

            final_cam = apply_full_effects(cam_surf, None, True, False)
            screen.blit(final_cam, (0, 0))

        if trans_active and trans_alpha > 0 and not exiting_camera:
            overlay_surf = pygame.Surface((W, H))
            overlay_surf.set_alpha(trans_alpha)
            overlay_surf.fill(BLACK)
            screen.blit(overlay_surf, (0, 0))
            if trans_pixels:
                current_pixel_size = 20 + (5 - pixel_timer) // 2 if pixel_timer else 20
                current_pixel_size = max(8, min(40, current_pixel_size))
                glitch_surf = add_pixel_glitch(screen, current_pixel_size, 180)
                screen.blit(glitch_surf, (0, 0))

        if return_to_game:
            return True

        pygame.display.flip()
        clock.tick(60)