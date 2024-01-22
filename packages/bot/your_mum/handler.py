import json
import os
from typing import Any

import requests
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


class InteractionType:
    """https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type"""

    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionCallbackType:
    """https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-callback-type"""

    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class DiscordAPI:
    BASE_URL = "https://discord.com/api/v10"

    def __init__(self) -> None:
        PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]
        self.verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        self.app_id = os.environ["DISCORD_APP_ID"]

    @staticmethod
    def make_response(status, body):
        return {"statusCode": status, "body": body}

    def verify(self, event):
        headers = event["headers"]
        body = json.loads(event["body"])

        signature = headers["x-signature-ed25519"]
        timestamp = headers["x-signature-timestamp"]

        message = timestamp + json.dumps(body, separators=(",", ":"))
        self.verify_key.verify(message.encode(), signature=bytes.fromhex(signature))

    def handle(self, event: dict):
        # check for pings
        if event.get("source") == "scheduler":
            return self.make_response(200, {})

        try:
            self.verify(event)
        except BadSignatureError:
            return self.make_response(401, {"msg": "invalid request signature"})

        body = json.loads(event["body"])

        interaction_type = body["type"]
        if interaction_type == InteractionType.PING:
            print("Received Discord ping!")
            return self.make_response(200, {"type": InteractionCallbackType.PONG})
        elif interaction_type == InteractionType.APPLICATION_COMMAND:
            return self.custom_handler(body)
        else:
            print(f"Unhandled interaction type: {interaction_type}")
            return self.make_response(400, {"msg": "unhandled request type."})

    def custom_handler(self, body) -> dict[str, Any]:
        raise NotImplementedError()

    def create_interaction_response(self, interaction_id, interaction_token, json_):
        endpoint = f"/interactions/{interaction_id}/{interaction_token}/callback"
        return requests.request("post", self.BASE_URL + endpoint, json=json_)

    def create_followup_message(self, interaction_token, json_):
        endpoint = f"/webhooks/{self.app_id}/{interaction_token}"
        return requests.request("post", self.BASE_URL + endpoint, json=json_)
