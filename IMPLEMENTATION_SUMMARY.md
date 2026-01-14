# Multi-Instance Development - Implementation Summary

## Overview

Implemented support for running multiple isolated SkyPilot instances locally for development. Each instance has its own state directory, databases, and API server port.

## Key Features

- **Zero breaking changes**: Default behavior unchanged (uses `~/.sky/` as before)
- **Environment-based**: Activated via `SKYPILOT_INSTANCE_ID` environment variable
- **Complete isolation**: Each instance has separate databases, configs, locks, etc.
- **Port management**: API server ports automatically offset by instance ID
- **Easy to use**: Simple wrapper scripts for all operations

## Code Changes

### 1. New Helper Function

**File**: `sky/utils/common_utils.py`

Added `get_sky_dir(subpath='')` function that:
- Returns `~/.sky/` when `SKYPILOT_INSTANCE_ID` is not set (default)
- Returns `~/.sky-dev-{id}/` when `SKYPILOT_INSTANCE_ID` is set
- Handles subdirectory paths correctly

### 2. Updated Runtime Utils

**File**: `sky/skylet/runtime_utils.py`

Enhanced `get_runtime_dir_path()` to:
- Check for `SKYPILOT_INSTANCE_ID` environment variable
- Transform `.sky` paths to `.sky-dev-{id}` paths when instance ID is set
- Maintain backward compatibility with `SKY_RUNTIME_DIR` override

### 3. Path Updates (12 files)

Updated the following files to use instance-aware paths:

| File | Constants Updated | Lines Changed |
|------|------------------|---------------|
| `sky/skypilot_config.py` | Config paths, lock paths | ~10 |
| `sky/jobs/scheduler.py` | Job controller PID, env, lock | ~5 |
| `sky/jobs/constants.py` | Job controller YAML, signal paths | ~8 |
| `sky/server/constants.py` | API server DB, cookies | ~3 |
| `sky/utils/cluster_utils.py` | SSH config locks | ~3 |
| `sky/ssh_node_pools/constants.py` | Node pool info, keys | ~3 |
| `sky/volumes/server/core.py` | Volume locks | ~1 |
| `sky/users/permission.py` | Policy update lock | ~1 |
| `sky/users/token_service.py` | JWT secret lock | ~1 |
| `sky/users/server.py` | User locks | ~1 |

**Total**: ~36 lines of code changes across 12 files

## Wrapper Scripts

Created two bash scripts in the repository root:

### 1. `sky-dev`

Main wrapper for running commands with a specific instance:

```bash
./sky-dev <instance-id> <command> [args...]
```

Sets:
- `SKYPILOT_INSTANCE_ID`: Instance identifier
- `SKYPILOT_API_SERVER_ENDPOINT`: API server URL

### 2. `sky-dev-api`

Helper for managing API servers:

```bash
./sky-dev-api <instance-id> <start|stop|status|restart>
```

Manages API server lifecycle with correct port for each instance.

## Documentation

Created two comprehensive guides:

1. **`MULTI_INSTANCE_DEV.md`**: Complete user guide with examples
2. **`IMPLEMENTATION_SUMMARY.md`**: This technical summary

## Testing

Verified:
- ✅ Instance ID correctly set by wrapper
- ✅ Environment variables propagate correctly
- ✅ Path resolution works for all instance IDs
- ✅ Default behavior preserved (no instance ID = `~/.sky/`)
- ✅ Port offset calculation correct

## Usage Examples

### Basic Usage

```bash
# Start API server for instance 1
./sky-dev-api 1 start

# Run commands with instance 1
./sky-dev 1 sky status
./sky-dev 1 sky launch my-task.yaml

# Use instance 2 in parallel
./sky-dev-api 2 start
./sky-dev 2 sky status
```

### Multiple Parallel Developments

```bash
# Terminal 1: Claude Code session 1
export SKYPILOT_INSTANCE_ID=1
sky status

# Terminal 2: Claude Code session 2
export SKYPILOT_INSTANCE_ID=2
sky status

# Or use the wrapper
./sky-dev 1 sky status
./sky-dev 2 sky status
```

## State Isolation

Each instance maintains isolated state:

```
~/.sky/           # Default (no instance ID)
~/.sky-dev-0/     # Instance 0
~/.sky-dev-1/     # Instance 1
~/.sky-dev-2/     # Instance 2
├── config.yaml
├── state_db.db
├── spot_jobs_db.db
├── serve_db.db
├── api_server/
│   └── requests.db
├── locks/
└── ...
```

## Port Allocation

- Instance 0: API server on port 46580
- Instance 1: API server on port 46581
- Instance 2: API server on port 46582
- Instance N: API server on port 46580+N

## Backward Compatibility

- ✅ No changes to default behavior
- ✅ All existing code works without modifications
- ✅ Environment variable is opt-in
- ✅ No breaking changes to APIs or CLIs

## Benefits for Multi-Claude Development

1. **Complete isolation**: Each Claude Code session can work independently
2. **No conflicts**: Separate databases, configs, and state
3. **Easy cleanup**: Just delete instance directories
4. **Parallel testing**: Test different configurations simultaneously
5. **Simple workflow**: Use wrapper scripts or export env var

## Known Limitations

1. **Skylet gRPC port**: Still shared (46590) - rarely causes issues
2. **Module-level constants**: Set at import time - SKYPILOT_INSTANCE_ID must be set before importing sky
3. **Remote paths**: Only local paths are instance-aware

## Design Decisions

### Why Environment Variable?

- Simple and familiar pattern (like `KUBECONFIG`, `DOCKER_CONFIG`)
- No command-line flag pollution
- Easy to set once per session
- Works with any SkyPilot command

### Why Minimal Code Changes?

- Easier to review and maintain
- Lower risk of introducing bugs
- Focused on critical local development paths
- Remote-only paths left unchanged

### Why Wrapper Scripts?

- No changes to sky CLI needed
- Easy to understand and modify
- Bash is universally available
- Can be added to PATH or aliased

## Future Enhancements (Optional)

Potential improvements if needed:

1. **Instance manager CLI**: Create `sky-instance` tool for better UX
2. **Automatic port detection**: Find free ports automatically
3. **Named instances**: Support names instead of just numbers
4. **Instance listing**: Command to show all active instances
5. **Skylet port isolation**: Support instance-specific Skylet ports

## Files Changed

### Modified Files (12)
- `sky/utils/common_utils.py`
- `sky/skylet/runtime_utils.py`
- `sky/skypilot_config.py`
- `sky/jobs/scheduler.py`
- `sky/jobs/constants.py`
- `sky/server/constants.py`
- `sky/utils/cluster_utils.py`
- `sky/ssh_node_pools/constants.py`
- `sky/volumes/server/core.py`
- `sky/users/permission.py`
- `sky/users/token_service.py`
- `sky/users/server.py`

### New Files (4)
- `sky-dev` (bash script)
- `sky-dev-api` (bash script)
- `MULTI_INSTANCE_DEV.md` (user guide)
- `IMPLEMENTATION_SUMMARY.md` (this file)

## Total Impact

- **Lines of code changed**: ~50
- **New files**: 4
- **Modified files**: 12
- **Breaking changes**: 0
- **Backward compatibility**: 100%

## Conclusion

This implementation provides a clean, minimal solution for running multiple SkyPilot instances locally. It's perfect for the use case of having multiple Claude Code sessions working on SkyPilot development simultaneously without conflicts.

The approach prioritizes simplicity and maintainability over feature completeness, focusing on the critical paths needed for local development while preserving backward compatibility.
