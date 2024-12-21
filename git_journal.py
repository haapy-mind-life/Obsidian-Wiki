#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from datetime import datetime

def ensure_git_repo():
    # Git 저장소인지 확인
    if not os.path.exists('.git'):
        print("현재 디렉토리에 Git 저장소가 없습니다. 초기화합니다.")
        subprocess.run(['git', 'init'], check=True)

def run_git_command(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print("Git 명령어 실행 중 오류 발생:\n", result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def create_entry(title):
    ensure_git_repo()
    # notes 폴더 생성
    notes_dir = 'notes'
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    # 오늘 날짜를 기반으로 파일명 생성
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_str}.md"
    filepath = os.path.join(notes_dir, filename)

    if os.path.exists(filepath):
        # 이미 오늘 날짜 일지가 있을 경우, 뒤에 시간 정보를 붙여 구분
        time_str = datetime.now().strftime('%H%M%S')
        filename = f"{date_str}-{time_str}.md"
        filepath = os.path.join(notes_dir, filename)

    # 파일 생성
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Date:** {date_str}\n\n")
        f.write("## 오늘 한 일\n- \n\n## 내일 할 일\n- \n")

    print(f"새 일지가 생성되었습니다: {filepath}")

    # Git add & commit
    run_git_command(['git', 'add', filepath])
    run_git_command(['git', 'commit', '-m', f"Add journal entry: {filename}"])
    print(f"Git에 커밋 완료: {filename}")

def list_entries():
    notes_dir = 'notes'
    if not os.path.exists(notes_dir):
        print("아직 일지가 없습니다. `new` 명령으로 일지를 생성해보세요.")
        return
    entries = sorted(os.listdir(notes_dir))
    if not entries:
        print("아직 일지가 없습니다. `new` 명령으로 일지를 생성해보세요.")
        return

    print("현재까지 생성된 일지 목록:")
    for entry in entries:
        if entry.endswith('.md'):
            print(f"- {entry}")

def main():
    parser = argparse.ArgumentParser(description="Git Journal CLI")
    subparsers = parser.add_subparsers(dest='command', help='명령을 선택하세요')

    # new 명령
    new_parser = subparsers.add_parser('new', help='새로운 일지 생성')
    new_parser.add_argument('title', type=str, help='일지의 제목')

    # list 명령
    list_parser = subparsers.add_parser('list', help='기존 일지 목록 조회')

    args = parser.parse_args()

    if args.command == 'new':
        create_entry(args.title)
    elif args.command == 'list':
        list_entries()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
