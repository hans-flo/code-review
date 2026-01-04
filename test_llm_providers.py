"""
LLM Provider 구현 테스트 스크립트
각 Provider가 정상적으로 import 되는지 확인
"""

import asyncio


async def test_providers():
    print("=== LLM Providers 테스트 ===\n")

    # 1. Ollama
    try:
        from llm_interface import OllamaClient
        print("✓ OllamaClient import 성공")
    except Exception as e:
        print(f"✗ OllamaClient import 실패: {e}")

    # 2. OpenAI
    try:
        from llm_interface import OpenAIClient
        print("✓ OpenAIClient import 성공")
    except Exception as e:
        print(f"✗ OpenAIClient import 실패: {e}")

    # 3. Gemini
    try:
        from llm_interface import GeminiClient
        print("✓ GeminiClient import 성공")
    except Exception as e:
        print(f"✗ GeminiClient import 실패: {e}")

    print("\n=== Provider 인스턴스 생성 테스트 ===\n")

    # Ollama 인스턴스 생성 테스트 (실제 Ollama 서버 없이도 객체 생성은 가능)
    try:
        from llm_interface import OllamaClient
        ollama = OllamaClient(model_name="qwen2.5-coder:14b")
        print(f"✓ OllamaClient 인스턴스 생성 성공: {ollama.model_name}")
    except Exception as e:
        print(f"✗ OllamaClient 인스턴스 생성 실패: {e}")

    # OpenAI 인스턴스 생성 테스트 (API Key 없이도 객체 생성은 가능)
    try:
        from llm_interface import OpenAIClient
        openai = OpenAIClient(model_name="gpt-4o-mini")
        print(f"✓ OpenAIClient 인스턴스 생성 성공: {openai.model_name}")
    except Exception as e:
        print(f"✗ OpenAIClient 인스턴스 생성 실패: {e}")

    # Gemini 인스턴스 생성 테스트 (API Key 없으면 실패할 수 있음)
    try:
        from llm_interface import GeminiClient
        gemini = GeminiClient(model_name="gemini-1.5-flash")
        print(f"✓ GeminiClient 인스턴스 생성 성공: {gemini.model_name}")
    except Exception as e:
        print(f"✗ GeminiClient 인스턴스 생성 실패: {e}")

    print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_providers())

