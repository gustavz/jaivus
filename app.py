import logging
import os
from datetime import datetime

import streamlit as st
import streamlit_toggle as tog

from jaivus.chat import get_chatbot
from jaivus.download import download_button
from jaivus.listen import get_listener
from jaivus.speak import get_speaker

logger = logging.getLogger(__name__)

WAKE_WORD = "Jarvis"

# Init streamlit session and stateful parameters
SESSION = st.session_state

if "wake_word" not in SESSION:
    SESSION["wake_word"] = False
if "api_key" not in SESSION:
    SESSION["api_key"] = None
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
    SESSION["speaker"] = None
if "listener" not in SESSION:
    SESSION["listener"] = "web"
if "config" not in SESSION:
    SESSION["config"] = "config.json"
if "conversation" not in SESSION:
    SESSION["conversation"] = []
if "local_mode" not in SESSION:
    SESSION["local_mode"] = False
if "mute" not in SESSION:
    SESSION["mute"] = True


# Helper methods
def stop_app():
    # Callable for reset button
    SESSION["start_app"] = False
    SESSION["run_app"] = False
    SESSION["conversation"] = []
    logger.info("stop the app")


## Streamlit app header
st.set_page_config(
    page_title="jAIvus [ʤɑ́ːvɪs]",
    page_icon="🧞",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.title("🧞 jAIvus [ʤɑ́ːvɪs]")
status_indicator = st.empty()
status_indicator.write("Submit your config to start the app ( *muted by default* )")
spinner = st.empty()


# Sidebar
with st.sidebar:
    st.image("logo.png")

    # Config form
    with st.form("config_form"):
        SESSION["api_key"] = st.text_input(
            "Enter your API key",
            type="password",
            help="Enter your OpenAI API key, which can be found [here](https://platform.openai.com/account/api-keys)",
        )
        if SESSION["advanced_settings"]:
            SESSION["mute"] = st.checkbox(
                "mute app",
                value=True,
                help="Mutes audio output",
            )
            SESSION["wake_word"] = st.checkbox(
                "use wake word",
                value=False,
                help="Use wake word 'Jarvis' to initially start the conversation",
            )
            SESSION["local_mode"] = st.checkbox(
                "local mode",
                value=False,
                help="Experimental mode using different libraries, only works if app is deployed locally",
            )

        # Submit button
        submitted = st.form_submit_button("Submit")
        if submitted:
            logger.info("config submitted")
            st.text("config submitted")
            SESSION["start_app"] = True
            SESSION["run_app"] = True

            # Update config or stop app
            if SESSION["local_mode"]:
                SESSION["listener"] = "local"
                SESSION["speaker"] = "pyttsx3"
            else:
                SESSION["listener"] = "web"
                SESSION["speaker"] = "gtts"
            if SESSION["mute"]:
                SESSION["speaker"] = None
            if SESSION["api_key"]:
                SESSION["config"] = {
                    "api_key": SESSION["api_key"],
                }
            elif not os.path.exists(SESSION["config"]):
                st.error("You need to enter an API Key", icon="🚨")
                SESSION["start_app"] = False
                SESSION["run_app"] = False

    if SESSION["start_app"]:
        # Reset button
        st.button("Reset", on_click=stop_app)
        # Download button container
        dowload_button = st.empty()
    else:
        # Advanced Settings toggle
        tog.st_toggle_switch(label="Advanced Settings", key="advanced_settings")


# Main screen
try:
    if SESSION["start_app"]:
        # Activate web microphone
        if SESSION["listener"] == "web":
            status_indicator.write("Select audio source and press **'Start'**")
        else:
            status_indicator.write("Initializing engines")
        listen = get_listener(SESSION["listener"], SESSION["recognizer"])

    if SESSION["start_app"] and listen.is_active:
        # Initialize engines
        logger.info(f"start the app with config {SESSION['config']}")
        speak = get_speaker(SESSION["speaker"])
        chat = get_chatbot(SESSION["chatbot"], SESSION["config"])

        # Wake-up Loop
        if SESSION["wake_word"]:
            # Wake-up instructions
            logger.info(f"waiting for wake word: {WAKE_WORD}")
            text = "Say the wake word to start the conversation:"
            status_indicator.write(f'{text} **"{WAKE_WORD}"**')
            speak.speak(text)

            with st.spinner("**Listening**"):
                while SESSION["run_app"]:
                    # Record audio until the wake word is spoken
                    command = listen.listen(number_of_chunks=5000)
                    if command is not None:
                        if WAKE_WORD.lower() in command.lower():
                            break

            # Transition to conversation loop
            text = "Wake word detected, starting conversation"
        else:
            text = "Starting conversation"
        speak.speak(text)
        status_indicator.write(f"{text}")

        # Conversation Loop
        with st.spinner("**Conversation**"):
            while SESSION["run_app"]:
                # Record audio until the speaker stops speaking
                status_indicator.write("I am listening to you")
                command = listen.listen(number_of_chunks=15000)
                if command is None:
                    status_indicator.write("Sorry, I didn't understand this")
                    continue

                # Display the transcribed text
                status_indicator.write(f'I am processing your command: "*{command}*"')
                st.text("You:")
                st.text(command)
                SESSION["conversation"].append(f"You: {command}")

                # Get chatbot response and play it
                response = chat.chat(command)
                st.text("Jarvis:")
                st.text(response)
                SESSION["conversation"].append(f"Jarvis: {response}")
                speak.speak(response)

                # Download conversation button
                with st.sidebar:
                    file = "\n".join(SESSION["conversation"])
                    file_name = f"jaivus_conversation_{str(datetime.now())}.txt"
                    download_str = download_button(
                        file, file_name, "Download conversation"
                    )
                    dowload_button.write(download_str, unsafe_allow_html=True)

except Exception as e:
    # Error handling
    logger.warning(f"app failed with: {e}")
    st.error(e, icon="🚨")

logger.info("reset the app")
st.stop()
