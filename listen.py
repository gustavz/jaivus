import logging
import time

import speech_recognition as sr

logger = logging.getLogger(__name__)

SUPPORTED_RECOGNIZER = [
    "google",
    "whisper",
    "google_cloud",
    "sphinx",
    "wit",
    "azure",
    "bing",
    "lex",
    "houndify",
    "amazon",
    "ibm",
    "tensorflow",
    "assemblyai",
    "vosk",
]


class Listener:
    def __init__(self, recognizer="google", duration=2, **kwargs):
        assert recognizer in SUPPORTED_RECOGNIZER
        logger.info(f"initializing {recognizer} speech recognition engine")
        self.recognizer = sr.Recognizer()
        self.recognizer_function_name = f"recognize_{recognizer}"
        self.kwargs = kwargs

        if duration is not None:
            with sr.Microphone() as source:
                logger.info(
                    f"wait {duration} seconds to adjust the recognizer to ambient noise"
                )
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)

    def listen(self):
        with sr.Microphone() as source:
            logger.info("start listening")
            audio = self.recognizer.listen(source)
        logger.info("stop listening")
        return self.recognize(audio)

    def recognize(self, audio):
        try:
            logger.info("start recognizing")
            t = time.time()
            text = getattr(self.recognizer, self.recognizer_function_name)(
                audio, **self.kwargs
            )
            time_parsing = time.time() - t
            logger.info(f"stop recognizing (it took {round(time_parsing, 3)} seconds)")
            return text
        except sr.UnknownValueError as e:
            logger.warning(f"recognizer could not understand audio")
        except sr.RequestError as e:
            logger.warning(f"could not request results from recognizer")

    def recognize_frames(self, audio_frames, sample_rate, sample_width):
        audio = sr.AudioData(audio_frames, sample_rate, sample_width)
        return self.recognize(audio)
