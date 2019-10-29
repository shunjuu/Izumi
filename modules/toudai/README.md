# Toudai

## Introduction

Toudai (灯台, lit. "lighthouse") is a lightweight, functionally minimal filesystem watcher designed specifically for Izumi's use. It tracks a given path for all new files, and reports them as new after a given interval has passed and the file itself hasn't changed in size.

## Usage

Toudai contains one primary method (which will act as a never-ending loop):
- `def watch(path: str, queue: Queue, logger: Logger, interval: int = 5, ) -> None`

Arguments:
- `path`: The system path for Toudai to watch
- `queue`: A queue.Queue object to pass in ToudaiEvents for new files
- `logger`: A Logger object for Toudai logging
- `interval`: In seconds, how long Toudai should wait before checking for new files again

New events are passed into the queue as TodaiEvents. They each contain four properties:

- `fullpath`: The full path of the new file
- `root`: The root folder of the new file (basically, what folder is storing the file)
- `name`: The new filename itself (just the filename, no path)
- `watch`: The path that Toudai was watching

---

[aleytia](https://github.com/Aleytia) | [best.moe](https://best.moe) | 2019