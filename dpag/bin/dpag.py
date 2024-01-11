"""Dpag Command Line Interface."""
import sys
import os
import subprocess

from pathlib import Path
import site
import django
import argparse


def setup_django():
    PACKAGE_ROOT = Path(__file__).resolve().parent.parent.as_posix()
    PROJECT_ROOT_DIR = Path(os.getcwd()).resolve()
    DJANGO_ROOT_DIR = PROJECT_ROOT_DIR / PACKAGE_ROOT
    sys.path.append(PACKAGE_ROOT)

    # The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "DjangoProcessAdminGeneric.settings"
    )
    os.environ.setdefault(
        "PROJECT_ROOT", PROJECT_ROOT_DIR.as_posix()
    )

    django.setup()

    return PACKAGE_ROOT

def run_django_commands(command):
    setup_django()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(["manage.py", command])

def run_start(init):
    PACKAGE_ROOT = setup_django()
    if init:
        for command in ["createcachetable", "makemigrations", "migrate"]:
            run_django_commands(command)

    command = ["uvicorn", "--reload", "--loop", "asyncio", f"--app-dir={PACKAGE_ROOT}",
               "DjangoProcessAdminGeneric.asgi:application"]

    subprocess.run(command)

def main():
    parser = argparse.ArgumentParser(description='Dpag Command Line Interface')
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_migrate = subparsers.add_parser('migrate')
    parser_makemigrations = subparsers.add_parser('makemigrations')
    parser_createcachtable = subparsers.add_parser('createcachtable')

    parser_start = subparsers.add_parser('start')
    parser_start.add_argument('--init', action='store_true', help='Perform initial migrations before starting to server')

    args = parser.parse_args()

    if args.command != 'start':
        run_django_commands(args.command)
    else:
        run_start(args.init)