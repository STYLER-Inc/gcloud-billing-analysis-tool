# -*- coding: utf-8 -*-
"""Slack Messenger

Sends Slack messages.

Functionality:
    * Plain text
    * Markdown block
"""

import argparse
import os
import ssl as ssl_lib

import certifi
import slack

from settings import Settings

SETTINGS = Settings()

# Client to use whilst the cloud function is alive.
SSL_CONTEXT = ssl_lib.create_default_context(cafile=certifi.where())
CLIENT = slack.WebClient(token=SETTINGS.SLACK_API_TOKEN, ssl=SSL_CONTEXT)


def send_slack_message(text: str = None,
                       blocks: list = None,
                       channel: str = SETTINGS.SLACK_CHANNEL):
    """Sends a slack message.

    Attributes:
        text: When specified, plain text is sent.
        blocks: When specified, a 'block' is sent.
        channel: The slack channel to send to.

    """
    if not text and not blocks:
        raise argparse.ArgumentError

    if text:
        response = CLIENT.chat_postMessage(channel=channel, text=text)
    if blocks:
        response = CLIENT.chat_postMessage(channel=channel, blocks=blocks)
    assert response["ok"]
