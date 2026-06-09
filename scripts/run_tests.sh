#!/usr/bin/env bash
# Run unit + integration tests (no slow/e2e)
set -euo pipefail

pytest tests/ -v --tb=short \
  --ignore=tests/performance \
  --ignore=tests/stress_test_autoresearch_schmidhuber.py \
  --ignore=tests/chaos_engineering.py \
  -m "not slow and not e2e" \
  --cov=src --cov-report=term-missing
