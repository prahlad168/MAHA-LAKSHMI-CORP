#!/usr/bin/env python3
"""
GAURANGA VOICE - Text to Speech Module
Generated audio responses for GAURANGA AI Assistant
"""

import gtts
import os
import uuid
import subprocess
import platform

class GauranggaVoice:
    def __init__(self):
        self.audio_dir = "/workspace/project/Bot_Molty5/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Voice styles
        self.voice_styles = {
            "enthusiastic": "excited, ready to help",
            "professional": "professional, clear",
            "friendly": "warm, friendly tone",
            "urgent": "quick, action-oriented"
        }
        
    def speak(self, text, style="friendly", lang="id"):
        """Convert text to speech and play"""
        try:
            # Generate audio file
            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            # Generate speech
            tts = gtts.gTTS(text=text, lang=lang, slow=False)
            tts.save(filepath)
            
            # Play audio
            self._play_audio(filepath)
            
            return filepath
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def _play_audio(self, filepath):
        """Play audio file based on OS"""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", filepath], check=True)
            elif system == "Linux":
                # Try multiple players
                players = ["aplay", "paplay", "mpg123", "ffplay"]
                for player in players:
                    try:
                        subprocess.run([player, filepath], check=True, capture_output=True)
                        break
                    except:
                        continue
            elif system == "Windows":
                subprocess.run(["powershell", "-c", f"(New-Object System.Media.SoundPlayer('{filepath}')).PlaySync()"], check=True)
        except Exception as e:
            print(f"Could not play audio: {e}")
            print(f"Audio saved to: {filepath}")
    
    def greet(self):
        """Greeting message"""
        text = "Ya, Pak Pur! Gaurangga siap menerima perintah!"
        self.speak(text)
        return text
    
    def confirm(self, task):
        """Confirmation message"""
        text = f"Baik, Pak Pur! Saya akan {task}"
        self.speak(text)
        return text
    
    def complete(self, task):
        """Completion message"""
        text = f"Selesai, Pak Pur! {task} sudah selesai!"
        self.speak(text)
        return text
    
    def error(self, message):
        """Error message"""
        text = f"Maaf Pak Pur, ada masalah: {message}"
        self.speak(text)
        return text
    
    def ready(self):
        """Ready message"""
        text = "Gaurangga siap! Silakan berikan perintah Anda!"
        self.speak(text)
        return text


# Quick function for easy use
def voice_speak(text, lang="id"):
    """Quick speak function"""
    try:
        from gtts import gTTS
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=text, lang=lang)
            tts.save(f.name)
            
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["afplay", f.name], check=True)
            elif system == "Linux":
                try:
                    subprocess.run(["paplay", f.name], check=True)
                except:
                    subprocess.run(["aplay", f.name], check=True)
            elif system == "Windows":
                subprocess.run(["powershell", "-c", f"(New-Object System.Media.SoundPlayer('{f.name}')).PlaySync()"], check=True)
            
            os.unlink(f.name)
    except Exception as e:
        print(f"Speech error: {e}")
        print(f"Text: {text}")


if __name__ == "__main__":
    # Test
    gv = GauranggaVoice()
    gv.greet()
