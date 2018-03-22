import time
from docker.errors import NotFound

__author__ = "Reinaldo Penno"
__version__ = "0.1"
__status__ = "alpha"
__email__ = "rapenno@gmail.com"


def run_opa_docker_container(docker_client):
    """
    We will use this function for system testing
    :param docker_client: Docker client handle
    :type docker_client:
    :return: docker container handle
    :rtype: string
    """
    # if there is no image we pull it
    try:
        opa_image = docker_client.images.get("openpolicyagent/opa")
    except NotFound as e:
        opa_image = docker_client.images.pull("openpolicyagent/opa", tag="latest")

    assert opa_image is not None

    # if container is not running we will start it
    try:
        opa_container = docker_client.containers.get("appguard_opa")
        if opa_container.status == "exited" or (opa_container.status == "created"):
            opa_container.remove()
            raise NotFound("Container Exited or could not be started")
    except NotFound as e:
        print("OPA docker container not found or not running\n")
        opa_container = docker_client.containers.run("openpolicyagent/opa",
                                                     command="run --server --log-level=debug",
                                                     name="appguard_opa",
                                                     ports={"8181/tcp": 8181}, detach=True)
        time.sleep(5)

    assert opa_container.status == "running" or (opa_container.status == "created"
                                                 and not opa_container.attrs["State"]["Error"])
    return opa_container

