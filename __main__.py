"""Entry-point for the :program:`dpag` umbrella command."""

import sys
def main() -> None:
    """Entrypoint to the ``dpag`` umbrella command."""
    from dpag.bin.dpag import main as _main
    sys.exit(_main())

if __name__ == '__main__':  # pragma: no cover
    main()