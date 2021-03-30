#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple Python 3 CLI to read your Things app data."""

from __future__ import print_function

__author__ = "Alexander Willner"
__copyright__ = "2021 Alexander Willner"
__credits__ = ["Alexander Willner"]
__license__ = "Apache License 2.0"
__version__ = "0.0.1"
__maintainer__ = "Alexander Willner"
__email__ = "alex@willner.ws"
__status__ = "Development"

import sys
import argparse
import json
import csv
from os import environ
import webbrowser
import argcomplete  # type: ignore

import things as api


class ThingsCLI:
    """A simple Python 3 CLI to read your Things app data."""

    print_json = False
    print_csv = False
    # print_opml = False
    # anonymize = False
    database = None

    def __init__(self, database=None):
        self.database = database
        # noqa todo: move to API:
        if environ.get("THINGSDB"):
            self.database = environ.get("THINGSDB")

    def print_tasks(self, tasks):
        """Print a task."""
        if self.print_json:
            print(json.dumps(tasks))
        # elif self.print_opml:
        #    Things3OPML().print_tasks(tasks)
        elif self.print_csv:
            fieldnames = []
            for task in tasks:
                fieldnames.extend(x for x in task if x not in fieldnames)
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(tasks)
        else:
            for task in tasks:
                title = task["title"]
                context = task["start"] if "start" in task else ""
                print(" - ", title, " (", context, ")")

    @classmethod
    def print_unimplemented(cls):
        """Show warning that method is not yet implemented."""
        print("not implemented yet (see things.sh for a more complete CLI)")

    @classmethod
    def get_parser(cls):
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(description="Simple read-only Thing 3 CLI.")

        subparsers = parser.add_subparsers(
            help="", metavar="command", required=True, dest="command"
        )
        # Core database methods
        subparsers.add_parser("inbox", help="Shows inbox tasks")
        subparsers.add_parser("today", help="Shows todays tasks")
        subparsers.add_parser("upcoming", help="Shows upcoming tasks")
        subparsers.add_parser("anytime", help="Shows anytime tasks")
        subparsers.add_parser("completed", help="Shows completed tasks")
        subparsers.add_parser("canceled", help="Shows canceled tasks")
        subparsers.add_parser("all", help="Shows all tasks")
        subparsers.add_parser("areas", help="Shows all areas")
        subparsers.add_parser("projects", help="Shows all projects")
        subparsers.add_parser("repeating", help="Shows all repeating tasks")
        subparsers.add_parser("logbook", help="Shows tasks completed today")
        subparsers.add_parser("trashed", help="Shows trashed tasks")
        subparsers.add_parser("subtasks", help="Shows all subtasks")
        subparsers.add_parser("tags", help="Shows all tags ordered by their usage")
        subparsers.add_parser("due", help="Shows tasks with due dates")
        subparsers.add_parser("headings", help="Shows headings")
        # Additional helper methods
        subparsers.add_parser("feedback", help="Give feedback")
        subparsers.add_parser("backlog", help="Shows backlog tasks")
        subparsers.add_parser("empty", help="Shows projects that are empty")
        subparsers.add_parser("hours", help="Shows hours planned today")
        subparsers.add_parser("ical", help="Shows tasks ordered by due date as iCal")
        subparsers.add_parser("lint", help="Shows tasks that float around")
        subparsers.add_parser(
            "mostClosed", help="Shows days when most tasks were closed"
        )
        subparsers.add_parser(
            "mostCancelled", help="Shows days when most tasks were cancelled"
        )
        subparsers.add_parser(
            "mostTrashed", help="Shows days when most tasks were trashed"
        )
        subparsers.add_parser(
            "mostCreated", help="Shows days when most tasks were created"
        )
        subparsers.add_parser("mostTasks", help="Shows projects that have most tasks")
        subparsers.add_parser(
            "mostCharacters", help="Shows tasks that have most characters"
        )
        subparsers.add_parser("nextish", help="Shows all nextish tasks")
        subparsers.add_parser("old", help="Shows all old tasks")
        subparsers.add_parser("schedule", help="Schedules an event using a template")
        subparsers.add_parser(
            "search", help="Searches for a specific task"
        ).add_argument("string", help="String to search for")
        subparsers.add_parser("stat", help="Provides a number of statistics")
        subparsers.add_parser("statcsv", help="Exports some statistics as CSV")
        subparsers.add_parser("tag", help="Shows all tasks with the waiting for tag")
        subparsers.add_parser(
            "waiting", help="Shows all tasks with the waiting for tag"
        )

        parser.add_argument(
            "-j",
            "--json",
            action="store_true",
            default=False,
            help="output as JSON",
            dest="json",
        )

        parser.add_argument(
            "-c",
            "--csv",
            action="store_true",
            default=False,
            help="output as CSV",
            dest="csv",
        )

        # parser.add_argument("-o", "--opml",
        #                     action="store_true", default=False,
        #                     help="output as OPML", dest="opml")

        # parser.add_argument("-a", "--anonymize",
        #                     action="store_true", default=False,
        #                     help="anonymize output", dest="anonymize")

        parser.add_argument(
            "-d", "--database", help="set path to database", dest="database"
        )

        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s (version {version})".format(version=__version__),
        )

        argcomplete.autocomplete(parser)

        return parser

    def main(self, args=None):
        """ Main entry point of the app """

        if args is None:
            self.main(ThingsCLI.get_parser().parse_args())
        else:
            command = args.command
            self.print_json = args.json
            self.print_csv = args.csv
            self.database = (
                args.database if args.database is not None else self.database
            )
            # self.print_opml = args.opml
            # self.anonymize = args.anonymize
            # self.things3.anonymize = self.anonymize ## not implemented

            if command == "all":
                self.print_tasks(api.todos(filepath=self.database))
            elif command == "search":
                self.print_tasks(api.search(args.string, filepath=self.database))
                #print("todo: implement search for: '%s'" % args.string)
            elif command == "feedback":  # pragma: no cover
                webbrowser.open("https://github.com/thingsapi/things-cli/issues")
            elif command in dir(api):
                self.print_tasks(getattr(api, command)(filepath=self.database))
            else:
                ThingsCLI.print_unimplemented()


def main():
    """Main entry point for CLI installation"""
    ThingsCLI().main()


if __name__ == "__main__":
    main()
