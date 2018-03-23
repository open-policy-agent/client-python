import json
import logging
from functools import singledispatch
from http import HTTPStatus
from io import TextIOWrapper

import os
from requests import exceptions

from magen_logger.logger_config import LogDefaults
from magen_rest_apis.rest_client_apis import RestClientApis

logger = logging.getLogger(LogDefaults.default_log_name)


@singledispatch
def create_opa_policy(policy, url):
    """
    This function creates a OPA policy on the server
    :param url: url address where policy is placed
    :param file_path: .rego file path or a raw rego string
    :return: Rest Return
    """
    if os.path.isfile(policy):
        with open(policy, 'r') as file:
            policy_data = file.read()
            policy_resp = RestClientApis.http_put_and_check_success(url,
                                                                    policy_data, headers={'Content-Type': 'text/plain'})
        return policy_resp
    else:
        # we are going to treat it as a raw string and hope for the best.
        policy_resp = RestClientApis.http_put_and_check_success(url,
                                                                policy, headers={'Content-Type': 'text/plain'})
        return policy_resp


@create_opa_policy.register(TextIOWrapper)
def create_opa_policy(file_handle, url):
    """
    This function creates a OPA policy on the server
    :param url: url address where policy is placed
    :param file_handle: .rego file handle
    :return: Rest Return
    """
    policy_data = file_handle.read()
    policy_resp = RestClientApis.http_put_and_check_success(url,
                                                            policy_data, headers={'Content-Type': 'text/plain'},
                                                            )
    if policy_resp.http_status != HTTPStatus.OK:
        raise exceptions.HTTPError(policy_resp.message)
    return policy_resp


def create_opa_base_doc(url, json_data):
    """
    This function creates a OPA policy on the server
    :param url: url address where base document is placed
    :param json_data: Json data for Base Document
    :return: Rest Return
    """
    resp = RestClientApis.http_put_and_check_success(url, json_data)
    return resp.success, resp.message


def delete_opa_base_doc(url):
    """
    This function deletes a OPA base doc on the server
    :param url: url address where base document is placed
    :param json_data: Json data for Base Document
    :return: Rest Return
    """
    data = json.dumps(dict())
    resp = RestClientApis.http_put_and_check_success(url, data)
    return resp.success, resp.message

def delete_policy(url):
    resp = RestClientApis.http_delete_and_check_success(url)
    if resp.http_status != HTTPStatus.OK:
        raise exceptions.HTTPError(resp.message)
    return


def base_doc_add(url, path, json_value):
    return


def base_doc_remove(url, path):
    return