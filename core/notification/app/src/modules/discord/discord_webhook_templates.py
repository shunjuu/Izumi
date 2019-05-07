# No imports needed
# Use template strings

TEMPLATE_1 = '''
{{
    "embeds": [
        {{
            "color": {color:d},
            "timestamp": "{timestamp}",
            "footer": {{
                "text": "© Aeri | {show_original}"
            }},
            "thumbnail": {{
                "url": "{thumbnail_url}"
            }},
            "fields": [
                {{
                    "name": "{title}",
                    "value": "{mins} mins, {size} [{sub_type}]"
                }},
                {{
                    "name": "Information",
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

        self.template_1 = TEMPLATE_1


    def get_template_1(self):
        return self.template_1


