# Multi-Instance SkyPilot - Quick Start

## TL;DR

Run multiple isolated SkyPilot instances for local development:

```bash
# Use instance 1
./sky-dev 1 sky status

# Use instance 2 in parallel
./sky-dev 2 sky status

# Manage API servers
./sky-dev-api 1 start
./sky-dev-api 2 start
```

Each instance has isolated state in `~/.sky-dev-{id}/` and runs API server on port `46580+id`.

## Common Commands

### Basic Usage
```bash
./sky-dev 1 sky status                    # Check status (instance 1)
./sky-dev 1 sky launch task.yaml          # Launch cluster (instance 1)
./sky-dev 2 sky exec cluster -- ls        # Execute command (instance 2)
```

### API Server Management
```bash
./sky-dev-api 1 start      # Start API server (port 46581)
./sky-dev-api 1 stop       # Stop API server
./sky-dev-api 1 status     # Check status
./sky-dev-api 1 restart    # Restart after code changes
```

### Multiple Parallel Sessions
```bash
# Terminal 1: Work on feature A
./sky-dev-api 1 start
./sky-dev 1 sky launch feature-a.yaml

# Terminal 2: Work on feature B
./sky-dev-api 2 start
./sky-dev 2 sky launch feature-b.yaml
```

## How It Works

**Sets environment variables:**
- `SKYPILOT_INSTANCE_ID=<id>`
- `SKYPILOT_API_SERVER_ENDPOINT=http://127.0.0.1:46580+<id>`

**Creates isolated directories:**
- Instance 1: `~/.sky-dev-1/`
- Instance 2: `~/.sky-dev-2/`
- Default: `~/.sky/` (unchanged)

## Optional: Add to PATH

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/user/skypilot:$PATH"

# Then use without ./
sky-dev 1 sky status
sky-dev-api 1 start
```

## Optional: Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias sky1='sky-dev 1 sky'
alias sky2='sky-dev 2 sky'

# Usage
sky1 status
sky2 launch task.yaml
```

## Cleanup

```bash
# Remove instance state
rm -rf ~/.sky-dev-1
rm -rf ~/.sky-dev-2
```

## Full Documentation

- **User Guide**: See `MULTI_INSTANCE_DEV.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`

## Testing

Run the test script to verify everything works:

```bash
./test_multi_instance_simple.sh
```
