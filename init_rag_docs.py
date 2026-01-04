"""RAG 테스트용 샘플 문서 초기화 스크립트"""

import os
from rag_engine import RAGService


def load_domain_documents():
    """domain.md 파일을 읽어서 섹션별로 문서를 분리합니다."""
    domain_file_path = os.path.join(os.path.dirname(__file__), "docs", "domain.md")

    if not os.path.exists(domain_file_path):
        print(f"⚠️  domain.md 파일을 찾을 수 없습니다: {domain_file_path}")
        return []

    with open(domain_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 문서를 의미있는 단위로 분할 (섹션 기반)
    docs = []
    current_section = []
    lines = content.split("\n")

    for line in lines:
        # 빈 줄이 2개 이상 연속되면 새로운 섹션으로 간주
        if line.strip():
            current_section.append(line)
        elif current_section:
            # 현재 섹션을 저장
            section_text = "\n".join(current_section).strip()
            if len(section_text) > 50:  # 최소 길이 필터
                docs.append(section_text)
            current_section = []

    # 마지막 섹션 추가
    if current_section:
        section_text = "\n".join(current_section).strip()
        if len(section_text) > 50:
            docs.append(section_text)

    return docs


def init_sample_documents():
    rag = RAGService()

    # 기존 컬렉션을 초기화 (재실행해도 안전)
    rag.reset_collection(name="code_docs")

    # domain.md 파일에서 문서 로드
    domain_docs = load_domain_documents()

    # 보안 규칙 문서 (기본 제공)
    security_docs = [
        "SQL Injection 방지를 위해 반드시 PreparedStatement 또는 ORM의 파라미터 바인딩을 사용해야 한다. 문자열 연결로 쿼리를 생성하지 말 것.",
        "사용자 입력값은 반드시 검증(Validation)과 이스케이프(Escape) 처리를 해야 한다. XSS 공격 방지를 위해 HTML 출력 시 인코딩 필수.",
        "비밀번호는 평문 저장 금지. bcrypt, scrypt, argon2 등의 안전한 해싱 알고리즘을 사용해야 한다. 솔트(salt)는 자동 생성되는 것을 사용할 것.",
        "API 엔드포인트는 인증(Authentication)과 인가(Authorization) 검증을 필수로 해야 한다. 민감한 데이터 접근 시 추가 권한 검증 필요.",
        "로그에 비밀번호, API 키, 개인정보(주민번호, 카드번호 등)를 출력하지 말 것. 마스킹 처리 필수.",
    ]

    # 컨벤션 규칙 문서 (기본 제공)
    convention_docs = [
        "함수명은 동사로 시작해야 한다 (예: get_user, create_order, validate_input). 클래스명은 명사형 PascalCase를 사용한다.",
        "한 함수는 하나의 역할만 수행해야 한다 (Single Responsibility). 함수 길이는 30줄 이내를 권장하며, 50줄을 초과하면 분리를 검토한다.",
        "매직 넘버 사용 금지. 상수로 정의하고 의미 있는 이름을 부여해야 한다 (예: MAX_RETRY_COUNT = 3).",
        "예외 처리 시 빈 catch 블록 금지. 최소한 로깅을 수행하거나, 예외를 상위로 전파해야 한다.",
        "코드 중복(DRY 원칙 위반)을 피해야 한다. 3번 이상 반복되는 로직은 함수로 추출한다.",
    ]

    if not domain_docs and not security_docs and not convention_docs:
        print("❌ 로드할 문서가 없습니다.")
        return

    # 문서 추가
    all_docs: list[str] = []
    all_metadatas: list[dict] = []
    all_ids: list[str] = []

    for i, doc in enumerate(domain_docs):
        all_docs.append(doc)
        all_metadatas.append({"category": "domain", "source": "docs/domain.md"})
        all_ids.append(f"domain_{i+1}")

    for i, doc in enumerate(security_docs):
        all_docs.append(doc)
        all_metadatas.append({"category": "security", "source": "built-in"})
        all_ids.append(f"security_{i+1}")

    for i, doc in enumerate(convention_docs):
        all_docs.append(doc)
        all_metadatas.append({"category": "convention", "source": "built-in"})
        all_ids.append(f"convention_{i+1}")

    rag.add_documents(docs=all_docs, metadatas=all_metadatas, ids=all_ids)

    print(f"✅ RAG 문서 초기화 완료!")
    print(f"   - Domain 문서: {len(domain_docs)}개")
    print(f"   - Security 문서: {len(security_docs)}개")
    print(f"   - Convention 문서: {len(convention_docs)}개")
    print(f"   - 총 {len(all_docs)}개 문서 저장됨")


if __name__ == "__main__":
    init_sample_documents()
