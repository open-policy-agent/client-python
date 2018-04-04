# coding=uft-8
"""
Open Policy Client module.

Represents a class with fabric methods to create policy and data objects.
"""

import os
import json
import urllib

from http import HTTPStatus
from magen_rest_apis.rest_client_apis import RestClientApis
from multiprocessing import Process

from requests.exceptions import ChunkedEncodingError

from opa_rest_client.opa_watch import OpaWatch
from magen_rest_apis.rest_return_api import RestReturn

from opa_rest_client.policy import Policy
from opa_rest_client.config import INVALID_REGO_ERROR

DEBUG_QUERY_STRING = "?explain=full&pretty"
WATCH_QUERY_STRING = "?watch&pretty=true"


def read_from_file(file_path):
    with open(file_path) as file:
        blob = file.read()
    return blob


class OPAValidationError(Exception):
    pass


class OPAClient(object):

    def __init__(self, server='localhost', port=8181, **kwargs):
        self.server = server
        self.port = str(port)
        api_version = kwargs.pop('api_version') or 'v1'
        self.base = 'http://' + self.server + ':' + self.port + '/' + api_version

    def create_policy(self, name, rego_policy):
        def validate():
            words = name.split('/')
            valid_words = [x for x in words if x.isalpha()]
            if len(words) != len(valid_words):
                raise OPAValidationError('only slashes and letters are acceptable in policy name')
        validate()
        policy_url = self.base + 'policies' + name
        if os.path.isfile(rego_policy):
            rego_policy = read_from_file(rego_policy)

        rest_response = RestClientApis.http_put_and_check_success(policy_url,
                                                                  rego_policy, headers={'Content-Type': 'text/plain'})

        rest_json = rest_response.json_body
        if rest_response.http_status == HTTPStatus.BAD_REQUEST and rest_json.get('code') == INVALID_REGO_ERROR:
            raise OPAValidationError(rest_json.get('errors', {}).get('message', 'Invalid or Empty REGO'))

        if rest_response.http_status == HTTPStatus.OK and not rest_json:
            return Policy(policy_name=name, policy_path=policy_url, rego_contents=rego_policy)


def create_opa_policy(url: str, policy):
    """
    This function creates a OPA policy on the server
    :param url: url address where policy is placed
    :param file_path: .rego file path or a raw rego string
    :return: RestReturn
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


def create_opa_base_doc(url, json_data):
    """
    This function creates a OPA policy on the server
    :param url: url address where base document is placed
    :param json_data: Json data for Base Document
    :return: success, message
    :rtype: tuple
    """
    resp = RestClientApis.http_put_and_check_success(url, json_data)
    return resp.success, resp.message


def patch_base_doc(url: str, json_data: str) -> (bool, str):
    """
    Patches a base document.
    :param url: URL of resource to be patched
    :param json_data: JSON data as string
    :return: success and message
    :rtype: tuple
    """
    resp = RestClientApis.http_patch_and_check_success(url, json_data,
                                                       headers={'Content-Type': 'application/json-patch+json'})
    return resp.success, resp.message


def delete_all_base_data_doc(url: str, debug=False):
    """
    This function deletes all OPA base docs on the server
    :param url: url address where base document is placed
    :return: success, message
    :rtype: tuple
    """
    if debug:
        url = url + DEBUG_QUERY_STRING
    data = json.dumps(dict())
    resp = RestClientApis.http_put_and_check_success(url, data)
    return resp.success, resp.message


def delete_base_doc(url: str, debug=False):
    """
    This function deletes an OPA base doc on the server
    :param url: url address where base document is placed
    :return: success, message
    :rtype: tuple
    """
    if debug:
        url = url + DEBUG_QUERY_STRING
    resp = RestClientApis.http_delete_and_check_success(url)
    return resp.success, resp.message


def get_base_doc(url: str, debug=False) -> (object):
    """
    This function gets an OPA base doc on the server
    :param url: url address where base document is placed
    :return: RestReturn Obj
    :rtype: RestReturn
    """
    if debug:
        url = url + DEBUG_QUERY_STRING
    resp = RestClientApis.http_get_and_check_success(url)
    return resp


def delete_policy(url: str, debug=False) -> (bool, str, dict):
    if debug:
        url = url + DEBUG_QUERY_STRING
    resp = RestClientApis.http_delete_and_check_success(url)
    return resp.success, resp.message, resp.json_body


def delete_all_policies(url: str, debug=False):
    """
    This function deletes all OPA base docs on the server
    :param url: url address where base document is placed
    :return: success, message
    :rtype: tuple
    """
    if debug:
        url = url + DEBUG_QUERY_STRING
    data = json.dumps(dict())
    resp = RestClientApis.http_put_and_check_success(url, data)
    return resp.success, resp.message


def read_chunks(resp):
    buf = ""
    try:
        for chunk in resp.iter_content(chunk_size=None):
            if chunk.endswith(b"\n"):
                buf += chunk.decode("utf-8")
                yield buf
                buf = ""
            else:
                buf += chunk
    except ChunkedEncodingError as e:
        # Nothing to do, connection terminated.
        pass


def process_watch_stream(resp):
    with open("watch_stream.txt", "wb+") as f:
        f.seek(0)
        for buf in read_chunks(resp):
            f.write(buf.encode("utf-8"))
            f.flush()


def create_watch(url: str) -> (bool, str, OpaWatch):
    """
    Creates a watch in OPA. Watches are persistent connections and changes to the watch points
    are streamed back through chunked-encoding.
    :param url: URL for resource to watch
    :return: success, message, OpaWatch class
    :rtype: tuple(bool, message, OpaWatch)
    """
    orig_url = url
    url = url + WATCH_QUERY_STRING
    resp_obj = RestClientApis.http_get_and_check_success(url, stream=True, timeout=(2.0, None))
    p = Process(target=process_watch_stream, args=(resp_obj.response_object,))
    p.start()
    opa_watch = OpaWatch(orig_url, p, p.pid)
    return resp_obj.success, resp_obj.message, opa_watch


def destroy_watch(opa_watch_cls: OpaWatch):
    opa_watch_cls.proc.terminate()
    opa_watch_cls.proc.join()


def execute_query(url: str, json_data: str) -> (bool, str, dict):
    """

    :param url: URL for query
    :param json_data: JSON in string format.
    :return: success, message and json body in dict
    :rtype: tuple(bool, str, dict)
    """
    resp_obj = RestClientApis.http_post_and_check_success(url, json_data, location=False)
    return resp_obj.success, resp_obj.message, resp_obj.json_body


def execute_adhoc_query(url: str, query_string: str=None) -> (bool, str, dict):
    """
    Executed an ad-hoc query
    :param query_string: Everything after the ?=
    :param url: URL for query that includes the query string
    :return: success, message and json body as dict
    :rtype: tuple(bool, str, dict)
    """
    if query_string:
        enc_query_string = urllib.parse.quote_plus(query_string)
        url = url + "?q=" + enc_query_string
    resp_obj = RestClientApis.http_get_and_check_success(url)
    return resp_obj.success, resp_obj.message, resp_obj.json_body
