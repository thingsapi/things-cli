# Things Python CLI

A simple Python 3 CLI to read your [Things app](https://culturedcode.com/things) data using the [things-cli API](https://github.com/thingsapi/things-cli/).

[![Build Status](https://github.com/thingsapi/things-cli/workflows/Build-Test/badge.svg)](https://github.com/thingsapi/things-cli/actions)
[![Coverage Status](https://codecov.io/gh/thingsapi/things-cli/branch/main/graph/badge.svg?token=DBWGKAEYAP)](https://codecov.io/gh/thingsapi/things-cli)
[![GitHub Release](https://img.shields.io/github/v/release/thingsapi/things-cli?sort=semver)](https://github.com/thingsapi/things-cli/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/things?label=pypi%20downloads)](https://pypi.org/project/things/)
[![GitHub Download Count](https://img.shields.io/github/downloads/thingsapi/things-cli/total.svg)](https://github.com/thingsapi/things-cli/releases)
[![GitHub Issues](https://img.shields.io/github/issues/thingsapi/things-cli)](https://github.com/thingsapi/things-cli/issues)
[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/quality/g/thingsapi/things-cli)](https://scrutinizer-ci.com/g/thingsapi/things-cli/?branch=master)

## Table of Contents

- [Install](#install)
- [Examples](#examples)

## Install

```sh
$ pip3 install things_cli
# or
$ git clone https://github.com/thingsapi/things_cli && cd things_cli && make install
```

## Examples

```shell
% things-cli inbox
 -  To-Do in Inbox  ( Inbox )

% things-cli all  
 -  To-Do in Today  ( Anytime )
 -  To-Do in Inbox  ( Inbox )
 -  To-Do in Upcoming  ( Someday )
 -  To-Do in Heading  ( Anytime )
 -  To-Do in Project  ( Anytime )
 -  To-Do in Anytime  ( Anytime )
 -  To-Do in Someday  ( Someday )
 -  To-Do in Area  ( Anytime )
 -  Repeating To-Do  ( Someday )

% things-cli --json today|jq
[
  {
    "uuid": "5pUx6PESj3ctFYbgth1PXY",
    "type": "to-do",
    "title": "To-Do in Today",
    "status": "incomplete",
    "notes": "With\nNotes",
    "start": "Anytime",
    "start_date": "2021-03-28",
    "due_date": null,
    "stop_date": null,
    "created": "2021-03-28 21:11:22",
    "modified": "2021-03-28 21:11:30"
  }
]

% things-cli --csv all > all.csv && open all.csv
```

