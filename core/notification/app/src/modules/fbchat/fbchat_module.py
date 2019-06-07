import sys
import os

from hurry.filesize import size
from datetime import datetime
from fbchat import Client
from fbchat.models import Message, ThreadType

from src.modules.fbchat.fbchat_templates import FBChatTemplates

from src.prints.modules.fbchat.fbchat_module_prints import FBChatModulePrints

class FBChatModule:
    """
    Handles sending notifications on Facebook Messenger
    """

    def __init__(self, conf, reqh, printh, info):
        """
        Params:
            conf - ConfigHandler
            reqh - RequestHandler
            printh - PrintHandler
            info - HishaInfo class
        """

        self._logger = printh._logger
        self._prints = FBChatModulePrints(printh.Colors())

        self._conf = conf
        self._reqh = reqh
        self._info = info

        # Load the templates
        self._webhook_templates = FBChatTemplates()
        self._template_1 = self._webhook_templates.TEMPLATE_1


    def _generate_fmt_1(self):
        """
        Generates the format for TEMPLATE_1
        """

        score = str(self._info.averageScore) if self._info.averageScore != -1 else "〇〇"
        eps = str(self._info.episodes) if self._info.episodes != -1 else "〇〇"

        message = Message(text=self._template_1.format(episode=self._reqh.episode,
            sub=self._reqh.sub_type.lower().capitalize(),
            size=size(self._reqh.filesize),
            score=score,
            eps=eps,
            time=datetime.now().strftime("%c")))

        return message

    def send_notifications(self):
        """
        Sends the notifications to FB Chat
        """

        message_1 = self._generate_fmt_1()

        if self._conf.use_dev:

            # Only run this if there's any chats at all
            if len(self._conf.dev_fbchat.chats) > 0:

                self._logger.info(self._prints.DEV_ENABLED)

                fbchat_client = Client(
                    self._conf.dev_fbchat.username,
                    self._conf.dev_fbchat.password)
 

                if self._conf.dev_fbchat.chats[0].template == 1:
                    message = message_1

                self._logger.info(self._prints.SENDING_TO.format(self._conf.dev_fbchat.chats[0].name,
                    self._conf.dev_fbchat.chats[0].template))

                fbchat_client.send(message,
                    thread_id=self._conf.dev_fbchat.chats[0].thread_id,
                    thread_type=self._conf.dev_fbchat.chats[0].type)

            else:
                self._logger.info(self._prints.NOT_SENDING)

        else:

            # only run if there are entries
            if len(self._conf.fbchat.chats) > 0:

                self._logger.info(self._prints.DEV_DISABLED)

                fbchat_client = Client(
                    self._conf.fbchat.username,
                    self._conf.fbchat.password)

                for chat in self._conf.fbchat.chats:

                    if chat.template == 1:
                        message = message_1

                    self._logger.info(self._prints.SENDING_TO.format(chat.name, chat.template))

                    fbchat_client.send(message,
                        thread_id=chat.thread_id,
                        thread_type=chat.type)

            else:
                self._logger.info(self._prints.NOT_SENDING)