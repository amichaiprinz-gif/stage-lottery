#!/usr/bin/env bash
# Runs the product's tests. Exit 0 only when every test passes.
set -u
cd "$(dirname "$0")/.."
failed=0
total=0
for t in tests/test_*.py; do
  total=$((total + 1))
  python3 "$t" || failed=$((failed + 1))
done
echo "$((total - failed)) מתוך $total בדיקות עברו"
[ "$failed" -eq 0 ]
