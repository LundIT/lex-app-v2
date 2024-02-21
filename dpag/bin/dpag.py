"""Dpag Command Line Interface."""
import sys
import os
import subprocess

from pathlib import Path
import site
import django
import argparse
import uvicorn
import click
from django.core.management import get_commands, call_command

DPAG_PACKAGE_ROOT = None

def setup_django():
    global DPAG_PACKAGE_ROOT
    DPAG_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.as_posix()
    PROJECT_ROOT_DIR = Path(os.getcwd()).resolve()
    sys.path.append(DPAG_PACKAGE_ROOT)

    # The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "DjangoProcessAdminGeneric.settings"
    )
    os.environ.setdefault(
        "PROJECT_ROOT", PROJECT_ROOT_DIR.as_posix()
    )

    django.setup()

@click.group()
def dpag():
    setup_django()


@dpag.command()
def start():
    global DPAG_PACKAGE_ROOT
    uvicorn.run(app="DjangoProcessAdminGeneric.asgi:application", reload=True, app_dir=DPAG_PACKAGE_ROOT, loop="asyncio")

@dpag.command()
def init():
    for command in ["createcachetable", "makemigrations", "migrate"]:
        call_command(command)

commands = get_commands()
commands = list(commands.keys()) + ["createcachetable"]
for command in commands:
    @dpag.command(name=command)
    def _():
        call_command(command)

def main():
    dpag()