#! /usr/bin/python3
"""
Test Suit for AppGuard GitHub Integration
"""

import unittest
import docker
import sys

from opa_rest_client.opa_client_apis.opa_docker_apis import run_opa_docker_container

__author__ = "Reinaldo Penno"
__license__ = "Apache"
__version__ = "0.1"
__email__ = "rapenno@gmail.com"


class TestOpaClient(unittest.TestCase):

    docker_client = client = docker.from_env()
    opa_container = None

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
