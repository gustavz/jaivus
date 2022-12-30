import logging
import time

import pyttsx3

logger = logging.getLogger(__name__)


class Speaker:
    def __init__(self, **kwargs):
        logger.info(f"initializing audio engine with properties {kwargs}")
        self.kwargs = kwargs
        self._init_engine()

    def _init_engine(self):
        self.engine = None
        self.engine = pyttsx3.init()
        for key, value in self.kwargs.items():
            self.engine.setProperty(key, value)

    def _sleep_text(self, text):
        rate = self.engine.getProperty("rate")
        words = len(text.split(" "))
        duration = words / rate * 60 + 1
        logger.info(
            f"sleeping {round(duration,3)} seconds while speaking {words} words"
        )
        time.sleep(duration)

    def speak(self, text):
        try:
            logger.info("start speaking")
            self.engine.say(text)
            self.engine.runAndWait()
            self._sleep_text(text)
            logger.info("stop speaking")
        except RuntimeError as e:
            logger.warning(f'caught audio runtime error "{e}" -> restart audio engine')
            self.engine.stop()
            self.engine.endLoop()
            self._init_engine()
            self.speak(text)
