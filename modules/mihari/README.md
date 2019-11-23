# Mihari

## Introduction

Mihari (見張り, lit. "watchman") is a lightweight, functionally minimal filesystem watcher designed specifically for Izumi's use. It tracks a given path for all new files and reports them when they appear.

## Usage

Mihari contains one primary method (which will act as a never-ending loop):
- `def watch(path: str, queue: Queue, logger: LoggerUtils, sleeper: SleepUtils, interval: int = 5, ) -> None`

Arguments:
- `path`: The system path for Mihari to watch
- `queue`: A queue.Queue object to pass in MihariEvents for new files
- `logger`: A LoggerUtil object for Mihari logging
- `sleeper`: A SleepUtil object for Mihari sleep casting
- `interval`: In seconds, how long Mihari should wait before checking for new files again

New events are passed into the queue as TodaiEvents. They each contain four properties:

- `fullpath`: The full path of the new file
- `root`: The root folder of the new file (basically, what folder is storing the file)
- `name`: The new filename itself (just the filename, no path)
- `watch`: The path that Mihari was watching

---

[aleytia](https://github.com/Aleytia) | [best.moe](https://best.moe) | 2019