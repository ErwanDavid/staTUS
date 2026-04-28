# status-monitor

Simple (2 files) cross-platform system status logger and web dashboard.
Logged info:
- Uptime
- CPU usage
- Memory usage
- Disk usage
- Network usage

Todo: 
- File rotate

## Install (Windows and Linux)

From a cloned repository:

```bash
python -m pip install .
```
You can then run the logger and dashboard from the command line:

## Commands

Start logging machine metrics to a TSV file:

```bash
status-log --sleep 30 --logfile status_log.tsv
```
or simply:
```bash
status-log
```

Start the dashboard:

```bash
status-dashboard --file status_log.tsv --host 127.0.0.1 --port 8050
```
or simply:
```bash
status-dashboard
```

Finally, open:

- http://127.0.0.1:8050

Refresh browser to pick up latest file changes.
