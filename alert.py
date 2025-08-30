import time, os
import simpleaudio as sa
import pyttsx3
import threading 
import multiprocessing
import queue

class AlertPlayer:
    def __init__(self, wav_path, cooldown_seconds=3.0):
        self.wav_path = wav_path
        self.cooldown = cooldown_seconds
        self.last_alert_time = 0.0
        self._obj = None
        if os.path.exists(self.wav_path):
            try:
                self._obj = sa.WaveObject.from_wave_file(self.wav_path)
            except Exception: 
                self._obj = None

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate",170)
        self.engine.setProperty("volume",1.0)

        self.speech_queue = queue.Queue()
        threading.Thread(target=self._speech_worker, daemon=True).start()

        self.messages = {
            "drowsy": "⚠️ Warning! You seem very drowsy. Please take a break or stop the vehicle safely.",
            "yawning": "You are yawning often. Try to rest or refresh yourself soon.",
            "looking_away": "Please keep your eyes on the road and stay attentive.",
            "normal": "You are going well, Keep up."
        }
        self.priorities = {
            "drowsy": 3,
            "yawning": 2,
            "looking_away": 1,
            "normal": 0
        }

    def play_sound_process(self):
        """Play beep in a fully isolated process."""
        if self._obj:
            try:
                play_obj = self._obj.play()
                play_obj.wait_done()
            except Exception as e:
                print("Beep error:", e)

    def play_sound_async(self):
        """Spawn a separate process for the beep."""
        if self._obj:
            p = multiprocessing.Process(target=self.play_sound_process)
            p.daemon = True
            p.start()
    
    def _speech_worker(self):
        """Runs in background, consumes messages from queue."""
        while True:
            text = self.speech_queue.get()
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("Speech error:", e)
            self.speech_queue.task_done()
    
    def speak_async(self, text):
        """Put message in queue for safe speaking."""
        self.speech_queue.put(text)

    def alert(self, states):
        """
        Accepts a single state or a list of states.
        Example: alert("drowsy") or alert(["yawning","looking_away"])
        """
        if isinstance(states, str):
            states = [states]

        # Pick highest priority state
        chosen_state = max(states, key=lambda s: self.priorities.get(s, 0))
        message = self.messages.get(chosen_state)

        # Check cooldown
        now = time.time()
        if message and (now - self.last_alert_time >= self.cooldown):
            self.play_sound_async()
            self.speak_async(message)
            self.last_alert_time = now
