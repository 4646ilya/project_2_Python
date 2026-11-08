#!/usr/bin/env python3

from primitive_db import engine


def main() -> None:
    """Точка входа приложения."""
    engine.welcome()
    engine.run()


if __name__ == "__main__":
    main()
