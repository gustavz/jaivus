import time

import speech_recognition as sr

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
        print(f"initializing {recognizer} speech recognition engine")
        self.recognizer = sr.Recognizer()
        self.recognizer_function_name = f"recognize_{recognizer}"
        self.kwargs = kwargs

        with sr.Microphone() as source:
            print(f"wait {duration} seconds to adjust the recognizer to ambient noise")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)

    def listen(self):
        with sr.Microphone() as source:
            print("start listening")
            audio = self.recognizer.listen(source)
        print("stop listening")

        try:
            t = time.time()
            text = getattr(self.recognizer, self.recognizer_function_name)(
                audio, **self.kwargs
            )
            time_parsing = time.time() - t
            print(f"it took {round(time_parsing, 3)} seconds to recognize: {text}")
            return text

        except sr.UnknownValueError:
            print(f"recognizer could not understand audio")
        except sr.RequestError as e:
            print(f"could not request results from recognizer")
