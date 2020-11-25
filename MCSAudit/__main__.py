"""
Entrypoint of the program.
"""

import argparse
import sys
from pathlib import Path

from .pipeline import Pipeline


def run_pipeline(namespace: argparse.Namespace) -> None:
    """
    Run the pipeline.
    """
    config = namespace.config
    pipeline = Pipeline.from_json(config)

    pipeline.precompute()
    pipeline.compute_defense()


def main(args) -> None:
    """
    Entrypoint of the program.
    """
    parser = argparse.ArgumentParser(prog="python -m grading")

    # Initialize the database.
    parser.add_argument(
        "config",
        help="Config file for the pipeline.",
        type=Path
    )

    namespace = parser.parse_args(args)
    run_pipeline(namespace)


if __name__ == "__main__":
    main(sys.argv[1:])
