# The Last Centaur - Scripts Directory

This directory contains utility scripts for managing The Last Centaur application. These scripts simplify common development and operational tasks.

## Docker Management Scripts

The following scripts help you manage Docker containers for the application:

### docker-manager.sh

The main entry point for Docker operations. This interactive script provides a menu-based interface for:

- Starting all containers
- Stopping all containers
- Restarting services
- Checking container status
- Viewing logs

**Usage:**

```bash
./docker-manager.sh
```

### run-docker.sh

Starts all Docker containers defined in the docker-compose.yml file. This script:

- Builds images if needed
- Sets up environment variables
- Starts containers in detached mode

**Usage:**

```bash
./scripts/run-docker.sh
```

### stop-docker.sh

Stops all running Docker containers for the application.

**Usage:**

```bash
./scripts/stop-docker.sh
```

### restart-services.sh

Restarts all services and applies CORS fixes for local development.

**Usage:**

```bash
./scripts/restart-services.sh
```

## Testing Scripts

The following scripts help simplify running tests:

### run_tests.sh

A shell script that runs all unit tests using pytest.

**Usage:**

```bash
./scripts/run_tests.sh
```

### run_api_tests.py

A Python script that runs API integration tests.

**Usage:**

```bash
python ./scripts/run_api_tests.py
```

### run_game_tests.py

A Python script that runs game-specific tests, with options to test specific paths.

**Usage:**

```bash
python ./scripts/run_game_tests.py --path warrior
python ./scripts/run_game_tests.py --path mystic
python ./scripts/run_game_tests.py --path stealth
```

### run_core_tests.py

A Python script that runs core engine tests without API or LLM dependencies. This is useful for testing the fundamental game mechanics directly.

**Usage:**

```bash
# Run all core engine tests
python ./scripts/run_core_tests.py --test all

# Test specific functionality
python ./scripts/run_core_tests.py --test warrior     # Test warrior path
python ./scripts/run_core_tests.py --test mystic      # Test mystic path
python ./scripts/run_core_tests.py --test stealth     # Test stealth path
python ./scripts/run_core_tests.py --test movement    # Test movement system
python ./scripts/run_core_tests.py --test board       # Test full board exploration
python ./scripts/run_core_tests.py --test items       # Test item pickup
python ./scripts/run_core_tests.py --test combat      # Test combat system
```

## Development Scripts

Additional scripts may be added in the future to assist with:

- Database migrations
- Test automation
- Deployment operations
- Performance profiling

## Adding New Scripts

When adding new scripts to this directory:

1. Make the script executable: `chmod +x your_script.sh`
2. Document the script in this README
3. Consider adding the script to the docker-manager.sh menu if appropriate

For more detailed documentation on Docker setup and configuration, see [../docs/DOCKER.md](../docs/DOCKER.md).
