import json
import logging

import openai
from pyChatGPT import ChatGPT
from revChatGPT.Official import Chatbot

logger = logging.getLogger(__name__)

SUPPORTED_CHATBOTS = ["openai", "pychatgpt", "revchatgpt"]


def get_chatbot(bot="openai", config="config.json"):
    assert bot in SUPPORTED_CHATBOTS
    if bot == "openai":
        return OpenAIBot(config)
    elif bot == "pychatgpt":
        return PyChatGPTBot(config)
    elif bot == "revchatgpt":
        return RevPyChatGPTBot(config)


class OpenAIBot:
    def __init__(self, config="config.json"):
        if isinstance(config, str):
            config = json.load(open(config))
        openai.api_key = config["api_key"]
        # Init openai parameters
        self.parameters = {}
        self.parameters["engine"] = config.get("engine", "text-davinci-003")
        self.parameters["temperature"] = config.get("temperature", 0.5)
        self.parameters["max_tokens"] = config.get("max_tokens", 1024)
        self.parameters["top_p"] = config.get("top_p", 1)
        self.parameters["frequency_penalty"] = config.get("frequency_penalty", 0)
        self.parameters["presence_penalty"] = config.get("presence_penalty", 0)

    def chat(self, prompt):
        logger.info("start chat")
        response = openai.Completion.create(
            prompt=prompt,
            **self.parameters,
        )
        logger.info(f"response: {response}")
        return response["choices"][0]["text"]


class PyChatGPTBot:
    def __init__(self, config="config.json"):
        if isinstance(config, str):
            config = json.load(open(config))
        self.bot = ChatGPT(config["session_token"])
        self.bot.reset_conversation()

    def chat(self, prompt):
        logger.info("start chat")
        response = self.bot.send_message(prompt)
        logger.info(f"response: {response}")
        return response["message"]


class RevPyChatGPTBot:
    def __init__(self, config="config.json"):
        if isinstance(config, str):
            config = json.load(open(config))
        self.bot = Chatbot(api_key=config["api_key"])

    def chat(self, prompt):
        logger.info("start chat")
        response = self.bot.ask(prompt)
        logger.info(f"response: {response}")
        return response["choices"][0]["text"]
