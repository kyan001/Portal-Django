#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run develop commands for django project"""
import os
import sys
import collections
from functools import wraps
import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


def pStartEnd(title="Call"):  # decorator
    """Decorator: Print start and end for a function"""
    def get_func(func: callable):
        @wraps(func)
        def callInputFunc(*args, **kwargs):
            ktk.pStart().pTitle(title)
            result = func(*args, **kwargs)
            ktk.pEnd()
            return result
        return callInputFunc
    return get_func


def manage_file_exist():
    """Detect if django project manage.py file exist

    returns
        bool: manage.py is under current path
    """
    return os.path.exists('./manage.py')


@pStartEnd('-- Installing Requirements --')
def requirements_install():
    """Install necessary modules by pip & requirements.txt"""
    if not os.path.exists('./requirements.txt'):
        ktk.err('No requirements.txt detected.').bye()
    if 'win' in sys.platform:
        ktk.runCmd('pip3 install -r requirements.txt')
    else:
        ktk.runCmd('sudo pip3 install -r requirements.txt')


@pStartEnd('-- Applying changes to database --')
def migrate_db():
    """Apply changes to database"""
    ktk.runCmd('py manage.py makemigrations')
    ktk.runCmd('py manage.py migrate')


@pStartEnd('-- Enter DB shell --')
def db_shell():
    """Enter Django database shell mode"""
    ktk.runCmd('py manage.py dbshell')


@pStartEnd('-- Enter interactive shell --')
def interactive_shell():
    """Enter Django shell mode"""
    ktk.runCmd('py manage.py shell')


@pStartEnd('-- Runserver localhost --')
def runserver_dev():
    """Runserver in development environment, only for localhost debug use"""
    ktk.runCmd('py manage.py runserver')


@pStartEnd('-- Create superuser --')
def create_superuser():
    """Create superuser account for Django admin"""
    ktk.info('Password is specified, ask someone for it')
    ktk.runCmd('py manage.py createsuperuser --username portal --email kai@superfarmer.net')


def show_menu():
    """Show commands menu

    returns:
        a callable function name
    """
    commands = collections.OrderedDict({
        'Install Requirements Modules': requirements_install,
        'Make & migrate database': migrate_db,
        'Create superuser account': create_superuser,
        'Runserver (localhost:8000)': runserver_dev,
        'Shell: Interactive': interactive_shell,
        'Shell: Database': db_shell,
        'Exit': ktk.bye,
    })
    ktk.echo('Select one of these:')
    selection = ktk.getChoice(sorted(commands.keys()))
    return commands.get(selection)


def main():
    ktk.clearScreen()
    if not manage_file_exist():
        ktk.err('No manage.py detected. Please run this under projects folder').bye()
    while True:
        to_run = show_menu()
        to_run()


if __name__ == '__main__':
    main()
