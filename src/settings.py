import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

SOUNDS = {
    "menu_music": os.path.join(ASSETS_DIR, "sounds/music_menu.mp3"),
    "monitor_open": os.path.join(ASSETS_DIR, "sounds/monitoropen.mp3"),
    "monitor_close": os.path.join(ASSETS_DIR, "sounds/monitorclose.mp3"),
}

TEXTURES = {
    "map": os.path.join(ASSETS_DIR, "textures/others/locat.png"),
    "camera_overlay": os.path.join(ASSETS_DIR, "textures/cameras/camera.png"),
    "background": os.path.join(ASSETS_DIR, "textures/cameras/background.jpg"),
    "glitch_1": os.path.join(ASSETS_DIR, "textures/others/background_he1.png"),
    "glitch_2": os.path.join(ASSETS_DIR, "textures/others/background_he2.png"),
}

PLAYER_MENU_BG = os.path.join(ASSETS_DIR, "textures/player_menu/1_background_game.png")
PLAYER_MENU_HOVER = os.path.join(ASSETS_DIR, "textures/player_menu/{}_background_game.png")

WINDOW_TITLE = "Entity"
FULLSCREEN = True
DEFAULT_VOLUME = 0.5
DEFAULT_CRT_ENABLED = True
DEFAULT_FLICKER_ENABLED = True
DEFAULT_VHS_ENABLED = True

TRANSITION_SPEED = 50
GLITCH_CHANCE = 0.001
GLITCH_DURATION = 60
CRT_SCANLINE_SIZE = 6
FADE_DURATION = 8000

CAM_ORDER = ["ENTRANCE-1", "SERVER", "ENTRANCE-2", "STORE", "ARMORY", "ENTRANCE-3", "MEDBAY", "RESERVOIR"]

ZONES = [
    {"name": "ENTRANCE-1", "x": 225, "y": 1250, "w": 180, "h": 60},
    {"name": "ENTRANCE-2", "x": 615, "y": 750, "w": 180, "h": 60},
    {"name": "ENTRANCE-3", "x": 1240, "y": 415, "w": 180, "h": 60},
    {"name": "ARMORY", "x": 1050, "y": 830, "w": 180, "h": 60},
    {"name": "STORE", "x": 958, "y": 1235, "w": 180, "h": 60},
    {"name": "RESERVOIR", "x": 1520, "y": 1120, "w": 180, "h": 60},
    {"name": "SERVER", "x": 600, "y": 1165, "w": 180, "h": 60},
    {"name": "MEDBAY", "x": 1515, "y": 830, "w": 180, "h": 60},
]

PAN_SPEED = 15
GRID_SIZE = 80
PAN_ACC = 0.02
PAN_MAX = 1
PAN_DURATION = 120
PAN_PAD = 600
ZONE_PAD = 80
BUTTON_SIZE = 70