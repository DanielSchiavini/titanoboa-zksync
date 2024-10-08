import os

import boa
import pytest
from eth_account import Account

import boa_zksync
from boa_zksync import EraTestNode
from boa_zksync.deployer import ZksyncDeployer
from boa.deployments import DeploymentsDB, set_deployments_db

STARTING_SUPPLY = 100


@pytest.fixture(scope="module")
def zksync_env(account):
    old_env = boa.env
    boa_zksync.set_zksync_test_env()
    boa.env.add_account(account, force_eoa=True)
    yield boa.env
    boa.set_env(old_env)


@pytest.fixture(scope="module")
def zksync_sepolia_fork(account):
    old_env = boa.env
    fork_url = os.getenv("FORK_URL", "https://sepolia.era.zksync.dev")
    boa_zksync.set_zksync_fork(
        fork_url,
        block_identifier=3000000,
        node_args=("--show-calls", "all", "--show-outputs", "true"),
    )
    boa.env.add_account(account, force_eoa=True)
    yield boa.env
    boa.set_env(old_env)


@pytest.fixture(scope="module")
def account():
    # default rich account from era_test_node
    _public_key, private_key = EraTestNode.TEST_ACCOUNTS[0]
    return Account.from_key(private_key)


@pytest.fixture(scope="module")
def simple_contract(zksync_env):
    code = """
totalSupply: public(uint256)
balances: HashMap[address, uint256]

@deploy
def __init__(t: uint256):
    self.totalSupply = t
    self.balances[self] = t

@external
def update_total_supply(t: uint16) -> uint256:
    self.totalSupply += convert(t, uint256)
    return self.totalSupply

@external
def raise_exception(t: uint256):
    raise "oh no!"
"""
    return boa.loads(code, STARTING_SUPPLY, name="SimpleContract")


@pytest.fixture(scope="module")
def zksync_env_with_db(account):
    old_env = boa.env
    boa_zksync.set_zksync_test_env()
    boa.env.add_account(account, force_eoa=True)

    db = DeploymentsDB(":memory:")

    with set_deployments_db(db):
        yield boa.env

    boa.set_env(old_env)


@pytest.fixture(scope="module")
def zksync_deployer(zksync_env_with_db) -> ZksyncDeployer:
    from tests.data import Counter

    return Counter
