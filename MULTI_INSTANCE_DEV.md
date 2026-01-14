# Multi-Instance Development Setup for SkyPilot

This guide explains how to run multiple isolated SkyPilot instances locally for development.

## Overview

The multi-instance development setup allows you to:
- Run multiple isolated SkyPilot instances simultaneously
- Each instance has its own state directory, databases, and config
- Each instance runs its API server on a different port
- Perfect for testing, parallel development, or comparing versions

## Quick Start

### 1. Use the wrapper scripts

Two wrapper scripts are provided in the repository root:

- **`sky-dev`**: Run any sky command with a specific instance
- **`sky-dev-api`**: Manage API servers for dev instances

### 2. Basic Usage

```bash
# Run commands with instance 1
./sky-dev 1 sky status
./sky-dev 1 sky launch my-task.yaml

# Run commands with instance 2
./sky-dev 2 sky status
./sky-dev 2 sky launch other-task.yaml

# Manage API servers
./sky-dev-api 1 start    # Start API server for instance 1 (port 46581)
./sky-dev-api 2 start    # Start API server for instance 2 (port 46582)
./sky-dev-api 1 status   # Check instance 1's API server status
./sky-dev-api 1 stop     # Stop API server for instance 1
```

## How It Works

### Environment Variables

When you run `./sky-dev <id> <command>`, it sets:

