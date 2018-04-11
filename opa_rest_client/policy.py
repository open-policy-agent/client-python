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
