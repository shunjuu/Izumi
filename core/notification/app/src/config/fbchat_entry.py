from fbchat.models import ThreadType

class FBChatEntry:
    """
    Stores each individual chat entry node
    """

    def __init__(self, chat):
        """Sets variables into properties"""
        self._name = chat['name']
        self._type = self._load_thread_type(chat['type'])
        self._thread_id = int(chat['thread_id'])
        self._template = self._load_template(chat)

    @property
    def name(self):
        return self._name
    
    @property
    def type(self):
        return self._type

    @property
    def thread_id(self):
        return self._thread_id

    @property
    def template(self):
        return self._template

    def _load_thread_type(self, thread_type):
        """Load ThreadType ENUM group"""
        if thread_type.lower() == "user":
            return ThreadType.USER
        else:
            return ThreadType.GROUP
    
    def _load_template(self, chat):
        """Load template type"""
        if 'template' in chat:
            return chat['template']
        else:
            return 1 # Default value