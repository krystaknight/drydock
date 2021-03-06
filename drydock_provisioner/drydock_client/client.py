# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""REST client for Drydock API."""

import logging

from drydock_provisioner import error as errors


class DrydockClient(object):
    """"
    A client for the Drydock API

    :param DrydockSession session: A instance of DrydockSession to be used by this client
    """

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def get_nodes(self):
        """Get list of nodes in MaaS and their status."""
        endpoint = 'v1.0/nodes'

        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def get_tasks(self):
        """
        Get a list of all the tasks, completed or running.

        :return: List of string uuid task IDs
        """

        endpoint = "v1.0/tasks"

        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def get_task(self, task_id):
        """
        Get the current description of a Drydock task

        :param string task_id: The string uuid task id to query
        :return: A dict representing the current state of the task
        """

        endpoint = "v1.0/tasks/%s" % (task_id)

        resp = self.session.get(endpoint)

        self._check_response(resp)

        return resp.json()

    def create_task(self, design_ref, task_action, node_filter=None):
        """
        Create a new task in Drydock

        :param string design_ref: A URI reference to the design documents for this task
        :param string task_action: The action that should be executed
        :param dict node_filter: A filter for narrowing the scope of the task. Valid fields are 'node_names',
                                 'rack_names', 'node_tags'.
        :return: The dictionary representation of the created task
        """

        endpoint = 'v1.0/tasks'

        task_dict = {
            'action': task_action,
            'design_ref': design_ref,
            'node_filter': node_filter,
        }

        self.logger.debug("drydock_client is calling %s API: body is %s" %
                          (endpoint, str(task_dict)))

        resp = self.session.post(endpoint, data=task_dict)

        self._check_response(resp)

        return resp.json()

    def _check_response(self, resp):
        if resp.status_code == 401:
            raise errors.ClientUnauthorizedError(
                "Unauthorized access to %s, include valid token." % resp.url)
        elif resp.status_code == 403:
            raise errors.ClientForbiddenError(
                "Forbidden access to %s" % resp.url)
        elif not resp.ok:
            raise errors.ClientError(
                "Error - received %d: %s" % (resp.status_code, resp.text),
                code=resp.status_code)
