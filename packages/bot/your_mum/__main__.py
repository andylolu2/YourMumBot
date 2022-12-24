import json
import os

import cohere

from lib.handler import DiscordAPI, InteractionCallbackType


class YourMumDiscordAPI(DiscordAPI):
    COMMAND_NAME = "mum_joke"

    def __init__(self):
        super().__init__()

        with open("config.json", "r") as f:
            config = json.load(f)

        template = []
        template.append(config["introduction"])
        template.append("")
        for sample in config["samples"]:
            template += [
                "Prompt: " + sample["prompt"],
                "Your mum joke: " + sample["joke"],
                "--",
            ]
        template += [
            "Prompt: {prompt}",
            "Your mum joke:",
        ]

        self.template = "\n".join(template)
        self.co = cohere.Client(os.environ["COHERE_API_KEY"])
        self.default = config["defaultResponse"]

    def make_joke(self, prompt: str):
        prediction = self.co.generate(
            model="xlarge",
            prompt=self.template.format(prompt=prompt),
            temperature=0.4,
            k=0,
            p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop_sequences=["--", "\n"],
            num_generations=1,
        )

        joke = prediction.generations[0].text

        if "your mum" not in joke.lower():
            return None

        return joke

    def custom_handler(self, body):
        data = body["data"]
        command = data["name"]
        interaction_id = body["id"]
        interaction_token = body["token"]

        if command == self.COMMAND_NAME:
            print(f"Received {command}.")

            prompts = [
                option for option in data["options"] if option["name"] == "prompt"
            ]
            assert len(prompts) == 1

            # shows "<Bot Name> is thinking..."
            response = self.create_interaction_response(
                interaction_id,
                interaction_token,
                {"type": InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE},
            )
            if not response.ok:
                print(response.json())

            prompt = prompts[0]["value"]
            joke = self.make_joke(prompt)

            if joke is None:
                content = self.default
            else:
                content = f"> *{prompt}*\n{joke}"

            # sends the response through http API
            response = self.create_followup_message(
                interaction_token, {"content": content}
            )
            if not response.ok:
                print(response.json())

            return {}

        print(f"Unknown command: {command}")
        return self.make_response(400, {"msg": "unhandled command"})


discord_api = YourMumDiscordAPI()


def main(args: dict):
    try:
        return discord_api.handle(event=args["http"])
    except Exception as e:
        print(e)
        return YourMumDiscordAPI.make_response(
            500, {"msg": "An interval server error occurred. Please view the logs."}
        )


"2022-12-22T03:51:56.576976176Z stdout: {'app_permissions': '1071698660929', 'application_id': '860228012809388042', 'channel_id': '859528780934676504', 'data': {'id': '1055162517464305714', 'name': 'mum_joke', 'options': [{'name': 'prompt', 'type': 3, 'value': 'Testing 123'}], 'type': 1}, 'entitlement_sku_ids': [], 'guild_id': '859528780934676501', 'guild_locale': 'en-US', 'id': '1055331824953466980', 'locale': 'en-GB', 'member': {'avatar': None, 'communication_disabled_until': None, 'deaf': False, 'flags': 0, 'is_pending': False, 'joined_at': '2021-06-29T20:20:30.694000+00:00', 'mute': False, 'nick': None, 'pending': False, 'permissions': '4398046511103', 'premium_since': None, 'roles': [], 'user': {'avatar': '9e84b18b5927333983f03c4f301aef5e', 'avatar_decoration': None, 'discriminator': '2545', 'id': '322965201827921924', 'public_flags': 0, 'username': 'BjergerK1ng'}}, 'token': 'aW50ZXJhY3Rpb246MTA1NTMzMTgyNDk1MzQ2Njk4MDowY2tjSWhpVVhxb3ZuNXFCS2thdEp2d0RiU0ZSV2VLOUtUdjg1V2dVMzVmb1l2UE5qdjdzQlljQUtyWjlMUGpqZTlyVjJjVGM4MVlVMVJIV3VQZmFKblZscnE4dHdZd2Z0N0k0bWJxTmw4ZWdIalZiRVZTeEx6eVA1M2Fna1ZlMg', 'type': 2, 'version': 1}"
