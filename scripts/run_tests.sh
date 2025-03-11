#!/bin/bash

# Set environment variables for testing
export POSTGRES_SERVER=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=thelastcentaur_test
export SECRET_KEY="testsecretkey"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# Run the tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Return the exit code of pytest
exit $? 