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
python -m venv ~/venv
source ~/venv/bin/activate  # On Windows use `venv\Scripts\activate`
python -m pip install .
```
few moments later...
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

Important:
- if you want to run the status_log in the background, you can use `nohup` on Linux:

```bash
nohup status-log --sleep 30 --logfile status_log.tsv &
```
- on Windows, you can use `start` command:

```bash
start /B status-log --sleep 30 --logfile status_log.tsv
```

- each time you need to activate the virtual environment before running the command, or you can add the `venv\Scripts` directory to your system PATH variable for easier access.    

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
