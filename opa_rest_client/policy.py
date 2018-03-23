# coding=utf-8
"""
Policy class represents a Policy entity of Open Policy Agent
"""


class Policy(object):
    """
    Policy Class responsible for policy object update and delete
    """
    def __init__(self, policy_name, policy_path, rego_contents):
        self.name = policy_name
        self.url = policy_path
        self.contents = rego_contents
        # data files will be provided on init or on update
        self.data_files = list()

POLICY_REGO_TEXT = '''
package appguard

# HTTP API request
import input as http_api

default allow = false

# Allow configuration that matches data portion
allow {
   http_api.zone  = data.appguard_config[i]["example.com/zone"]
   http_api.classification = data.appguard_config[i]["example.com/classification"]
}
'''

POLICY_DATA_DICT = {
    'appguard_config': [
    {
      'example.com/zone': 'internal',
      'example.com/classification': 'secret'
    },
    {
      'example.com/zone': 'external',
      'example.com/classification': 'public'
    }
  ]
}

import json
import requests


def load_policy_and_data_opa(policy_text=POLICY_REGO_TEXT, policy_data=POLICY_DATA_DICT):
    """
    Load initial policy and data
    :return: status of success
    :rtype: bool
    """
    policy_resp = requests.put('http://localhost:8181/v1/policies/appguard',
                               data=policy_text,
                               headers={'Content-Type': 'text/plain'}
                               )

    data_resp = requests.put('http://localhost:8181/v1/data',
                             data=json.dumps(policy_data),
                             headers={'Content-Type': 'Application/json'}
                             )

    return policy_resp.status_code == 200 and data_resp.status_code == 204

print(load_policy_and_data_opa())
