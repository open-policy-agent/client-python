import json
import logging

import os

from magen_logger.logger_config import LogDefaults
from magen_rest_apis.rest_client_apis import RestClientApis
from multiprocessing import Process

from requests.exceptions import ChunkedEncodingError

from opa_rest_client.opa_watch import OpaWatch

DEBUG_QUERY_STRING = "?explain=full&pretty"
WATCH_QUERY_STRING = "?watch&pretty=true"

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


def patch_base_doc(url, json_data):
    resp = RestClientApis.http_patch_and_check_success(url, json_data,
                                                       headers={'Content-Type': 'application/json-patch+json'})
    return resp.success, resp.message


def delete_all_base_data_doc(url, debug=False):
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


def delete_base_doc(url, debug=False):
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


def get_base_doc(url, debug=False):
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


def delete_policy(url, debug=False):
    if debug:
        url = url + DEBUG_QUERY_STRING
    resp = RestClientApis.http_delete_and_check_success(url)
    return resp.success, resp.message, resp.json_body


def delete_all_policies(url, debug=False):
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


def create_watch(url, callback=None):
    """
    Creates a watch in OPA. Watches are persistent connections and changes to the watch points
    are streamed back through chunked-encoding.
    :param url:
    :param callback:
    :return:
    """
    orig_url = url
    url = url + WATCH_QUERY_STRING
    resp_obj = RestClientApis.http_get_and_check_success(url, stream=True, timeout=(2.0, None))
    p = Process(target=process_watch_stream, args=(resp_obj.response_object,))
    p.start()
    opa_watch = OpaWatch(orig_url, p, p.pid)
    return resp_obj.success, resp_obj.message, opa_watch


def destroy_watch(opa_watch_cls):
    opa_watch_cls.proc.terminate()
    opa_watch_cls.proc.join()


def execute_query(url, json_data):
    resp_obj = RestClientApis.http_post_and_check_success(url, json_data, location=False)
    return resp_obj.success, resp_obj.message, resp_obj.json_body


def execute_adhoc_query(url, json_data):
    resp_obj = RestClientApis.http_post_and_check_success(url, json_data, location=False)
    return resp_obj.success, resp_obj.message, resp_obj.json_body




