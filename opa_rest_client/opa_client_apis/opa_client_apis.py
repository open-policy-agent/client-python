import logging
import json
from http import HTTPStatus
from requests import exceptions

from magen_logger.logger_config import LogDefaults
from magen_rest_apis.rest_client_apis import RestClientApis
from magen_rest_apis.rest_return_api import RestReturn
from opa_rest_client.opa_client_apis.opa_exceptions_apis import handle_specific_exception

logger = logging.getLogger(LogDefaults.default_log_name)


def known_exceptions(func):
    """
    Known Exceptions decorator.
    wraps a given function into try-except statement
    :param func: function to decorate
    :type func: Callable
    :return: decorated
    :rtype: Callable
    """
    def helper(*args, **kwargs):
        """Actual Decorator for handling known exceptions"""
        try:
            return func(*args, **kwargs)
        except (exceptions.RequestException, FileExistsError, FileNotFoundError, EOFError, IndexError,
                json.JSONDecodeError) as err:
            return handle_specific_exception(err)
        except TypeError as err:
            success = False
            return RestReturn(success=success, message=err.args[0])
    return helper


@known_exceptions
def create_opa_policy(url, file_path):
    """
    This function creates a OPA policy on the server
    :param url: url address where policy is placed
    :param file_path: .rego file path
    :return: Rest Return
    """
    policy_resp = None
    with open(file_path, 'r') as file:
        policy_data = file.read()
        policy_resp = RestClientApis.http_put_and_check_success(url,
                                                                policy_data, headers={'Content-Type': 'text/plain'},
                                                                params={'file': file_path})
        if policy_resp.http_status != HTTPStatus.OK:
            raise exceptions.HTTPError(policy_resp.message)
    return policy_resp


@known_exceptions
def create_opa_base_doc(url, json_data):
    """
    This function creates a OPA policy on the server
    :param url: url address where base document is placed
    :param json_data: Json data for Base Document
    :return: Rest Return
    """
    resp = RestClientApis.http_put_and_check_success(url, json_data, headers={'Content-Type': 'application/json'})
    if resp.http_status != HTTPStatus.OK:
        raise json.JSONDecodeError(resp.message)
    return resp


@known_exceptions
def delete_policy(url):
    resp = RestClientApis.http_delete_and_check_success(url)
    if resp.http_status != HTTPStatus.OK:
        raise exceptions.HTTPError(resp.message)
    return


@known_exceptions
def base_doc_add(url, path, json_value):
    return


@known_exceptions
def base_doc_remove(url, path):
    return