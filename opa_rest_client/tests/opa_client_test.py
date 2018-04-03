#! /usr/bin/python3
"""
Test Suit for AppGuard GitHub Integration
"""
import json
import unittest
import urllib

import docker
import sys

from magen_utils_apis.compare_utils import compare_dicts

from opa_rest_client.opa_client_apis import create_opa_policy, create_base_doc, delete_base_doc, get_base_doc, \
    delete_policy, patch_base_doc, create_watch, delete_all_policies, destroy_watch, execute_query, execute_adhoc_query, \
    DEBUG_QUERY_STRING
from opa_rest_client.opa_docker_apis import run_opa_docker_container
from opa_rest_client.tests.opa_client_test_messages import EXAMPLE_DATA, EXAMPLE_POLICY, OPA_EMPTY_RESP, \
    PATCH_DATA_SERVERS_ADD, PATCH_DATA_SERVERS_REMOVE, EXAMPLE_POLICY_WITH_INPUT, POST_WITH_INPUT_REQ, \
    POST_WITH_INPUT_RESP, POST_WITHOUT_URL, EXAMPLE_SYSTEM_POLICY, ADHOC_QUERY_RESP

__author__ = "Reinaldo Penno"
__license__ = "Apache"
__version__ = "0.1"
__email__ = "rapenno@gmail.com"


class TestOpaClient(unittest.TestCase):
    docker_client = client = docker.from_env()
    opa_container = None
    base_url = "http://localhost:8181"
    base_query_url = "http://localhost:8181/v1/query"
    base_doc_url = "http://localhost:8181/v1/data"
    base_policies_url = "http://localhost:8181/v1/policies"

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

    def setUp(self):
        """
        This function prepares the system for running tests
        """
        pass

    def tearDown(self):
        pass

    def test_create_policy(self):
        pass

    def clean_base_doc(self):
        success, message = delete_base_doc(type(self).base_doc_url + "/networks")
        self.assertTrue(success)
        success, message = delete_base_doc(type(self).base_doc_url + "/ports")
        self.assertTrue(success)
        success, message = delete_base_doc(type(self).base_doc_url + "/servers")
        self.assertTrue(success)
        resp = get_base_doc(type(self).base_doc_url)
        self.assertTrue(resp.success)
        expected_resp = json.loads(OPA_EMPTY_RESP)
        success = compare_dicts(resp.json_body, expected_resp)
        self.assertTrue(success)

    def test_create_data_doc(self):
        success, message = create_base_doc(type(self).base_doc_url, EXAMPLE_DATA)
        self.assertTrue(success)
        self.clean_base_doc()

    def test_create_data_and_policy(self):
        success, message = create_base_doc(type(self).base_doc_url, EXAMPLE_DATA)
        self.assertTrue(success)
        success, message = create_opa_policy(type(self).base_policies_url + "/example1", EXAMPLE_POLICY.encode("utf-8"))
        self.assertTrue(success)
        success, message, json_dict = delete_policy(type(self).base_policies_url + "/example1")
        self.assertTrue(success)
        self.clean_base_doc()

    def test_create_data_and_policy_debug(self):
        success, message = create_base_doc(type(self).base_doc_url, EXAMPLE_DATA)
        self.assertTrue(success)
        success, message = create_opa_policy(type(self).base_policies_url + "/example1", EXAMPLE_POLICY.encode("utf-8"))
        self.assertTrue(success)
        success, message, json_dict = delete_policy(type(self).base_policies_url + "/example1", debug=True)
        self.assertTrue(success) and self.assertTrue("metrics" in json_dict)
        self.clean_base_doc()

    def test_watch(self):
        success, message = create_base_doc(type(self).base_doc_url, EXAMPLE_DATA)
        self.assertTrue(success)
        success, message = create_opa_policy(type(self).base_policies_url + "/example1", EXAMPLE_POLICY.encode("utf-8"))
        self.assertTrue(success)
        success, message, watch_cls = create_watch(type(self).base_doc_url + "/servers")
        self.assertTrue(success)
        success, message = patch_base_doc(type(self).base_doc_url + "/servers", PATCH_DATA_SERVERS_ADD)
        self.assertTrue(success)
        success, message = patch_base_doc(type(self).base_doc_url + "/servers", PATCH_DATA_SERVERS_REMOVE)
        self.assertTrue(success)
        success, message, json_dict = delete_policy(type(self).base_policies_url + "/example1", debug=True)
        self.assertTrue(success)
        destroy_watch(watch_cls)
        self.clean_base_doc()

    def test_query_with_input(self):
        success, message = create_opa_policy(type(self).base_policies_url + "/example1",
                                             EXAMPLE_POLICY_WITH_INPUT.encode("utf-8"))
        self.assertTrue(success)
        success, message, json_dict = execute_query(type(self).base_doc_url + "/opa/examples/allow_request",
                                                    POST_WITH_INPUT_REQ)
        self.assertTrue(success)
        expected_resp = json.loads(POST_WITH_INPUT_RESP)
        success = compare_dicts(json_dict, expected_resp)
        self.assertTrue(success)

    def test_unversioned_query(self):
        success, _, _ = execute_query(type(self).base_url + "/", POST_WITHOUT_URL)
        self.assertFalse(success)
        success, message = create_opa_policy(type(self).base_policies_url + "/example1",
                                             EXAMPLE_SYSTEM_POLICY.encode("utf-8"))
        self.assertTrue(success)
        success, message, json_dict = execute_query(type(self).base_url + "/",
                                                    POST_WITHOUT_URL)
        self.assertTrue(success)
        self.assertEqual("hello, alice", json_dict)

    def test_adhoc_query(self):
        query_string = urllib.parse.quote_plus("data.servers[i].ports[_] = \"p2\"; data.servers[i].name = name")
        adhoc_query_url = type(self).base_query_url + "?q=" + query_string
        success, message = create_base_doc(type(self).base_doc_url, EXAMPLE_DATA)
        self.assertTrue(success)
        success, message = create_opa_policy(type(self).base_policies_url + "/example1", EXAMPLE_POLICY.encode("utf-8"))
        self.assertTrue(success)
        # adhoc query
        success, message, json_body = execute_adhoc_query(adhoc_query_url)
        self.assertTrue(success)
        expected_resp = json.loads(ADHOC_QUERY_RESP)
        success = compare_dicts(json_body, expected_resp)
        self.assertTrue(success)
        success, message, json_dict = delete_policy(type(self).base_policies_url + "/example1")
        self.assertTrue(success)
        self.clean_base_doc()