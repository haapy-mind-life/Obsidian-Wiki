import streamlit as st
import os
import json
from datetime import datetime
import shutil

# 디렉토리 및 파일 설정
DOCS_DIR = "docs"
METADATA_FILE = "metadata.json"

# 메타데이터 로드 함수
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 메타데이터 저장 함수
def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

# 문서명 생성 함수
def generate_filename():
    date_str = datetime.now().strftime("%Y-%m-%d")
    counter = 1
    file_name = f"{date_str}-#{counter}.md"
    while os.path.exists(os.path.join(DOCS_DIR, file_name)):
        counter += 1
        file_name = f"{date_str}-#{counter}.md"
    return file_name

# 문서 생성 함수
def create_document(title, category, tags, content):
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    metadata = load_metadata()
    file_name = generate_filename()

    # Markdown 파일 저장 (Front Matter 사용)
    with open(os.path.join(DOCS_DIR, file_name), "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"category: \"{category}\"\n")
        f.write(f"tags: {json.dumps(tags, ensure_ascii=False)}\n")
        f.write(f"---\n\n")
        f.write(content)

    # JSON 메타데이터 업데이트
    metadata[file_name] = {
        "title": title,
        "category": category,
        "tags": tags
    }
    save_metadata(metadata)

# 문서 목록 불러오기
def get_document_list():
    metadata = load_metadata()
    return list(metadata.keys())

# 문서 내용 로드하기
def load_document_content(file_name):
    with open(os.path.join(DOCS_DIR, file_name), "r", encoding="utf-8") as f:
        lines = f.readlines()
    # front matter 파싱
    # front matter는 --- 로 시작/끝
    # 단순 파싱 예제
    content_start = 0
    front_matter = []
    if lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                content_start = i + 1
                break
            front_matter.append(lines[i].strip())
    content = "".join(lines[content_start:])
    return front_matter, content

# 문서 수정 함수
def update_document(file_name, title, category, tags, content):
    metadata = load_metadata()
    if file_name not in metadata:
        st.error("메타데이터에 해당 문서가 없습니다.")
        return

    # 파일 업데이트
    with open(os.path.join(DOCS_DIR, file_name), "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"category: \"{category}\"\n")
        f.write(f"tags: {json.dumps(tags, ensure_ascii=False)}\n")
        f.write(f"---\n\n")
        f.write(content)

    # 메타데이터 업데이트
    metadata[file_name] = {
        "title": title,
        "category": category,
        "tags": tags
    }
    save_metadata(metadata)

# 문서 삭제 함수
def delete_document(file_name):
    metadata = load_metadata()
    if file_name in metadata:
        del metadata[file_name]
        save_metadata(metadata)
    if os.path.exists(os.path.join(DOCS_DIR, file_name)):
        os.remove(os.path.join(DOCS_DIR, file_name))

def build_and_deploy():
    # mkdocs 빌드 및 gh-deploy 실행
    result_build = os.system("mkdocs build")
    if result_build != 0:
        st.error("mkdocs build 실패!")
        return
    result_deploy = os.system("mkdocs gh-deploy")
    if result_deploy != 0:
        st.error("mkdocs gh-deploy 실패!")
        return
    st.success("정적 사이트 빌드 및 배포 완료!")

# Streamlit UI
st.title("Markdown 문서 관리 및 자동화 시스템")

menu = st.sidebar.selectbox("메뉴", ["문서 생성", "문서 수정", "문서 삭제", "빌드 및 배포"])

if menu == "문서 생성":
    st.header("새 문서 생성")
    title = st.text_input("문서 제목")
    category = st.text_input("카테고리 (예: 대분류 > 소분류)")
    tags_str = st.text_input("태그 (쉼표로 구분)")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    content = st.text_area("문서 내용")

    if st.button("저장"):
        if not title:
            st.error("제목을 입력해주세요.")
        else:
            create_document(title, category, tags, content)
            st.success("문서가 성공적으로 생성되었습니다.")

elif menu == "문서 수정":
    st.header("기존 문서 수정")
    docs = get_document_list()
    if docs:
        selected_file = st.selectbox("수정할 문서를 선택하세요", docs)
        if selected_file:
            metadata = load_metadata()
            doc_meta = metadata[selected_file]
            # 문서 내용 불러오기
            _, old_content = load_document_content(selected_file)

            new_title = st.text_input("문서 제목", value=doc_meta["title"])
            new_category = st.text_input("카테고리", value=doc_meta["category"])
            new_tags_str = st.text_input("태그 (쉼표로 구분)", value=", ".join(doc_meta["tags"]))
            new_tags = [t.strip() for t in new_tags_str.split(",") if t.strip()]
            new_content = st.text_area("문서 내용", value=old_content)

            if st.button("수정"):
                update_document(selected_file, new_title, new_category, new_tags, new_content)
                st.success("문서가 성공적으로 수정되었습니다.")
    else:
        st.info("수정할 문서가 없습니다. 먼저 문서를 생성해주세요.")

elif menu == "문서 삭제":
    st.header("문서 삭제")
    docs = get_document_list()
    if docs:
        selected_file = st.selectbox("삭제할 문서를 선택하세요", docs)
        if selected_file and st.button("삭제"):
            delete_document(selected_file)
            st.success("문서가 성공적으로 삭제되었습니다.")
    else:
        st.info("삭제할 문서가 없습니다.")

elif menu == "빌드 및 배포":
    st.header("정적 사이트 빌드 및 배포")
    if st.button("mkdocs 빌드 및 GitHub Pages 배포"):
        build_and_deploy()
