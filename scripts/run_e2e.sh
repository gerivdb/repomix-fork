#!/usr/bin/env bash
# Run E2E tests — requires live environment
set -euo pipefail

echo "[E2E] Running complete engine tests..."
bash tests/e2e_test_complete_engines.sh

echo "[E2E] Running ECOS launch tests..."
bash tests/e2e_test_ecos_launch.sh

echo "[E2E] Done."
