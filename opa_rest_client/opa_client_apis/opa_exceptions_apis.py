import json
import logging
import sys
from functools import singledispatch
from http import HTTPStatus
import requests.exceptions

from magen_logger.logger_config import LogDefaults
from magen_rest_apis.rest_return_api import RestReturn

LOGGER = logging.getLogger(LogDefaults.default_log_name)


@singledispatch
def handle_specific_exception(err):
    """
    Handles exceptions for the REST APIs functions.
    This function is overloaded with specific functions
    for the most important types of exceptions
    :return: Rest return object
    """
    LOGGER.error('Unexpected Error. Error: %s', sys.exc_info()[0])
    success = False
    message = err.args[0]
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    rest_return_obj = RestReturn(success=success, message=message, http_status=http_status,
                                 json_body=None,
                                 response_object=None)
    return rest_return_obj


@handle_specific_exception.register(requests.exceptions.HTTPError)
def http_error(err):
    """Handles specific exception requests.exceptions.HTTPError"""
    success = False
    http_status = err.response.status_code
    message = err.response.reason
    json_body = err.response.json()
    LOGGER.error(
        'HTTP Error. Error: %s', http_status)
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=json_body,
                                 response_object=err.response)
    return rest_return_obj


@handle_specific_exception.register(requests.exceptions.ReadTimeout)
@handle_specific_exception.register(requests.exceptions.ConnectTimeout)
def read_connect_timeout(err):
    """Handles specific exception requests.exceptions.ReadTimeout requests.exceptions.ConnectTimeout"""
    LOGGER.error(
        'Server too slow. Error: %s', err)
    success = False
    message = HTTPStatus.SERVICE_UNAVAILABLE.phrase
    http_status = HTTPStatus.SERVICE_UNAVAILABLE
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(requests.exceptions.ConnectionError)
def connection_error(err):
    """Handles specific exception requests.exceptions.ConnectionError"""
    LOGGER.error('ConnectionError. Error: %s', err)
    success = False
    message = HTTPStatus.SERVICE_UNAVAILABLE.phrase
    http_status = HTTPStatus.SERVICE_UNAVAILABLE
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(requests.exceptions.InvalidURL)
def invalid_url(err):
    """Handles specific exception requests.exceptions.InvalidURL"""
    LOGGER.error('InvalidURL. Error: %s', err)
    success = False
    message = HTTPStatus.NOT_FOUND.phrase
    http_status = HTTPStatus.NOT_FOUND
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(json.JSONDecodeError)
def json_decode_error(err):
    """Handles specific exception json.JSONDecodeError"""
    LOGGER.error(
        'JSONDecodeError. Error: %s', err)
    success = False
    message = HTTPStatus.INTERNAL_SERVER_ERROR.phrase
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(FileExistsError)
def file_exists_error(err):
    """Handles specific exception requests.exceptions.FileExistsError"""
    LOGGER.error('FileExistsError. Error: %s', err)
    success = False
    message = HTTPStatus.CONFLICT.phrase
    http_status = HTTPStatus.CONFLICT
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(EOFError)
def eof_error(err):
    """Handles specific exception requests.exceptions.EOFError"""
    LOGGER.error('EOFError. Error: %s', err)
    success = False
    message = HTTPStatus.BAD_REQUEST.phrase
    http_status = HTTPStatus.BAD_REQUEST
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(FileNotFoundError)
def file_not_found_error(err):
    """Handles specific exception requests.exceptions.FileNotFoundError"""
    LOGGER.error('FileNotFoundError. Error: %s', err)
    success = False
    message = HTTPStatus.NOT_FOUND.phrase
    http_status = HTTPStatus.NOT_FOUND
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj


@handle_specific_exception.register(IndexError)
def index_error(err):
    """Handles specific exception requests.exceptions.IndexError"""
    LOGGER.error('IndexError. Error: %s', err)
    success = False
    message = HTTPStatus.BAD_REQUEST.phrase
    http_status = HTTPStatus.BAD_REQUEST
    rest_return_obj = RestReturn(success=success, message=message,
                                 http_status=http_status, json_body=None, response_object=None)
    return rest_return_obj