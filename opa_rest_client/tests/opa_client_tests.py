# coding=utf-8
"""
Open Policy Agent Client Test Suit
"""

import sys
import os
import unittest
import docker

from opa_rest_client.opa_docker_apis import run_opa_docker_container
from opa_rest_client.opa_client_apis import OPAClient, OPAValidationError
from opa_rest_client.policy import Policy


TEST_REGO_POLICY = '''
package opa_test

default allow = false

# Allow configuration that matches data portion
allow {
   input.zone  = data.opa_config[i]["example.com/zone"]
   input.classification = data.opa_config[i]["example.com/classification"]
}
'''


class TestOpaClient(unittest.TestCase):
    docker_client = client = docker.from_env()
    opa_container = None
    # FIXME: if running tests outside pycharm need to add 'tests/'
    test_rego_policy_path = os.path.abspath('data/test_rego_policy')

    @classmethod
    def setUpClass(cls):
        try:
            # Start opa container
            cls.opa_container = run_opa_docker_container(cls.docker_client)
            assert cls.opa_container is not None

        except BaseException as e:
            print("Unexpected error:", sys.exc_info()[0])
            raise ValueError("Unexpected error") from e

    @classmethod
    def tearDownClass(cls):
        if cls.opa_container is not None:
            cls.opa_container.stop()

    def test_create_policy(self):
        """ Test creation of a Policy object """
        opa_client = OPAClient()

        test_name = 'tests/test_policy'
        test_policy = TEST_REGO_POLICY

        # valid parameters, valid REGO, REGO blob
        policy_obj = opa_client.create_policy(test_name, test_policy)

        self.assertIsInstance(policy_obj, Policy)
        self.assertEqual(policy_obj.name, test_name)
        self.assertEqual(policy_obj.data_files, list())
        self.assertEqual(policy_obj.contents, test_policy)

        # invalid parameters, valid REGO, REGO blob
        test_name = 'invalid-name'  # only slashes and underscores allowed

        self.assertRaises(OPAValidationError, opa_client.create_policy, test_name, test_policy)

        # valid parameters, invalid REGO, REGO blob
        test_name = 'test_policy'
        test_policy = 'invalid Rego blob'

        self.assertRaises(OPAValidationError, opa_client.create_policy, test_name, test_policy)

        # valid parameters, valid REGO, REGO file path
        # multiple default rules with same name are not allowed by OPA ('allow' rule)
        self.assertRaises(OPAValidationError, opa_client.create_policy, test_name, type(self).test_rego_policy_path)

        with open(type(self).test_rego_policy_path) as test_policy:
            self.assertRaises(OPAValidationError, opa_client.create_policy, test_name, test_policy)
