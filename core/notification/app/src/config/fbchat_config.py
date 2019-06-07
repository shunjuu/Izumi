from src.config.fbchat_entry import FBChatEntry

class FBChatConfig:
    """
    Stores FBChat configurations
    """

    def __init__(self, fbchat_conf, dev=False):
        """Initialize variables""" 
        self._username = self._load_username(fbchat_conf, dev)
        self._password = self._load_password(fbchat_conf, dev)
        self._chats = self._load_chats(fbchat_conf, dev)

    @property
    def username(self):
        """Username for FBChat"""
        return self._username

    @property
    def password(self):
        """Password for FBChat"""
        return self._password

    @property
    def chats(self):
        """Chat listings for FBChat"""
        return self._chats
    
    def _load_username(self, fbchat_conf, dev=False):
        """Load the username"""
        return fbchat_conf['username']

    def _load_password(self, fbchat_conf, dev=False):
        """Load the password"""
        return fbchat_conf['password']

    def _load_chats(self, fbchat_conf, dev=False):
        """Load the chats"""
        chats = list()

        if not dev:
            for chat in fbchat_conf['chats']:
                chats.append(FBChatEntry(chat))
        else:

            # If username/password/name is not provided, chats is set to 0-len list,
            # which will cause FBChat to be completely skipped :)
            if not self._username or not self._password or not fbchat_conf['name']:
                return list()

            chat = dict()
            chat['name'] = fbchat_conf['name']
            chat['type'] = fbchat_conf['type']
            chat['thread_id'] = fbchat_conf['thread_id']
            chat['template'] = fbchat_conf['template']
            chats.append(FBChatEntry(chat))

        return chats
