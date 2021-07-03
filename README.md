<!-- omit in toc -->
# YourMumBot

YourMumBot is a discord bot that reads at text sent by 
users in a discord channel, and makes your mum jokes from them.

<!-- omit in toc -->
# :warning: DISCLAIMER :warning:

**THIS MODEL IS PURPOSEFULLY DESIGNED TO BE INSULTING.**

**THIS BOT IS CREATED FOR COMEDIC PURPOSES ONLY. PLEASE BE AWARE THAT 
CONTENT SENT BY YOURMUMBOT CAN BE VERY OFFENSIVE.**

**DO NOT** use this bot if anyone in the server would find it offensive / 
inappropriate.

I am **NOT** responsible for misuse of this bot / code. Misuse includes 
but is not limited to: 
- Using this bot to offend someone
- Using this bot in stituations where someone would find it offensive
- Causing undesired results by using this code


<!-- omit in toc -->
## Table of contents
- [Add YourMumBot to your server](#add-yourmumbot-to-your-server)
- [Sample outputs](#sample-outputs)
- [How it works](#how-it-works)
  - [Pipeline](#pipeline)
- [Links](#links)

## Add YourMumBot to your server

Click here :point_down:

[<img src="static/readme/discord-logo.svg" alt="discord logo" width="100">](https://discord.com/api/oauth2/authorize?client_id=856211082720444456&permissions=3072&scope=bot)

## Sample outputs

```
User: Flat earthers think that the earth is flat
Bot: Flat earthers think that your mum is flat

User: League of legends is such a shit game
Bot: Your mum is such a shit game

User: Today is a good day. You are very tall.
Bot: Today is your mum. Your mum is very tall.
```

## How it works

YourMumBot makes use of 3 main nlp models / tools:
1. [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) 
via [stanza](https://stanfordnlp.github.io/stanza/corenlp_client.html)
2. [Detoxify](https://github.com/unitaryai/detoxify)
3. [Language tools](https://github.com/jxmorris12/language_tool_python)

### Pipeline

1. The `CoreNLP` library 
[constituency parser](https://stanfordnlp.github.io/CoreNLP/parse.html)
is used to 
identify noun phrases (NP) in a input sentence. 
2. These NPs serves as potential places in the sentence where we can
substitute the NP with the string `your mum`. This works surprisingly 
well.
3. For each of these potential substitutions, we use `Detoxify` to 
rate the toxicity of the sentence. We then pick the sentence 
that has the highest toxicity.
4. At various points while processing the input, `language tools` 
is used to correct grammatical mistakes of the (potential) 
output sentences. 

    For example, this might be due to substitution of 
    `you` with `your mum` in `You are very tall`, which leads 
    to the grammatically incorrect output `your mum are very tall`.

    `language tools` tries to fix this problem.

## Links

- Docker Hub repository: [link](https://hub.docker.com/repository/docker/andylolu24/yourmumbot)
