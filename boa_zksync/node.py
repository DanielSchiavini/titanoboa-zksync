import logging
import sys
from subprocess import Popen

from boa.rpc import EthereumRPC

from boa_zksync.util import stop_subprocess, find_free_port, wait_url


class EraTestNode(EthereumRPC):
    def __init__(self, rpc: EthereumRPC, block_identifier="safe"):
        self._inner_url = rpc._rpc_url

        port = find_free_port()
        fork_at = [
            "--fork-at",
            block_identifier
        ] if isinstance(block_identifier, int) else []
        self._test_node = Popen([
            "era_test_node",
            "--port",
            f"{port}",
            "fork",
            self._inner_url,
        ] + fork_at, stdout=sys.stdout, stderr=sys.stderr)

        super().__init__(f"http://localhost:{port}")
        logging.info(f"Started fork node at {self._rpc_url}")
        wait_url(self._rpc_url)

    @property
    def inner_url(self):
        return self._inner_url

    def __del__(self):
        stop_subprocess(self._test_node)