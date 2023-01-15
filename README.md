# Tiny Tetris Bot

## Description

The Tiny Tetris Bot allows you to play the classic game of Tetris right within your Discord server. With a variety of Tetris pieces to play with, you can challenge your friends and compete for the highest score. The bot also features a variety of game controls, such as the ability to rotate and move pieces, as well as the ability to clear lines. Additionally, the bot tracks your score and number of lines cleared, giving you a sense of progression as you play.

The game is played in an interactive way, by using discord reactions as a control method. The bot also features an embedded message that updates in real-time, giving you a clear view of the game board and your progress. The game board is designed to be immersive, with different colored squares representing the different Tetris pieces. The bot is also designed to be user-friendly, with easy-to-use controls and a simple interface. The game also includes a game over feature and allows to restart the game again with just one press of a button. Unfortunately, due to Discord's API rate limit, the game progresses very slowly—this may change in the future.

> The code for this bot is written in Python, using the discord.py library and the asyncio library for running coroutines. It also uses RNG to make the game more interesting and challenging. Additionally, the code utilizes the dotenv library to store the bot's token, making it easy to run the bot on your own server.
<br>

## Video Demonstration

Watch the demo [here](https://drive.google.com/file/d/1Ylk65-2wrIk2a93cwuL8KCYuBMw28OMn/view?usp=sharing).
<br>

## Documentation

[Click here](Tiny Tetris Bot.pdf) for the documentation of this project.

## How to Run

1. Install the dotenv and discord.py dependencies.

```
pip install dotenv
pip install discord.py
```

2. Create a bot on the Discord Developer Portal, make sure all intents are enabled, and enable Administrator in Bot Permissions. Be sure to save your bot's token.
Here's a [website](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) for a full tutorial on hosting your own Discord bot.
3. Download and extract the zip file from this repository.
4. Open the folder in VSC.
5. Under the folder directory in the explorer, right-click > New File.
6. Name the file ```.env```.
7. In the file, type ```DISCORD_TOKEN = ``` followed by your bot's token.
8. In ```ttb.py```, click the run button on the top-right corner of the window. The bot should start running.
