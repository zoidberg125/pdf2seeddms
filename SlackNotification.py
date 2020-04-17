import logging
import requests
import json
import uuid
import os
from slack import WebClient
from slack.errors import SlackApiError

class SlackNotification:
    def __init__(self, logger):
        self.logger = logger
        self.SLACK_TOKEN="xoxb-320574012802-4n6GuhVZlicoppoeEEI3qHCE"
        self.slack_client = WebClient(self.SLACK_TOKEN)
    def notify(self,message):
        self.logger.info("Notifying Slack Channel")
        slack_client = self.slack_client
        try:
            slack_client.chat_postMessage(channel="#private_alerts",
                                            text="<@U44PAFHEY> "+ message
                                        )
        except Exception as e:
            self.logger.exception("SlackNotification failed")
