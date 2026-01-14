"""Runtime utilities for SkyPilot."""
import os

from sky.skylet import constants


def get_runtime_dir_path(path_suffix: str = '') -> str:
    """Get an expanded path within the SkyPilot runtime directory.

    Supports multi-instance development via SKYPILOT_INSTANCE_ID env var.
    When set, creates isolated state directories for each instance.

    Priority order:
    1. SKY_RUNTIME_DIR env var (for Slurm/special environments)
    2. SKYPILOT_INSTANCE_ID env var (for multi-instance local dev)
    3. Default home directory

    Args:
        path_suffix: Path suffix to join with the runtime dir
        (e.g., '.sky/jobs.db').

    Returns:
        The full expanded path.
    """
    # Check for explicit runtime dir override first (highest priority)
    runtime_dir_override = os.environ.get(constants.SKY_RUNTIME_DIR_ENV_VAR_KEY)
    if runtime_dir_override:
        runtime_dir = os.path.expanduser(runtime_dir_override)
    else:
        runtime_dir = os.path.expanduser('~')
        # Check for instance ID for multi-instance dev support
        instance_id = os.environ.get('SKYPILOT_INSTANCE_ID', '')
        if instance_id and path_suffix:
            # Transform .sky paths to .sky-dev-{instance_id} paths
            if path_suffix.startswith('.sky/'):
                path_suffix = f'.sky-dev-{instance_id}/{path_suffix[5:]}'
            elif path_suffix.startswith('.sky'):
                path_suffix = f'.sky-dev-{instance_id}{path_suffix[4:]}'

    if path_suffix:
        return os.path.join(runtime_dir, path_suffix)
    return runtime_dir
