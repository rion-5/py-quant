#!/bin/bash

# Ubuntu용: 홈 디렉토리 경로만 변경
cd /home/rion5/Zena/py-quant/ || exit

# 로그 디렉토리 확인
mkdir -p /home/rion5/Zena/py-quant/log


# 실제 Python 스크립트 실행
/home/rion5/miniconda3/envs/zena/bin/python -m data.save_daily_data >> /home/rion5/Zena/py-quant/log/cron_log_$(date +%Y-%m-%d).log 2>&1
