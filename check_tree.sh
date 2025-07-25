#!/bin/bash

show_usage() {
    echo "사용법: $0 [-n 파일수] [경로]"
    echo "  -n: 각 파일 타입별 최대 표시 개수 (기본값: 2)"
    echo "  경로: 트리를 표시할 디렉토리 경로 (생략시 현재 디렉토리)"
}

MAX_FILES_PER_TYPE=2  # 기본값 설정

# 명령행 인자 처리
while getopts "hn:" opt; do
    case $opt in
        h)
            show_usage
            exit 0
            ;;
        n)
            MAX_FILES_PER_TYPE=$OPTARG
            ;;
        \?)
            echo "잘못된 옵션입니다."
            show_usage
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

TARGET_PATH="${1:-.}"

if [ ! -d "$TARGET_PATH" ]; then
    echo "오류: '$TARGET_PATH' 디렉토리가 존재하지 않습니다."
    exit 1
fi

FULL_PATH=$(realpath "$TARGET_PATH" 2>/dev/null || readlink -f "$TARGET_PATH" 2>/dev/null || echo "$TARGET_PATH")

echo "디렉토리: $FULL_PATH"
echo "각 파일 타입별로 디렉토리당 최대 ${MAX_FILES_PER_TYPE}개까지 표시됩니다."
echo "----------------------------------------"

cd "$TARGET_PATH" && tree -a | \
awk -v MAX_FILES_PER_TYPE="$MAX_FILES_PER_TYPE" '
{
    line = $0

    # 파일명에서 확장자 찾기
    if (line ~ /\.[a-zA-Z0-9]+$/) {
        # 마지막 점 이후를 확장자로 추출
        pos = match(line, /\.([a-zA-Z0-9]+)$/)
        if (pos > 0) {
            ext = substr(line, pos + 1)
            ext = tolower(ext)

            if (cnt[ext] < MAX_FILES_PER_TYPE) {
                print line
                cnt[ext]++
            } else if (cnt[ext] == MAX_FILES_PER_TYPE) {
                print "    ... (더 많은 ." ext " 파일들)"
                cnt[ext]++
            }
        } else {
            print line
        }
    } else {
        # 디렉토리 또는 확장자 없는 파일
        delete cnt
        print line
    }
}'
