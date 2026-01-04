import asyncio
import logging
from llm_interface import OpenAIClient  # OpenAIClient, GeminiClient도 사용 가능
from rag_engine import RAGService
from git_analyzer import GitManager
from review_agents import ReviewAgent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 60)
    logger.info("🚀 코드 리뷰 시스템 시작")
    logger.info("=" * 60)

    # 1. 인프라 설정
    logger.info("📦 RAG 서비스 초기화 중...")
    rag = RAGService()
    logger.info("✅ RAG 서비스 초기화 완료")

    logger.info("📦 Git 분석기 초기화 중...")
    git = GitManager()
    logger.info("✅ Git 분석기 초기화 완료")

    # 2. LLM 클라이언트 초기화 (원하는 Provider 선택)

    # Ollama (로컬)
    #llm = OllamaClient(model_name="qwen2.5-coder:14b")

    # OpenAI (환경변수 OPENAI_API_KEY 필요)
    # from llm_interface import OpenAIClient
    logger.info("📦 LLM 클라이언트 초기화 중 (OpenAI gpt-5-2025-08-07)...")
    llm = OpenAIClient(model_name="gpt-5-2025-08-07")
    logger.info("✅ LLM 클라이언트 초기화 완료")

    # Google Gemini (환경변수 GOOGLE_API_KEY 필요)
    # from llm_interface import GeminiClient
    # llm = GeminiClient(model_name="gemini-1.5-flash")

    # 3. 에이전트 초기화 (도메인, 보안, 컨벤션)
    logger.info("📦 리뷰 에이전트 초기화 중...")
    agents = [
        ReviewAgent("Domain Verifier", llm, rag, category="domain"),
        ReviewAgent("Security Auditor", llm, rag, category="security"),
        ReviewAgent("Convention Checker", llm, rag, category="convention"),
    ]
    logger.info(f"✅ {len(agents)}개 에이전트 초기화 완료")

    # 4. 변경된 파일 분석 시작
    logger.info("🔍 변경된 파일 검색 중...")
    changed_files = git.get_diff_files()
    if not changed_files:
        logger.warning("⚠️ 변경 사항이 없습니다.")
        print("변경 사항이 없습니다.")
        return

    logger.info(f"✅ {len(changed_files)}개 파일 변경 감지")
    for idx, file_path in enumerate(changed_files, 1):
        logger.info(f"   [{idx}] {file_path}")

    # 프로젝트 구조 가져오기 (1회만 실행)
    logger.info("🏗️ 프로젝트 구조 분석 중...")
    project_structure = git.get_project_structure()
    logger.info("✅ 프로젝트 구조 분석 완료")

    full_report = []

    for idx, file_path in enumerate(changed_files, 1):
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"📂 [{idx}/{len(changed_files)}] 파일 분석 시작: {file_path}")
        logger.info("=" * 60)
        print(f"\n📂 Analyzing: {file_path} ...")

        logger.info("📖 파일 내용 로드 중...")
        code_content = git.get_file_content(file_path)
        logger.info(f"✅ 파일 내용 로드 완료 ({len(code_content)} bytes)")

        logger.info("🔍 Diff 컨텍스트 추출 중...")
        diff_content = git.get_diff_context(file_path)
        logger.info(f"✅ Diff 컨텍스트 추출 완료 ({len(diff_content)} bytes)")

        # 5. 비동기 병렬 실행 (3명의 에이전트가 동시에 검증)
        logger.info(f"🚀 {len(agents)}개 에이전트 병렬 리뷰 시작...")
        tasks = [agent.review(file_path, code_content, diff_content, project_structure) for agent in agents]
        results = await asyncio.gather(*tasks)
        logger.info("✅ 모든 에이전트 리뷰 완료")

        full_report.append(f"# File: {file_path}\n" + "\n".join(results))

    # 6. 최종 리포트 출력
    logger.info("")
    logger.info("=" * 60)
    logger.info("📝 최종 리포트 생성 중...")
    with open("code_review_report.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_report))
    logger.info("✅ 리포트 파일 저장 완료: code_review_report.md")
    logger.info("=" * 60)
    logger.info("🎉 코드 리뷰 시스템 종료")
    logger.info("=" * 60)
    print("\n✅ 리뷰 완료! 'code_review_report.md'를 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main())
