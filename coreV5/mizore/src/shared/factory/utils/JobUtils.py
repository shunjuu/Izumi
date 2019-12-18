"""
Fancy transformations with the Job class
"""

import json

from typing import Dict

from src.shared.constants.Job import Job #pylint: disable=import-error

class JobUtils:

    @staticmethod
    def to_dict(job: Job) -> Dict:
        dict_form = dict()
        dict_form['show'] = job.show
        dict_form['episode'] = job.episode
        dict_form['filesize'] = job.filesize
        dict_form['sub'] = job.sub

        return dict_form
    
    @staticmethod
    def to_jsons(job: Job) -> str:
        return json.dumps(JobUtils.to_dict(job))