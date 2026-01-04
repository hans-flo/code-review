import logging
import chromadb
from chromadb.config import Settings
from pathlib import Path

logger = logging.getLogger(__name__)


def preprocess_diff_for_query(diff_content: str) -> str:
    """
    Git diff에서 의미 있는 코드만 추출하여 RAG 쿼리용으로 정제

    제거 대상:
    - @@ ... @@ 헝크 헤더
    - --- a/file, +++ b/file 파일 헤더
    - diff --git, index 라인

    처리:
    - +, -, 공백 접두사 제거하여 순수 코드만 추출
    """
    lines = diff_content.split('\n')
    cleaned_lines = []

    for line in lines:
        # 메타데이터 라인 스킵
        if line.startswith(('@@', '---', '+++', 'diff --git', 'index ')):
            continue

        # +/- /공백 접두사 제거
        if line.startswith(('+', '-', ' ')):
            cleaned_lines.append(line[1:])

    return '\n'.join(cleaned_lines)


class RAGService:
    """ChromaDB 기반 RAG 서비스 - 관련 문서 검색으로 토큰 절약"""

    def __init__(self, db_path: str | None = None):
        # db_path가 없으면 이 파일이 있는 프로젝트 루트 기준으로 chroma_db 디렉터리 사용
        if db_path is None:
            project_root = Path(__file__).resolve().parent
            db_path = project_root / "chroma_db"
        else:
            db_path = Path(db_path)

        logger.debug(f"ChromaDB 경로: {db_path}")
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(db_path),
        ))
        self.collection = self.client.get_or_create_collection(name="code_docs")
        logger.debug(f"ChromaDB 컬렉션 로드 완료: code_docs")

    def add_documents(self, docs: list[str], metadatas: list[dict], ids: list[str]):
        """문서 벡터화 및 저장 (최초 1회 실행용)"""
        logger.info(f"문서 추가 중... ({len(docs)}개)")
        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)
        logger.info(f"문서 추가 완료")

    def search(self, query_text: str, category: str, k: int = 3) -> str:
        """
        카테고리별 관련 문서 검색

        - 특정 category 문서가 하나도 없으면 chromadb가 NoDatapointsException을 던질 수 있어
          안전하게 '관련된 문서가 없습니다.'로 처리합니다.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=k,
                where={"category": category}
            )
        except Exception as e:
            # chromadb.errors.NoDatapointsException 등
            msg = str(e)
            if "No datapoints found" in msg:
                return "관련된 문서가 없습니다."
            raise

        docs = results.get('documents', [[]])
        if not docs or not docs[0]:
            return "관련된 문서가 없습니다."

        return "\n\n".join(docs[0])

    def reset_collection(self, name: str = "code_docs") -> None:
        """컬렉션을 삭제 후 재생성합니다 (초기화/재인덱싱 용)."""
        try:
            self.client.delete_collection(name=name)
        except Exception:
            # 없는 경우 등은 무시
            pass
        self.collection = self.client.get_or_create_collection(name=name)
