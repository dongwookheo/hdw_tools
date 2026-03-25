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
BEGIN {
    # 색상 코드 정의
    RED="\033[31m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    BLUE="\033[34m"
    MAGENTA="\033[35m"
    CYAN="\033[36m"
    GRAY="\033[90m"
    RESET="\033[0m"
}

function get_color(ext) {
    if (ext == "png" || ext == "jpg" || ext == "jpeg" || ext == "gif") return BLUE
    if (ext == "json" || ext == "xml") return GREEN
    if (ext == "txt" || ext == "md") return YELLOW
    if (ext == "js") return CYAN
    if (ext == "css") return MAGENTA
    if (ext == "html") return RED
    if (ext == "pt") return MAGENTA
    return RESET
}

function output_files() {
    if (file_types == "") return

    # 파일 타입들을 분리하고 정렬
    split(file_types, type_array, ",")

    # 간단한 버블 정렬
    for (i = 1; i <= length(type_array); i++) {
        for (j = i + 1; j <= length(type_array); j++) {
            if (type_array[i] > type_array[j]) {
                temp = type_array[i]
                type_array[i] = type_array[j]
                type_array[j] = temp
            }
        }
    }

    # 각 타입별로 출력
    for (i = 1; i <= length(type_array); i++) {
        ext = type_array[i]
        if (ext == "") continue

        color = get_color(ext)
        count = file_count[ext]

        # 각 타입별로 최대 개수만큼 출력
        for (j = 1; j <= count && j <= MAX_FILES_PER_TYPE; j++) {
            key = ext "_" j
            printf "%s%s%s\n", color, file_lines[key], RESET
        }
    }

    # 파일 타입별 총 개수 요약 정보
    summary = ""
    has_hidden = 0

    for (i = 1; i <= length(type_array); i++) {
        ext = type_array[i]
        if (ext == "") continue

        count = file_count[ext]
        color = get_color(ext)

        if (summary != "") summary = summary ", "

        if (count > MAX_FILES_PER_TYPE) {
            # 생략된 파일이 있는 경우: 총 개수 표시
            summary = summary color "." ext " (" count ")" RESET
            has_hidden = 1
        } else {
            # 모든 파일이 표시된 경우: 총 개수만 표시
            summary = summary color "." ext " (" count ")" RESET
        }
    }

    if (summary != "") {
        # 현재 디렉토리의 들여쓰기 추출
        indent = ""
        if (current_dir_line != "") {
            match(current_dir_line, /^[├└│ ]*/)
            base_indent = substr(current_dir_line, 1, RLENGTH)
            gsub(/[├└─]/, " ", base_indent)
            indent = base_indent "    "
        }
        printf "%s%s[%s]%s\n", indent, GRAY, summary, RESET
    }

    # 변수 초기화
    file_types = ""
    delete file_count
    delete file_lines
    delete type_array
}

{
    line = $0

    # 디렉토리나 구조 라인인지 확인
    if (line ~ /^[├└│ ]*[├└]─/ && line !~ /\.[a-zA-Z0-9]+$/) {
        # 이전 디렉토리의 파일들 출력
        output_files()
        print line
        current_dir_line = line
    } else if (line ~ /\.[a-zA-Z0-9]+$/) {
        # 파일인지 확인
        pos = match(line, /\.([a-zA-Z0-9]+)$/)
        if (pos > 0) {
            ext = substr(line, pos + 1)
            ext = tolower(ext)

            # 파일 정보 저장
            file_count[ext]++
            key = ext "_" file_count[ext]
            file_lines[key] = line

            # 파일 타입 목록에 추가 (중복 방지)
            if (index(file_types, ext) == 0) {
                if (file_types != "") file_types = file_types ","
                file_types = file_types ext
            }
        }
    } else if (line !~ /^[├└│ ]*$/) {
        # 기타 라인 (루트나 기타 구조)
        output_files()
        print line
    }
}

END {
    output_files()
}'
