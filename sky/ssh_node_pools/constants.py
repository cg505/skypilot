"""Constants for SSH Node Pools"""
# pylint: disable=line-too-long
import os

from sky.utils import common_utils

DEFAULT_KUBECONFIG_PATH = os.path.expanduser('~/.kube/config')
SSH_CONFIG_PATH = os.path.expanduser('~/.ssh/config')
NODE_POOLS_INFO_DIR = common_utils.get_sky_dir('ssh_node_pools_info')
NODE_POOLS_KEY_DIR = common_utils.get_sky_dir('ssh_keys')
DEFAULT_SSH_NODE_POOLS_PATH = common_utils.get_sky_dir('ssh_node_pools.yaml')

# TODO (kyuds): make this configurable?
K3S_TOKEN = 'mytoken'  # Any string can be used as the token
