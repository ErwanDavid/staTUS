# status-monitor

Cross-platform system status logger and dashboard.

## Install (Windows and Linux)

From a cloned repository:

```bash
python -m pip install .
```

For editable development install:

```bash
python -m pip install -e .
```

## Commands

Start logging machine metrics to a TSV file:

```bash
status-log --sleep 30 --logfile status_log.tsv
```

Start the dashboard:

```bash
status-dashboard --file status_log.tsv --host 127.0.0.1 --port 8050
```

Then open:

- http://127.0.0.1:8050

## Quick start workflow

1. Start logger in terminal 1:

```bash
status-log
```

2. Start dashboard in terminal 2:

```bash
status-dashboard
```

3. Refresh browser to pick up latest file changes.

## Uninstall

```bash
python -m pip uninstall status-monitor
```
