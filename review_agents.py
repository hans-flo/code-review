import logging
from llm_interface import LLMProvider
from rag_engine import RAGService, preprocess_diff_for_query

logger = logging.getLogger(__name__)


class ReviewAgent:
    """코드 리뷰 에이전트 - RAG 검색 + LLM 기반 검증"""

    def __init__(self, name: str, llm: LLMProvider, rag: RAGService, category: str):
        self.name = name
        self.llm = llm
        self.rag = rag
        self.category = category

    async def review(self, file_path: str, code_content: str, diff_content: str, project_structure: str) -> str:
        """
        파일에 대한 코드 리뷰 수행

        Args:
            file_path: 대상 파일 경로
            code_content: 파일 전체 내용
            diff_content: git diff 내용

        Returns:
            리뷰 결과 (마크다운 형식)
        """
        logger.info(f"🔍 [{self.name}] 리뷰 시작: {file_path}")

        # 1. RAG: diff 전처리 후 관련 문서 검색
        logger.debug(f"   [{self.name}] Diff 전처리 중...")
        cleaned_diff = preprocess_diff_for_query(diff_content)

        logger.info(f"   [{self.name}] RAG 문서 검색 중 (category={self.category}, k=3)...")
        relevant_docs = self.rag.search(
            query_text=cleaned_diff[:1000],
            category=self.category,
            k=3
        )
        logger.info(f"   [{self.name}] RAG 검색 완료 ({len(relevant_docs)} bytes)")

        # 2. 프롬프트 구성
        logger.debug(f"   [{self.name}] 프롬프트 구성 중...")
        system_prompt = f"""
            당신은 {self.name} 전문가입니다.
            
            [프로젝트 전체 구조]
            아래 트리는 이 프로젝트의 파일 구조입니다. 파일의 위치(패키지)를 보고 아키텍처 의도를 파악하세요.
            {project_structure}
            
            [참고 문서/규칙]
            {relevant_docs}
            """

        user_prompt = f"""[대상 파일] {file_path}

[전체 코드]
{code_content}

[변경 사항 (Git Diff)]
{diff_content}

위 변경 사항에 대해 {self.category} 관점에서 문제점을 지적하세요.
문제가 없다면 'PASS'라고만 답하세요."""

        # 3. LLM 호출
        logger.info(f"🤖 [{self.name}] LLM 호출 중...")
        print(f"🚀 [{self.name}] 검증 시작: {file_path}")
        result = await self.llm.generate(system_prompt, user_prompt)
        logger.info(f"✅ [{self.name}] LLM 응답 완료 ({len(result)} bytes)")

        return f"## 🕵️ {self.name} Review\n{result}\n"
