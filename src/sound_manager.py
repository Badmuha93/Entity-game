import pygame


class SoundManager:
    
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.current_music = None

    def load(self, name, path):
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.sfx_volume)
            return True
        except Exception:
            return False

    def play(self, name, loops=0):
        if name in self.sounds:
            self.sounds[name].play(loops)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def play_music(self, path, loop=-1, fade_ms=0):
        try:
            if fade_ms > 0:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.play(loop)
                steps = fade_ms // 50
                for i in range(steps):
                    volume = self.music_volume * (i / steps)
                    pygame.mixer.music.set_volume(volume)
                    pygame.time.wait(50)
                pygame.mixer.music.set_volume(self.music_volume)
            else:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loop)
            self.current_music = path
            return True
        except Exception:
            return False

    def stop_music(self, fade_ms=0):
        if fade_ms > 0:
            current_volume = pygame.mixer.music.get_volume()
            steps = fade_ms // 50
            for i in range(steps):
                volume = current_volume * (1 - i / steps)
                pygame.mixer.music.set_volume(volume)
                pygame.time.wait(50)
        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(self.music_volume)
        self.current_music = None

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)