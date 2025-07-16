#!/bin/zsh

# MacOS용: 홈 디렉토리 및 Python 경로 주의
cd /Users/rion5/Zena/py-quant/ || exit

# 로그 디렉토리 확인
mkdir -p log

# 실제 Python 스크립트 실행
/opt/miniconda3/envs/zena/bin/python -m data.save_daily_data >> log/cron_log_$(date +%Y-%m-%d).log 2>&1
