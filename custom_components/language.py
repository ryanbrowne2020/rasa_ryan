from typing import Dict, Text, Any, List, Optional

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
#from langdetect import detect

import requests
import json


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class LanguageHandler(GraphComponent):
    def __init__(
        self,
        model_storage: ModelStorage,
        resource: Resource,
        training_artifact: Optional[Dict],
    ) -> None:
        self._model_storage = model_storage
        self._resource = resource

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ):
        # TODO: Implement this
        return cls(model_storage, resource, training_artifact=None)

    def train(self, training_data: TrainingData) -> Resource:
        # TODO: Implement this if your component requires training
        pass

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # TODO: Implement this if your component augments the training data with
        #       tokens or message features which are used by other components
        #       during training.

        return training_data

    def process(self, messages: List[Message]) -> List[Message]:
        # TODO: This is the method which Rasa Open Source will call during inference.

        updated_messages = []
        for message in messages:
            text = Text(
                message.get("text")
            )  # handle text as a Text object rather than a simple string for rasa version compatibilty issues else it won't work

            # if detected_lang.lang != 'en':
            response = requests.post(
                "https://api.deepl.com/v2/translate",
                data={
                    "auth_key": "005c8434-eb66-6eb9-0c33-753756ea4b6d",
                    "target_lang": "EN",
                    "text": text,
                },
            )
            json_obj = json.loads(response.text)

            detected_lang = json_obj["translations"][0]["detected_source_language"]
            text = json_obj["translations"][0]["text"]

            print("//// System understood: " + text)

            # changing the input message's text after translation
            message.set("text", Text(text))
            updated_messages.append(message)
        return updated_messages
