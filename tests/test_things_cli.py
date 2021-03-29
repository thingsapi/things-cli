#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module documentation goes here."""

import unittest
import io
import sys
from things_cli import cli


class ThingsCLICase(unittest.TestCase):
    """Class documentation goes here."""

    things3_cli = cli.ThingsCLI(database='tests/main.sqlite')

    def test_methods(self):
        """Invoke all commands."""
        parser = self.things3_cli.get_parser()
        for command in parser._subparsers._actions[1].choices:  # noqa # pylint: disable=protected-access
            if command != "feedback" and command != "search":
                args = parser.parse_args([command])
                new_out = io.StringIO()
                old_out = sys.stdout
                try:
                    sys.stdout = new_out
                    self.things3_cli.main(args)
                finally:
                    sys.stdout = old_out
                self.assertIn(" ", new_out.getvalue())

    def test_noparam(self):
        """Test no parameter."""
        new_out = io.StringIO()
        old_out = sys.stdout
        with self.assertRaises(SystemExit):
            sys.stderr = new_out
            self.things3_cli.main()
        sys.stderr = old_out
        self.assertIn("usage:", new_out.getvalue())
        with self.assertRaises(SystemExit):
            sys.stderr = new_out
            cli.main()
        sys.stderr = old_out
        self.assertIn("usage:", new_out.getvalue())

    def test_today(self):
        """Test Today."""
        args = self.things3_cli.get_parser().parse_args(['-d', 'tests/main.sqlite', 'today'])
        new_out = io.StringIO()
        old_out = sys.stdout
        try:
            sys.stdout = new_out
            self.things3_cli.main(args)
        finally:
            sys.stdout = old_out
        self.assertIn("To-Do in Today", new_out.getvalue())

    def test_csv(self):
        """Test Next via CSV."""
        args = self.things3_cli.get_parser().parse_args(['-d', 'tests/main.sqlite', '-c', 'anytime'])
        new_out = io.StringIO()
        old_out = sys.stdout
        try:
            sys.stdout = new_out
            self.things3_cli.main(args)
        finally:
            sys.stdout = old_out
        self.assertIn("E18tg5qepzrQk9J6jQtb5C", new_out.getvalue())

    def test_json(self):
        """Test Upcoming via JSON."""
        args = self.things3_cli.get_parser().parse_args(['-d', 'tests/main.sqlite', '-j', 'upcoming'])
        new_out = io.StringIO()
        old_out = sys.stdout
        try:
            sys.stdout = new_out
            self.things3_cli.main(args)
        finally:
            sys.stdout = old_out
        self.assertIn("7F4vqUNiTvGKaCUfv5pqYG", new_out.getvalue())


if __name__ == '__main__':
    unittest.main()
