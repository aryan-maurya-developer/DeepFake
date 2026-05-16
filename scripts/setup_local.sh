#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r api/requirements.txt

pushd frontend >/dev/null
npm install
popd >/dev/null

echo "Local environment ready. Run './start.sh' to launch the stack."
