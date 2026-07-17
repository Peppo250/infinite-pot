# ui/audio.py
from engine.audio import audio_manager

class UIAudio:
    @staticmethod
    def play_click():
        """Play general button selection sound."""
        audio_manager.play_sfx("select")
        
    @staticmethod
    def play_coin():
        """Play currency or cash transaction sound."""
        audio_manager.play_sfx("coin")
        
    @staticmethod
    def play_success():
        """Play success fanfare / upgrade sound."""
        audio_manager.play_sfx("success")
        
    @staticmethod
    def play_dialogue():
        """Play random dialogue gibberish/VO sound."""
        audio_manager.play_sfx("dialogue")
        
    @staticmethod
    def play_notify():
        """Play pop-in alert notification sound."""
        audio_manager.play_sfx("notify")
        
    @staticmethod
    def play_music(track_name: str):
        """Play background music track (home, hotel, romance, bar)."""
        audio_manager.play_music(track_name)
