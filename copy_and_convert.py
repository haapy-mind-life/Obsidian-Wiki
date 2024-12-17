import os
import shutil

# 원본 파일 경로
source_dirs = [
    r"G:\내 드라이브\Obsidian_\Study-Idea-Project",
    r"G:\내 드라이브\Obsidian_\Templates",
    r"G:\내 드라이브\Obsidian_\Prompts"
]
# MkDocs 프로젝트 docs 경로
destination = r"C:\Users\jake7\Desktop\my-project\docs"

# 파일 복사 및 변환
for src_dir in source_dirs:
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            src_path = os.path.join(root, file)
            relative_dir = os.path.relpath(root, src_dir)
            dest_dir = os.path.join(destination, relative_dir)
            os.makedirs(dest_dir, exist_ok=True)

            # .txt 파일을 .md로 변환
            if file.endswith(".txt"):
                new_file_name = os.path.splitext(file)[0] + ".md"
                dest_path = os.path.join(dest_dir, new_file_name)
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                shutil.copy(src_path, os.path.join(dest_dir, file))

print(f"Files copied and converted to {destination}")
