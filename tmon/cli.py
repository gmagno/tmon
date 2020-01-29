"""CLI script for tmon."""
import sys

from tmon import tmon


def main():
    return tmon.TMon().run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
