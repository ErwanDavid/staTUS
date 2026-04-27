import datetime
import time
import argparse
import os

import psutil

sep = '\t'

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='System Status Logger')
    parser.add_argument('--sleep', '-s', type=int, default=30, help='Sleep time between logs in seconds')
    parser.add_argument('--logfile', '-l', type=str, default='status_log.tsv', help='Log file name')
    return parser.parse_args()

def round_megabyte(bytes_value):
    return int(round(bytes_value / (1024 * 1024), 0))

def bigger_disk_free_space():
    partitions = psutil.disk_partitions()
    free_spaces = []
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            free_spaces.append(usage.free)
        except PermissionError:
            continue
    return max(free_spaces) if free_spaces else 0

def write_csv_line(a, filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            header = f"Timestamp{sep}System Uptime (s)\
{sep}Avab Mem MB{sep}Total Mem MB{sep}Cached Mem MB{sep}Used Mem MB{sep}Mem Usage %\
{sep}CPU Usage %{sep}Single CPU Max %{sep}Free Disk Space GB{sep}Disk Read MB\
{sep}Disk Write MB{sep}Delta Read MB/s{sep}Delta Write kB/s{sep}Network Sent MB\
{sep}Network Recv MB{sep}Delta Network Sent kB/s{sep}Delta Network Recv kB/s\n"
            f.write(header)
            print(header.strip())
    with open(filename, 'a') as f:
        csv_string =  f"{a['now_string']}{sep}{a['system_uptime']}\
{sep}{a['available_memory_mb']}{sep}{a['total_memory_mb']}{sep}{a['cached_memory_mb']}\
{sep}{a['used_memory_mb']}{sep}{a['memory_usage_percentage']}{sep}\
{a['cpu_usage_percentage']}{sep}{a['max_single_cpu_usage_percentage']}{sep}{a['free_disk_space_gb']}\
{sep}{a['disk_io_read']}{sep}{a['disk_io_write']}{sep}{a['delta_read']}{sep}{a['delta_write']}\
{sep}{a['network_io_sent']}{sep}{a['network_io_recv']}{sep}{a['delta_network_sent']}{sep}{a['delta_network_recv']}\n"
        f.write(csv_string)
        print(csv_string.strip())


def main() -> None:
    args = parse_args()
    sleep_time = args.sleep
    log_file = args.logfile

    previous_read = 0
    previous_write = 0
    previous_network_sent = 0
    previous_network_recv = 0
    while True:
        a={}
        a['now_string'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        a['system_uptime'] = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        a['available_memory_mb'] = round_megabyte(psutil.virtual_memory().available)
        a['total_memory_mb'] = round_megabyte(psutil.virtual_memory().total)
        try:
            a['cached_memory_mb'] = round_megabyte(psutil.virtual_memory().cached)
        except AttributeError:
            a['cached_memory_mb'] = 0
        a['used_memory_mb'] = a['total_memory_mb'] - a['available_memory_mb']
        a['memory_usage_percentage'] = f"{(a['used_memory_mb'] / a['total_memory_mb']) * 100:.1f}"
        a['cpu_usage_percentage'] = f"{psutil.cpu_percent(interval=1):.1f}"
        a['free_disk_space_gb'] = f"{round_megabyte(bigger_disk_free_space())/1024:.1f}"
        a['max_single_cpu_usage_percentage'] = f"{max(psutil.cpu_percent(interval=1, percpu=True)):.1f}"
        a['disk_io_read'] = round_megabyte(psutil.disk_io_counters().read_bytes)
        a['disk_io_write'] = round_megabyte(psutil.disk_io_counters().write_bytes)
        a['delta_read'] = round((a['disk_io_read'] - previous_read) / sleep_time * 1024, 1)
        a['delta_write'] = round((a['disk_io_write'] - previous_write) / sleep_time * 1024, 1)
        previous_read = a['disk_io_read']
        previous_write = a['disk_io_write']
        a['network_io_sent'] = round_megabyte(psutil.net_io_counters().bytes_sent)
        a['network_io_recv'] = round_megabyte(psutil.net_io_counters().bytes_recv)
        a['delta_network_sent'] = round((a['network_io_sent'] - previous_network_sent) / sleep_time * 1024, 1)
        a['delta_network_recv'] = round((a['network_io_recv'] - previous_network_recv) / sleep_time * 1024, 1)
        previous_network_sent = a['network_io_sent']
        previous_network_recv = a['network_io_recv']
        write_csv_line(a, log_file)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()