- **`SKYPILOT_INSTANCE_ID`**: The instance identifier
- **`SKYPILOT_API_SERVER_ENDPOINT`**: API server URL (http://127.0.0.1:46580+id)

### State Isolation

Each instance gets its own isolated state directory:

```
~/.sky-dev-0/          # Instance 0 (default instance acts like regular ~/.sky/)
~/.sky-dev-1/          # Instance 1
~/.sky-dev-2/          # Instance 2
├── config.yaml        # Instance-specific config
├── state_db.db        # Cluster state database
├── spot_jobs_db.db    # Managed jobs database
├── serve_db.db        # Serve database
├── api_server/        # API server state
├── locks/             # Lock files
└── ...                # Other instance-specific files
```

### Port Allocation

Each instance's API server runs on a unique port:

- Instance 0: port 46580 (default)
- Instance 1: port 46581
- Instance 2: port 46582
- Instance N: port 46580+N

## Code Changes

The following files were modified to support multi-instance development:

### New Helper Function

**`sky/utils/common_utils.py`**:
- Added `get_sky_dir(subpath)` function that respects `SKYPILOT_INSTANCE_ID`

### Updated Paths

The following modules now use instance-specific directories:

- **Databases**: `sky/utils/db/db_utils.py` via `sky/skylet/runtime_utils.py`
- **Config**: `sky/skypilot_config.py`
- **User hash**: `sky/utils/common_utils.py`
- **Job controller**: `sky/jobs/scheduler.py`, `sky/jobs/constants.py`
- **API server**: `sky/server/constants.py`
- **SSH locks**: `sky/utils/cluster_utils.py`
- **SSH node pools**: `sky/ssh_node_pools/constants.py`
- **Volumes**: `sky/volumes/server/core.py`
- **Users/RBAC**: `sky/users/permission.py`, `sky/users/token_service.py`, `sky/users/server.py`

## Examples

### Running Multiple Dev Environments

```bash
# Terminal 1: Work on feature A with instance 1
./sky-dev-api 1 start
./sky-dev 1 sky launch feature-a.yaml

# Terminal 2: Work on feature B with instance 2
./sky-dev-api 2 start
./sky-dev 2 sky launch feature-b.yaml

# Terminal 3: Test main branch with instance 0
./sky-dev 0 sky status
```

### Testing Different Configurations

```bash
# Instance 1: Test with AWS
./sky-dev 1 bash -c "echo 'cloud: aws' > ~/.sky-dev-1/config.yaml"
./sky-dev 1 sky launch test.yaml

# Instance 2: Test with GCP
./sky-dev 2 bash -c "echo 'cloud: gcp' > ~/.sky-dev-2/config.yaml"
./sky-dev 2 sky launch test.yaml
```

### Python API Usage

You can also use the wrapper with Python scripts:

```bash
./sky-dev 1 python my_sky_script.py
./sky-dev 2 python -m sky.client.sdk
```

## Tips & Best Practices

### 1. Add to PATH (optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/user/skypilot:$PATH"

# Now you can use without ./
sky-dev 1 sky status
sky-dev-api 1 start
```

### 2. Shell Aliases (optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
alias sky1='sky-dev 1 sky'
alias sky2='sky-dev 2 sky'

# Usage
sky1 status
sky2 launch mycluster.yaml
```

### 3. Always Restart API Server After Code Changes

```bash
# After modifying SkyPilot code
./sky-dev-api 1 restart
```

### 4. Clean Up Instances

```bash
# Remove instance state when done
rm -rf ~/.sky-dev-1
rm -rf ~/.sky-dev-2
```

### 5. Check Which Instances Are Running

```bash
# List all instance directories
ls -d ~/.sky-dev-*

# Check which API servers are running
for i in 0 1 2 3 4 5 6 7 8 9; do
    if lsof -i :$((46580 + i)) > /dev/null 2>&1; then
        echo "Instance $i API server is running on port $((46580 + i))"
    fi
done
```

## Limitations

### Remote Cluster Operations

The Skylet gRPC port (46590) is still shared across instances. This means:
- Remote cluster operations work fine
- Multiple instances can connect to different remote clusters
- If two instances try to use the same remote cluster simultaneously, there might be conflicts (but this is rare in practice)

### Claude Code Compatibility

When using with Claude Code:
- Each Claude Code session should use a different instance ID
- Set the instance ID at the start of your development session
- The wrapper ensures complete isolation between sessions

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the port
lsof -i :46581

# Kill the process if needed
kill <PID>

# Or use a different instance ID
./sky-dev 10 sky status  # Uses port 46590
```

### Wrong Instance Directory

If commands seem to use the wrong state:

```bash
# Verify environment variables are set
./sky-dev 1 bash -c 'echo $SKYPILOT_INSTANCE_ID'
./sky-dev 1 bash -c 'echo $SKYPILOT_API_SERVER_ENDPOINT'

# Check the state directory exists
ls -la ~/.sky-dev-1/
```

### API Server Issues

```bash
# Check API server logs
./sky-dev 1 bash -c 'cat ~/.sky-dev-1/api_server/server.log'

# Restart the API server
./sky-dev-api 1 restart
```

## Implementation Details

### Instance ID Resolution

The `SKYPILOT_INSTANCE_ID` environment variable is checked at module import time. The helper function `get_sky_dir()` translates paths:

- Without `SKYPILOT_INSTANCE_ID`: `~/.sky/` (default)
- With `SKYPILOT_INSTANCE_ID=1`: `~/.sky-dev-1/`
- With `SKYPILOT_INSTANCE_ID=2`: `~/.sky-dev-2/`

### Database Paths

The `sky/skylet/runtime_utils.py` module was updated to support instance IDs. It modifies `.sky` paths to `.sky-dev-{id}` when the environment variable is set.

### API Server Port

The API server port is determined by `46580 + INSTANCE_ID`, and the wrapper sets the `SKYPILOT_API_SERVER_ENDPOINT` environment variable accordingly.

## Contributing

If you modify paths in the codebase:
1. Use `common_utils.get_sky_dir(subpath)` for new paths under `~/.sky/`
2. For remote paths, use `runtime_utils.get_runtime_dir_path()`
3. Test with multiple instances to ensure isolation

## Questions?

For issues or questions about multi-instance development:
1. Check this guide first
2. Verify wrapper scripts are executable: `chmod +x sky-dev sky-dev-api`
3. Report issues on GitHub: https://github.com/skypilot-org/skypilot/issues
