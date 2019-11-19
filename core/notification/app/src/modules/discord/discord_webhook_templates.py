# No imports needed
# Use template strings

TEMPLATE_1 = '''
{{
    "embeds": [
        {{
            "title": "{title}",
            "description": "{mins} mins, {size} [{sub_type}]",
            "color": {color:d},
            "timestamp": "{timestamp}",
            "footer": {{
                "text": "{show_original}"
            }},
            "thumbnail": {{
                "url": "{thumbnail_url}"
            }},
            "author": {{
                "name": "{studio}",
                "url": "{studio_url}"
            }},
            "fields": [
                {{
                    "name": "Stats",
                    "value": "Score: {score}/100, Pop: {popularity}, Total: {eps} Eps."
                }},
                {{
                    "name": "Links",
                    "value": "[MyAnimeList]({mal_url}) | [Anilist]({anilist_url}) | [Kitsu]({kitsu_url})"
                }}
            ]
        }}
    ]    
}}
'''


class DiscordWebhookTemplates:
    """
    Contains templates used by Discord's requests
    """

    def __init__(self):

        self._TEMPLATE_1 = TEMPLATE_1

    @property
    def TEMPLATE_1(self):
        return self._TEMPLATE_1
    
