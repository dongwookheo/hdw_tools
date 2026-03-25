#!/bin/bash
set -euo pipefail

echo "===== 💻 기본 시스템 정보 ====="
# 운영체제, 커널, 아키텍처
hostnamectl 2>/dev/null | egrep -i 'Operating System|Kernel|Architecture' || true
echo "날짜: $(date +%F\ %T)"
echo

echo "===== 🧠 CPU 정보 ====="
# 모델명, 코어/스레드 수, 소켓 수
lscpu | egrep -i 'Model name|CPU\(s\):|Core\(s\)|Socket\(s\)' || true
echo

echo "===== 💾 RAM / SWAP 정보 ====="
# 전체 메모리, 사용 가능 메모리
free -h
echo

echo "===== 💿 디스크 사용량 ====="
# 파일 시스템별 전체/사용된/남은 용량 (임시 파일 시스템 제외)
df -hT | egrep -v 'tmpfs|devtmpfs' | head -n 1 && df -hT | egrep -v 'tmpfs|devtmpfs' | tail -n +2 | sort -hrk 5 || true
echo

echo "===== 🎮 NVIDIA GPU 정보 ====="
if command -v nvidia-smi >/dev/null 2>&1; then
  # GPU 이름 및 VRAM 총량
  nvidia-smi -L
  echo "--- GPU 상태 (이름, 드라이버, 총 메모리, 사용 메모리, 온도) ---"
  nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,temperature.gpu --format=csv,noheader
  echo
  # CUDA 버전
  echo "CUDA Version (from nvidia-smi banner):"
  nvidia-smi | head -n 5 | egrep -o 'CUDA Version: [0-9.]+' || true
else
  echo "nvidia-smi 명령어를 찾을 수 없습니다."
fi
echo

echo "===== ✅ 완료 ====="
