#!/usr/bin/env bash
# Build and run the host tests for the v1 bake program (needs only g++).
#
#   firmware/v1/test/kjor_tester.sh
set -euo pipefail
cd "$(dirname "$0")/../../.."
B=firmware/v1/components/bakeplan
OUT="${TMPDIR:-/tmp}/surdeigsbaker-tester"
mkdir -p "$OUT"
FLAGS="-std=gnu++17 -Wall -Wextra -O2 -I $B"

g++ $FLAGS $B/planner.cpp firmware/v1/test/planner_test.cpp -o "$OUT/planner_test"
g++ $FLAGS $B/doser.cpp firmware/v1/test/doser_test.cpp -o "$OUT/doser_test"
g++ $FLAGS $B/planner.cpp $B/doser.cpp $B/sequence.cpp $B/bake.cpp $B/sim.cpp firmware/v1/test/bake_test.cpp \
  -o "$OUT/bake_test"

for t in planner_test doser_test bake_test; do
  echo "=== $t"
  "$OUT/$t" | grep -v "^    "
done
