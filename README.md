# [🧞 jAIvus](https://jaivus.streamlit.app/) [ʤɑ́ːvɪs]

<img src="logo.png" height=200 width=200>


Leveraging open source APIs to create a personal assistant chatbot

## Installation

1. Optionally install system dependencies (Ubuntu): `xargs -a packages.txt sudo apt-get install` 
2. Install python requirements: `pip install -r requirements.txt`
3. Copy `config.json.example` to `config.json` and fill in OpenAI `api_key` and optionally `session_token`

## Usage

Run `run streamlit app.py`

## To-dos

- [x] Add logo to project and UI
- [x] Add config options to the UI
- [x] Add a stop button to the UI
- [x] Add a download conversation button to the UI
- [x] Make the Stop button interruptive
- [x] Add statefulness where it makes sense
- [x] Host app on free cloud instance
- [x] Enable hosted app to use browser audio and microphone
- [x] Fix web listener recognizing speaker words
- [ ] Make the download button not reset the app
- [ ] Fix pyttsx3 save and load audio file
- [ ] Get rich or die trying