#!/bin/bash

# 获取进程名或PID
PROCESS_NAME="$1"
PID="$1"
echo $PID

if [ -z "$PID" ]; then
    echo "进程未找到: $PROCESS_NAME"
    exit 1
fi

INTERVAL=1  # 采集间隔（秒）
LOG_FILE="usage.csv"

# 写入CSV头部
echo "timestamp,cpu_percent,mem_percent,vsize_kb,rss_kb" > "$LOG_FILE"

while true; do
    if ! ps -p "$PID" > /dev/null; then
        echo "进程 $PID 已终止"
        exit 1
    fi
    # 获取CPU、内存数据
    STATS=$(ps -p "$PID" -o %cpu,%mem,vsize,rss | tail -n1 | xargs | sed 's/ /,/g')
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$TIMESTAMP,$STATS" >> "$LOG_FILE"
    sleep "$INTERVAL"
done