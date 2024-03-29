# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This contains the proxy agent class."""

import sys
from queue import Queue
from typing import Optional

import gym

from aea.agent import Agent
from aea.helpers.base import locate
from aea.mail.base import Envelope, MailBox

sys.modules["gym_connection"] = locate("packages.connections.gym")
from gym_connection.connection import GymConnection  # noqa: E402


class ProxyAgent(Agent):
    """This class implements a proxy agent to be used by a proxy environment."""

    def __init__(self, name: str, gym_env: gym.Env, proxy_env_queue: Queue) -> None:
        """
        Instantiate the agent.

        :param name: the name of the agent
        :param gym_env: gym environment
        :param proxy_env_queue: the queue of the proxy environment
        :return: None
        """
        super().__init__(name, timeout=0)
        self.proxy_env_queue = proxy_env_queue
        self.mailbox = MailBox(GymConnection(self.crypto.public_key, gym_env))

    def setup(self) -> None:
        """
        Set up the agent.

        :return: None
        """
        pass

    def act(self) -> None:
        """
        Perform actions.

        :return: None
        """
        pass

    def react(self) -> None:
        """
        React to incoming events.

        :return: None
        """
        while not self.inbox.empty():
            envelope = self.inbox.get_nowait()  # type: Optional[Envelope]
            if envelope is not None:
                self.proxy_env_queue.put(envelope)

    def update(self) -> None:
        """Update the current state of the agent.

        :return None
        """
        pass

    def teardown(self) -> None:
        """
        Tear down the agent.

        :return: None
        """
        pass
