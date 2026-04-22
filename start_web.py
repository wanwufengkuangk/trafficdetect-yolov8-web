from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


def parse_bootstrap_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", help="Optional runtime config yaml path.")
    return parser.parse_known_args()


def bootstrap() -> None:
    args, remaining = parse_bootstrap_args()
    if args.config:
        os.environ["TRAFFICDETECT_CONFIG"] = str(Path(args.config).resolve())
    sys.argv = [sys.argv[0], *remaining]

    from app.main import main

    main()


if __name__ == "__main__":
    bootstrap()
