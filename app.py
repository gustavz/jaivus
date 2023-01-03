import logging
import os
from datetime import datetime

import streamlit as st
import streamlit_toggle as tog

from chat import SUPPORTED_CHATBOTS, get_chatbot
from download import download_button
from listen import SUPPORTED_LISTENER, SUPPORTED_RECOGNIZER, get_listener
from speak import SUPPORTED_SPEAKER, get_speaker

logger = logging.getLogger(__name__)

# Init streamlit session and stateful parameters
SESSION = st.session_state

if "wake_word" not in SESSION:
    SESSION["wake_word"] = None
if "api_key" not in SESSION:
    SESSION["api_key"] = None
if "session_token" not in SESSION:
    SESSION["session_token"] = None
if "advanced_settings" not in SESSION:
    SESSION["advanced_settings"] = False
if "start_app" not in SESSION:
    SESSION["start_app"] = False
if "run_app" not in SESSION:
    SESSION["run_app"] = True
if "recognizer" not in SESSION:
    SESSION["recognizer"] = "google"
if "chatbot" not in SESSION:
    SESSION["chatbot"] = "openai"
if "speaker" not in SESSION:
    SESSION["speaker"] = "gtts"
if "listener" not in SESSION:
    SESSION["listener"] = "web"
if "config" not in SESSION:
    SESSION["config"] = "config.json"
if "conversation" not in SESSION:
    SESSION["conversation"] = []


# Helper methods
def stop_app():
    # Callable for reset button
    SESSION["start_app"] = False
    SESSION["run_app"] = False
    SESSION["conversation"] = []
    logger.info("stop the app")


## Streamlit app header
st.set_page_config(
    page_title="jAIvus",
    page_icon="🧞",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.title("🧞 jAIvus")
status_indicator = st.empty()
status_indicator.write("Submit your config to start the app")
listener_indicator = st.empty()
spinner = st.empty()


# Sidebar
with st.sidebar:
    st.image("logo.png")

    # Config form
    with st.form("config_form"):
        SESSION["api_key"] = st.text_input(
            "Enter your API key",
            type="password",
            help="OpenAI API key, needed if 'openai' chatbot is used",
        )
        if SESSION["advanced_settings"]:
            SESSION["session_token"] = st.text_input(
                "Enter your session token",
                type="password",
                help="OpenAI session token, needed if any other chatbot than 'openai' is used",
            )
            SESSION["chatbot"] = st.selectbox(
                "Choose chatbot",
                SUPPORTED_CHATBOTS,
                help="'openai' uses the model 'text-davinci-003' under the hood, the other chatbots directly invoke ChatGBT sessions",
            )
            SESSION["speaker"] = st.selectbox(
                "Choose speaker",
                SUPPORTED_SPEAKER,
                help="the text-to-speech library to use, if 'None' is selected, the app does not output any audio",
            )
            SESSION["recognizer"] = st.selectbox(
                "Choose a recoginzer",
                SUPPORTED_RECOGNIZER,
                help="the speech-to-text recognizer library to use",
            )
            SESSION["listener"] = st.selectbox(
                "Choose listener",
                SUPPORTED_LISTENER,
                help="the audio engine driver to use, 'local' only works if app is deployed locally",
            )
            SESSION["wake_word"] = st.text_input(
                "Enter a wake word",
                help="a wake word to start the app",
            )

        # Submit button
        submitted = st.form_submit_button("Submit")
        if submitted:
            logger.info("config submitted")
            st.text("config submitted")
            SESSION["start_app"] = True
            SESSION["run_app"] = True

            # Update config or stop app
            if SESSION["api_key"] or SESSION["session_token"]:
                SESSION["config"] = {
                    "api_key": SESSION["api_key"],
                    "session_token": SESSION["session_token"],
                }
            elif not os.path.exists(SESSION["config"]):
                st.error("You need to enter an API key or session token", icon="🚨")
                SESSION["start_app"] = False
                SESSION["run_app"] = False

    if SESSION["start_app"]:
        # Reset button
        cols = st.columns([1, 3])
        cols[0].button("Reset", on_click=stop_app)
    else:
        # Advanced Settings toggle
        tog.st_toggle_switch(label="Advanced Settings", key="advanced_settings")

# Main screen
try:
    if SESSION["start_app"]:
        # Activate microphone
        status_indicator.write("Select audio source and press 'Start'")
        listen = get_listener(SESSION["listener"], SESSION["recognizer"])

    if SESSION["start_app"] and listen.is_active:
        logger.info(f"start the app with config {SESSION['config']}")
        # Initialize engines
        speak = get_speaker(SESSION["speaker"])
        chat = get_chatbot(SESSION["chatbot"], SESSION["config"])

        # Wake-up Loop
        if SESSION["wake_word"]:
            # Wake-up instructions
            logger.info(f"waiting for wake word: {SESSION['wake_word']}")
            text = "Say the wake word to start the conversation:"
            status_indicator.write(f'{text} **"{SESSION["wake_word"]}"** [ʤɑ́ːvɪs]')
            speak.speak(text)

            with st.spinner("**Listening.**"):
                while SESSION["run_app"]:
                    # Record audio until the wake word is spoken
                    command = listen.listen(number_of_chunks=5000)
                    if command is not None:
                        listener_indicator.write(f'I understood: "*{command}*"')
                        if SESSION["wake_word"] in command.lower():
                            break

            # Transition to conversation loop
            text = "Wake word detected. Starting conversation..."
            speak.speak(text)
            status_indicator.write(f"**{text}**")
            listener_indicator.empty()

        # Conversation Loop
        with st.spinner("**Speak now.**"):
            while SESSION["run_app"]:
                # Record audio until the speaker stops speaking
                command = listen.listen(number_of_chunks=15000)
                if command is None:
                    listener_indicator.write("Sorry, I didn't understand this")
                    continue

                # Display the transcribed text
                listener_indicator.write(f'I understood: "*{command}*"')
                st.text("You:")
                st.text(command)
                SESSION["conversation"].append(f"You: {command}")

                # Get chatbot response and play it
                response = chat.chat(command)
                st.text("Jarvis:")
                st.text(response)
                SESSION["conversation"].append(f"Jarvis: {response}")
                speak.speak(response)
                listener_indicator.empty()

                # Download conversation button
                with st.sidebar:
                    file = "\n".join(SESSION["conversation"])
                    file_name = f"jaivus_conversation_{str(datetime.now())}.txt"
                    download_button_str = download_button(
                        file, file_name, "Download conversation"
                    )
                    cols[1].empty()
                    cols[1].markdown(download_button_str, unsafe_allow_html=True)

except Exception as e:
    # Error handling
    logger.warning(f"app failed with: {e}")
    st.error(e, icon="🚨")

logger.info("reset the app")
st.stop()
