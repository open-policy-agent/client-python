import json
import logging

import os

from magen_logger.logger_config import LogDefaults
from magen_rest_apis.rest_client_apis import RestClientApis

logger = logging.getLogger(LogDefaults.default_log_name)


def create_opa_policy(url, policy):
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
        return policy_resp.success, policy_resp.message


def create_base_doc(url, json_data):
    """
    This function creates a OPA policy on the server
    :param url: url address where base document is placed
    :param json_data: Json data for Base Document
    :return: success, message
    :rtype: tuple
    """
    resp = RestClientApis.http_put_and_check_success(url, json_data)
    return resp.success, resp.message


def delete_all_base_data_doc(url):
    """
    This function deletes all OPA base docs on the server
    :param url: url address where base document is placed
    :return: success, message
    :rtype: tuple
    """
    data = json.dumps(dict())
    resp = RestClientApis.http_put_and_check_success(url, data)
    return resp.success, resp.message


def delete_base_doc(url):
    """
    This function deletes an OPA base doc on the server
    :param url: url address where base document is placed
    :return: success, message
    :rtype: tuple
    """
    resp = RestClientApis.http_delete_and_check_success(url)
    return resp.success, resp.message


def get_base_doc(url):
    """
    This function gets an OPA base doc on the server
    :param url: url address where base document is placed
    :return: RestReturn Obj
    :rtype: RestReturn
    """
    resp = RestClientApis.http_get_and_check_success(url)
    return resp


def delete_policy(url):
    resp = RestClientApis.http_delete_and_check_success(url)
    return resp.success, resp.message


def delete_all_policies(url):
    """
    This function deletes all OPA base docs on the server
    :param url: url address where base document is placed
    :return: success, message
    :rtype: tuple
    """
    data = json.dumps(dict())
    resp = RestClientApis.http_put_and_check_success(url, data)
    return resp.success, resp.message
