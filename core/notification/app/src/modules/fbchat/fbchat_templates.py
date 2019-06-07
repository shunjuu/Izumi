# No imports needed
# Use template strings

TEMPLATE_1 = '''
{episode}

{sub} | {size}
{score}/100 | {eps} Eps

{time}
'''

class FBChatTemplates:
    """
    Contains templates used by FBChat's requests
    """

    def __init__(self):

        self._TEMPLATE_1 = TEMPLATE_1

    @property
    def TEMPLATE_1(self):
        return self._TEMPLATE_1
    
