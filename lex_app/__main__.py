"""Entry-point for the :program:`lex` umbrella command."""

import sys
def main() -> None:
    """Entrypoint to the ``lex`` umbrella command."""
    from lex_app.bin.lex import main as _main
    sys.exit(_main())

if __name__ == '__main__':  # pragma: no cover
    main()