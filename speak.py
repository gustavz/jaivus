import time
import pyttsx3


class Speaker:
    def __init__(self, **kwargs):
        print(f'initializing audio engine with properties {kwargs}')
        self.kwargs = kwargs
        self._init_engine()
    
    def _init_engine(self):
        self.engine = None
        self.engine = pyttsx3.init()
        for key, value in self.kwargs.items():
            self.engine.setProperty(key, value)
            print
    
    def _sleep_text(self, text):
        rate = self.engine.getProperty('rate')
        words = len(text.split(' '))
        duration = words / rate * 60 + 1
        print(f'sleeping {round(duration,3)} seconds while speaking {words} words')
        time.sleep(duration)

    def speak(self, text):
        try:
            print('start speaking')
            self.engine.say(text)
            self.engine.runAndWait()
            self._sleep_text(text)
            print('stop speaking')
        except RuntimeError as e:
            print(f'caught audio runtime error "{e}" -> restart audio engine')
            self.engine.stop()
            self.engine.endLoop()
            self._init_engine()
            self.speak(text)

