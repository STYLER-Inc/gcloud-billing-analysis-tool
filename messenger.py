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

SSL_CONTEXT = ssl_lib.create_default_context(cafile=certifi.where())

def send_slack_message(channel: str,
                       api_token: str,
                       text: str = None,
                       blocks: list = None):
    """Sends a slack message.

    Attributes:
        text: When specified, plain text is sent.
        blocks: When specified, a 'block' is sent.
        channel: The slack channel to send to.

    """
    if not text and not blocks:
        raise argparse.ArgumentError

    # Client to use whilst the cloud function is alive.
    client = slack.WebClient(token=api_token, ssl=SSL_CONTEXT)

    if text:
        response = client.chat_postMessage(channel=channel, text=text)
    if blocks:
        response = client.chat_postMessage(channel=channel, blocks=blocks)
    assert response["ok"]
