OPA_EMPTY_RESP = """
{
  "result": {}
}
"""


EXAMPLE_DATA = """
{
  "servers": [
    {
      "id": "s1",
      "name": "app",
      "protocols": [
        "https",
        "ssh"
      ],
      "ports": [
        "p1",
        "p2",
        "p3"
      ]
    },
    {
      "id": "s2",
      "name": "db",
      "protocols": [
        "mysql"
      ],
      "ports": [
        "p3"
      ]
    },
    {
      "id": "s3",
      "name": "cache",
      "protocols": [
        "memcache",
        "http"
      ],
      "ports": [
        "p3"
      ]
    },
    {
      "id": "s4",
      "name": "dev",
      "protocols": [
        "http"
      ],
      "ports": [
        "p1",
        "p2"
      ]
    }
  ],
  "networks": [
    {
      "id": "n1",
      "public": false
    },
    {
      "id": "n2",
      "public": false
    },
    {
      "id": "n3",
      "public": true
    }
  ],
  "ports": [
    {
      "id": "p1",
      "networks": [
        "n1"
      ]
    },
    {
      "id": "p2",
      "networks": [
        "n3"
      ]
    },
    {
      "id": "p3",
      "networks": [
        "n2"
      ]
    }
  ]
}
"""

EXAMPLE_POLICY = """
# This policy module belongs to the opa.examples package.
package opa.examples

# Refer to data.servers as `servers`.
import data.servers
# Refer to the data.networks as `networks`.
import data.networks
# Refer to the data.ports as `ports`.
import data.ports

# A server exists in the violations set if...
violations[server] {
    # ...the server exists
    server = servers[_]
    # ...and any of the server’s protocols is HTTP
    server.protocols[_] = "http"
    # ...and the server is public.
    public_servers[server] = true
}

# A server exists in the public_servers set if...
public_servers[server] {
    # ...the server exists
    server = servers[_]
    # ...and the server is connected to a port
    server.ports[_] = ports[i].id
    # ...and the port is connected to a network
    ports[i].networks[_] = networks[j].id
    # ...and the network is public.
    networks[j].public = true
}
"""

PATCH_DATA_SERVERS_ADD = """
[
  {
    "op": "add",
    "path": "-",
    "value": {
      "id": "s5",
      "name": "job",
      "protocols": [
        "amqp"
      ],
      "ports": [
        "p3"
      ]
    }
  }
]
"""

PATCH_DATA_SERVERS_REMOVE = """
[
    {
     "op": "remove",
     "path": "1"
    }
]
"""
