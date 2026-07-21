import os
import sys
import random

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class AudioManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AudioManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.enabled = True
        self.current_track = None
        self._initialized = True
        
        if not PYGAME_AVAILABLE:
            self.enabled = False
            return
            
        try:
            pygame.mixer.init()
        except Exception as e:
            # Silent fallback if audio device is missing or busy
            self.enabled = False

    def play_music(self, track_name: str, loop: int = -1):
        """Plays a background music track (MP3) from the songs/ directory.
        Tracks: 'home', 'hotel', 'romance'
        """
        if not self.enabled:
            return
            
        song_path = os.path.join("songs", f"{track_name}.mp3")
        if not os.path.exists(song_path):
            return
            
        if self.current_track == track_name:
            return  # Already playing this track
            
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(loop)
            self.current_track = track_name
        except Exception:
            pass

    def stop_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
            self.current_track = None
        except Exception:
            pass

    def play_sfx(self, sfx_name: str):
        """Plays a short sound effect from songs/UI sounds/ folder.
        Common sfx_name options:
        - 'button_click': SFX_Button_004.wav
        - 'menu_click': SFX_Button_018.wav
        - 'coin': SFX_Coin_Particle_004.wav (for cash change, transaction)
        - 'dialogue': Random VO sound effect
        - 'select': SFX_Item_Select_001.wav
        - 'notify': SFX_Notification_008.wav
        - 'success': SFX_Positive_Feedback_008.wav
        """
        if not self.enabled:
            return
            
        # Map logical names to filenames
        mapping = {
            "button_click": "SFX_Button_004.wav",
            "menu_click": "SFX_Button_018.wav",
            "coin": "SFX_Coin_Particle_004.wav",
            "select": "SFX_Item_Select_001.wav",
            "notify": "SFX_Notification_008.wav",
            "success": "SFX_Positive_Feedback_008.wav"
        }
        
        if sfx_name == "dialogue":
            dialogues = [
                "SFX_Dialogue_VO_Agathe_003.wav",
                "SFX_Dialogue_VO_Frank_004.wav",
                "SFX_Dialogue_VO_Frank_006.wav",
                "SFX_Dialogue_VO_Jacob_002.wav"
            ]
            filename = random.choice(dialogues)
        else:
            filename = mapping.get(sfx_name)
            
        if not filename:
            filename = sfx_name  # fallback to raw filename if not in mapping
            
        sfx_path = os.path.join("songs", "UI sounds", filename)
        if not os.path.exists(sfx_path):
            return
            
        try:
            sound = pygame.mixer.Sound(sfx_path)
            sound.set_volume(getattr(self, 'sfx_volume', 1.0))
            sound.play()
        except Exception:
            pass

    def set_music_volume(self, volume: float):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception:
            pass

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = volume

# Global convenience instance
audio_manager = AudioManager()
