#!/usr/bin/env python3

"""A simple Python 3 CLI to read your Things app data."""

from __future__ import print_function

import argparse
import csv
from datetime import datetime
from io import StringIO
import json
import sys
from typing import Dict
import webbrowser
from xml.dom import minidom
import xml.etree.ElementTree as ETree
from xml.etree.ElementTree import Element, SubElement

import argcomplete  # type: ignore
import things as api

from things_cli import __version__


class ThingsCLI:  # pylint: disable=too-many-instance-attributes
    """A simple Python 3 CLI to read your Things app data."""

    print_json = False
    print_csv = False
    print_gantt = False
    print_opml = False
    # anonymize = False
    database = None
    recursive = False
    filter_project = None
    filter_area = None
    filter_tag = None
    only_projects = None

    def __init__(self, database=None):
        """Initialize class."""
        self.database = database

    def print_tasks(self, tasks):
        """Print a task."""

        if self.only_projects:
            for task in tasks:
                task["items"] = (
                    [
                        items
                        for items in task["items"]
                        if items["type"] in ["area", "project"]
                    ]
                    if task.get("items")
                    else []
                )
                for items in task["items"]:
                    items["items"] = (
                        [
                            sub_items
                            for sub_items in items["items"]
                            if sub_items["type"] in ["area", "project"]
                        ]
                        if items.get("items")
                        else []
                    )

        if self.print_json:
            print(json.dumps(tasks))
        elif self.print_opml:
            print(self.opml_dumps(tasks))
        elif self.print_csv:
            print(self.csv_dumps(tasks))
        elif self.print_gantt:
            print("gantt")
            print("  dateFormat  YYYY-MM-DD")
            print("  title       Things To-Dos")
            print("  excludes    weekends")
            print(self.gantt_dumps(tasks))
        else:
            print(self.txt_dumps(tasks), end="")

    def gantt_dumps(self, tasks, array=None):
        """Convert tasks into mermaid-js GANTT."""

        result = ""

        if array is None:
            array = {}

        for task in tasks:
            ThingsCLI.gantt_add_task(task, array)
            self.gantt_dumps(task.get("items", []), array)

        for group in array:
            result += f"  section {group}\n"
            for item in array[group]:
                result += item

        return result

    @staticmethod
    def gantt_add_task(task, array):
        """Add a task to a mermaid-js GANTT."""

        context = (
            task.get("project_title", None)
            or task.get("area_title", None)
            or task.get("heading_title", None)
            or task.get("start", None)
            or ""
        )

        title = task["title"].replace(":", " ")
        start = task.get("start_date")
        deadline = task.get("deadline") or "1h"
        if not start and deadline != "1h":
            start = deadline
        if start == deadline:
            deadline = "1h"
        if deadline == "1h":
            visual = ":milestone"
        else:
            visual = ":active"
            # lint-ignore todo: if in the past: done
        if start and not task.get("stop_date"):
            if context not in array:
                array[context] = []
            if not "".join(s for s in array[context] if title.lower() in s.lower()):
                array[context].append(f"    {title} {visual}, {start}, {deadline}\n")

    def csv_dumps(self, tasks):
        """Convert tasks into CSV."""

        fieldnames = []
        self.csv_header(tasks, fieldnames)
        if "items" in fieldnames:
            fieldnames.remove("items")
        if "checklist" in fieldnames:
            fieldnames.remove("checklist")

        output = StringIO()
        writer = csv.DictWriter(
            output, fieldnames=fieldnames, delimiter=";", escapechar="\\"
        )
        writer.writeheader()

        self.csv_converter(tasks, writer)

        return output.getvalue()

    def csv_header(self, tasks, fieldnames):
        """Convert tasks into CSV header."""
        for task in tasks:
            fieldnames.extend(field for field in task if field not in fieldnames)
            self.csv_header(task.get("items", []), fieldnames)

    def csv_converter(self, tasks, writer):
        """Convert tasks into CSV."""
        if tasks is True:
            return
        for task in tasks:
            self.csv_converter(task.get("items", []), writer)
            task.pop("items", [])
            self.csv_converter(task.get("checklist", []), writer)
            task.pop("checklist", [])
            writer.writerow(task)

    def opml_dumps(self, tasks):
        """Convert tasks into OPML."""

        top = Element("opml")
        head = SubElement(top, "head")
        SubElement(head, "title").text = "Things 3 Database"
        body = SubElement(top, "body")

        self.opml_convert(tasks, body)

        return minidom.parseString(ETree.tostring(top)).toprettyxml(indent="   ")

    def opml_convert(self, tasks, top):
        """Print pretty OPML of selected tasks."""

        if tasks is True:
            return
        for task in tasks:
            area = SubElement(top, "outline")
            text = task["title"]
            if task.get("start_date"):
                text = f"{text} (Scheduled: {task['start_date']})"
            elif task.get("start"):
                text = f"{text} ({task['start']})"
            area.set("text", text)
            self.opml_convert(task.get("items", []), area)
            task.pop("items", [])
            self.opml_convert(task.get("checklist", []), area)
            task.pop("checklist", [])

    def txt_dumps(self, tasks, indentation="", result=""):
        """Print pretty text version of selected tasks."""

        if tasks is True:
            return result
        for task in tasks:
            title = task["title"]
            context = (
                task.get("project_title", None)
                or task.get("area_title", None)
                or task.get("heading_title", None)
                or task.get("start", None)
            )
            start = task.get("start_date", None)
            details = " | ".join(filter(None, [start, context]))
            result = result + f"{indentation}- {title} ({details})\n"
            result = self.txt_dumps(task.get("items", []), indentation + "  ", result)
            task.pop("items", [])
            result = self.txt_dumps(
                task.get("checklist", []), indentation + "  ", result
            )

        return result

    @classmethod
    def print_unimplemented(cls, command):
        """Show warning that method is not yet implemented."""
        print(f"command '{command}' not implemented yet", file=sys.stderr)

    @classmethod
    def get_parser(cls):
        """Create command line argument parser."""
        parser = argparse.ArgumentParser(description="Simple read-only Thing 3 CLI.")

        subparsers = parser.add_subparsers(
            help="", metavar="command", required=True, dest="command"
        )

        ################################
        # Core database methods
        ################################
        subparsers.add_parser("inbox", help="Shows inbox tasks")
        subparsers.add_parser("today", help="Shows todays tasks")
        subparsers.add_parser("upcoming", help="Shows upcoming tasks")
        subparsers.add_parser("anytime", help="Shows anytime tasks")
        subparsers.add_parser("completed", help="Shows completed tasks")
        subparsers.add_parser("someday", help="Shows someday tasks")
        subparsers.add_parser("canceled", help="Shows canceled tasks")
        subparsers.add_parser("trash", help="Shows trashed tasks")
        subparsers.add_parser("todos", help="Shows all todos")
        subparsers.add_parser("all", help="Shows all tasks")
        subparsers.add_parser("areas", help="Shows all areas")
        subparsers.add_parser("projects", help="Shows all projects")
        subparsers.add_parser("logbook", help="Shows completed tasks")
        subparsers.add_parser("logtoday", help="Shows tasks completed today")
        subparsers.add_parser("createdtoday", help="Shows tasks created today")
        subparsers.add_parser("tags", help="Shows all tags ordered by their usage")
        subparsers.add_parser("deadlines", help="Shows tasks with due dates")

        ################################
        # Additional functions
        ################################
        subparsers.add_parser("feedback", help="Give feedback")
        subparsers.add_parser(
            "search", help="Searches for a specific task"
        ).add_argument("string", help="String to search for")

        ################################
        # To be implemented in things.py
        ################################
        # subparsers.add_parser("repeating", help="Shows all repeating tasks")
        # subparsers.add_parser("subtasks", help="Shows all subtasks")
        # subparsers.add_parser("headings", help="Shows headings")

        ################################
        # To be converted from https://github.com/alexanderwillner/things.sh
        ################################
        # subparsers.add_parser("backlog", help="Shows backlog tasks")
        # subparsers.add_parser("empty", help="Shows projects that are empty")
        # subparsers.add_parser("hours", help="Shows hours planned today")
        # subparsers.add_parser("ical", help="Shows tasks ordered by due date as iCal")
        # subparsers.add_parser("lint", help="Shows tasks that float around")
        # subparsers.add_parser(
        #     "mostClosed", help="Shows days when most tasks were closed"
        # )
        # subparsers.add_parser(
        #     "mostCancelled", help="Shows days when most tasks were cancelled"
        # )
        # subparsers.add_parser(
        #     "mostTrashed", help="Shows days when most tasks were trashed"
        # )
        # subparsers.add_parser(
        #     "mostCreated", help="Shows days when most tasks were created"
        # )
        # subparsers.add_parser("mostTasks", help="Shows projects that have most tasks")
        # subparsers.add_parser(
        #     "mostCharacters", help="Shows tasks that have most characters"
        # )
        # subparsers.add_parser("nextish", help="Shows all nextish tasks")
        # subparsers.add_parser("old", help="Shows all old tasks")
        # subparsers.add_parser("schedule", help="Schedules an event using a template")
        # subparsers.add_parser("stat", help="Provides a number of statistics")
        # subparsers.add_parser("statcsv", help="Exports some statistics as CSV")
        # subparsers.add_parser("tag", help="Shows all tasks with the waiting for tag")
        # subparsers.add_parser(
        #     "waiting", help="Shows all tasks with the waiting for tag"
        # )

        ################################
        # To be converted from https://github.com/alexanderwillner/things.sh
        ################################
        # parser.add_argument("-a", "--anonymize",
        #                     action="store_true", default=False,
        #                     help="anonymize output", dest="anonymize")

        parser.add_argument(
            "-p", "--filter-project", dest="filter_project", help="filter by project (UUID)"
        )
        parser.add_argument(
            "-a", "--filter-area", dest="filter_area", help="filter by area (UUID)"
        )
        parser.add_argument(
            "-t", "--filtertag", dest="filter_tag", help="filter by tag"
        )
        parser.add_argument(
            "-e",
            "--only-projects",
            action="store_true",
            default=False,
            dest="only_projects",
            help="export only projects",
        )
        parser.add_argument(
            "-o",
            "--opml",
            action="store_true",
            default=False,
            help="output as OPML",
            dest="opml",
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

        parser.add_argument(
            "-g",
            "--gantt",
            action="store_true",
            default=False,
            help="output as mermaid-js GANTT",
            dest="gantt",
        )

        parser.add_argument(
            "-r",
            "--recursive",
            help="in-depth output",
            dest="recursive",
            default=False,
            action="store_true",
        )

        parser.add_argument(
            "-d", "--database", help="set path to database", dest="database"
        )

        parser.add_argument(
            "--version",
            "-v",
            action="version",
            version=f"%(prog)s (version {__version__})",
        )

        argcomplete.autocomplete(parser)

        return parser

    def defaults(self):
        """Set default options for the new API."""
        return {
            "project": self.filter_project,
            "area": self.filter_area,
            "tag": self.filter_tag,
            "include_items": self.recursive,
            "filepath": self.database,
        }

    def main(self, args=None):
        """Start the main app."""

        if args is None:
            self.main(ThingsCLI.get_parser().parse_args())
        else:
            self.print_json = args.json
            self.print_csv = args.csv
            self.print_gantt = args.gantt
            self.print_opml = args.opml
            self.database = args.database or self.database
            self.filter_project = args.filter_project or None
            self.filter_area = args.filter_area or None
            self.filter_tag = args.filter_tag or None
            self.only_projects = args.only_projects or None
            self.recursive = args.recursive
            # self.anonymize = args.anonymize
            # self.things3.anonymize = self.anonymize ## not implemented
            defaults = self.defaults()

            self.parse_command(defaults, args)

    def parse_command(self, defaults: Dict, args):
        """Handle given command."""

        command = args.command

        if command == "tags":
            defaults.pop("tag")
            defaults.pop("project")
        if command in ["all", "areas"]:
            defaults.pop("area")
            defaults.pop("project")

        if command == "all":
            inbox = api.inbox(**defaults)
            today = api.today(**defaults)
            upcoming = api.upcoming(**defaults)
            anytime = api.anytime(**defaults)
            someday = api.someday(**defaults)
            logbook = api.logbook(**defaults)

            no_area = api.projects(**defaults)
            areas = api.areas(**defaults)
            structure = [
                {"title": "Inbox", "items": inbox},
                {"title": "Today", "items": today},
                {"title": "Upcoming", "items": upcoming},
                {"title": "Anytime", "items": anytime},
                {"title": "Someday", "items": someday},
                {"title": "Logbook", "items": logbook},
                {"title": "No Area", "items": no_area},
                {"title": "Areas", "items": areas},
            ]
            self.print_tasks(structure)
        elif command == "logtoday":
            today = datetime.now().strftime("%Y-%m-%d")
            result = getattr(api, "logbook")(**defaults, stop_date=today)
            self.print_tasks(result)
        elif command == "createdtoday":
            result = getattr(api, "last")("1d")
            self.print_tasks(result)
        elif command == "upcoming":
            result = getattr(api, command)(**defaults)
            result.sort(key=lambda task: task["start_date"], reverse=False)
            self.print_tasks(result)
        elif command == "search":
            self.print_tasks(
                api.search(
                    args.string,
                    filepath=self.database,
                    include_items=self.recursive,
                )
            )
        elif command == "feedback":  # pragma: no cover
            webbrowser.open("https://github.com/thingsapi/things-cli/issues")
        elif command in dir(api):
            self.print_tasks(getattr(api, command)(**defaults))
        else:  # pragma: no cover
            ThingsCLI.print_unimplemented(command)
            sys.exit(3)


def main():
    """Start for CLI installation."""
    ThingsCLI().main()


if __name__ == "__main__":
    main()
