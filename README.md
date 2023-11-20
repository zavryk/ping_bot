# IP Status Bot
AI generated bot and readme

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)

This Telegram bot, powered by [aiogram](https://docs.aiogram.dev/), checks the status of a specified IP address and sends updates to a designated chat. It provides humorous responses based on whether the monitored IP is up or down.

## Features

- **Status Check**: Regularly checks the status of a specified IP address.
- **Scheduled Checks**: Performs status checks at intervals and sends updates to the specified chat.
- **Humorous Responses**: Provides entertaining responses when the IP is up or down.
- **Inline Query Support**: Allows users to inquire about the status with inline queries.

## Usage

1. **Set Up Environment Variables:**
    - `ACCESS_TOKEN`: Your Telegram bot token.
    - `NODE`: The IP address to monitor.
    - `NODE_PORT`: The port on the monitored node (default is 53131).
    - `YOUR_CHAT_ID`: The Telegram chat ID where status updates will be sent.

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Bot:**
    ```bash
    python your_bot_script.py
    ```

## Commands

- `/status`: Manually checks and sends the current status.
- "А щас?": Asks for the current status.

## Inline Queries

Use inline queries to get the current status on the go!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
