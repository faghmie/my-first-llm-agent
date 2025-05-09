# Install the Slack SDK
# pip install slack-sdk

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Set your Slack token here or use an environment variable
SLACK_TOKEN = "xoxb-your-bot-token"
CHANNEL_NAME = "#your-channel-name"  # or use a channel ID like "C1234567"

def send_slack_message(message):
    # Initialize the Slack client
    client = WebClient(token=SLACK_TOKEN)

    try:
        # Post a message to the channel
        response = client.chat_postMessage(
            channel=CHANNEL_NAME,
            text=message
        )
        return f"Message sent at: {response['ts']}"

    except SlackApiError as e:
        return f"Error: {e.response['error']}"
