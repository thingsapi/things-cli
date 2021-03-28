# Things Python CLI

A simple Python 3 library to read your [Things app](https://culturedcode.com/things) data using the [things.py API](https://github.com/thingsapi/things.py/).

## Table of Contents

- [Install](#install)
- [Examples](#examples)
- [Background](#background)
- [Things URLs](#things-urls)

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

% things-cli --csv today > today.csv && open today.csv # e.g. on macOS this might open Excel
```

