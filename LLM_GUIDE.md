# LLM Provider 사용 가이드

이 프로젝트는 3가지 LLM Provider를 지원합니다:
- **Ollama** (로컬 실행)
- **OpenAI** (GPT-4, GPT-3.5 등)
- **Google Gemini** (Gemini 1.5 Flash, Pro 등)

## 1. Ollama (로컬)

### 설치
```bash
# Ollama 설치 (https://ollama.ai/)
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull qwen2.5-coder:14b
```

### 사용 예시
```python
from llm_interface import OllamaClient

llm = OllamaClient(model_name="qwen2.5-coder:14b")

# 또는 다른 모델 사용
llm = OllamaClient(model_name="llama3:8b")
```

### 장점
- 무료
- 로컬에서 실행 (인터넷 불필요)
- 데이터 프라이버시 보장

### 단점
- 높은 컴퓨팅 리소스 필요
- 클라우드 모델 대비 성능 낮을 수 있음

---

## 2. OpenAI

### 설치
```bash
pip install openai
```

### API 키 설정
```bash
# 환경변수 설정
export OPENAI_API_KEY="sk-..."

# 또는 코드에서 직접 지정
```

### 사용 예시
```python
from llm_interface import OpenAIClient

# 환경변수에서 API 키 자동 로드
llm = OpenAIClient(model_name="gpt-4o-mini")

# 또는 API 키 직접 지정
llm = OpenAIClient(model_name="gpt-4o", api_key="sk-...")
```

### 지원 모델
- `gpt-4o` - 최신 GPT-4 Omni
- `gpt-4o-mini` - 경량화된 버전 (권장)
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - 저렴한 옵션

### 장점
- 높은 품질
- 빠른 응답 속도
- 안정적인 서비스

### 단점
- 유료 (토큰당 과금)
- 인터넷 필요

---

## 3. Google Gemini

### 설치
```bash
pip install google-genai
```

### API 키 설정
```bash
# Google AI Studio에서 API 키 발급: https://aistudio.google.com/apikey
export GOOGLE_API_KEY="AIza..."
```

### 사용 예시
```python
from llm_interface import GeminiClient

# 환경변수에서 API 키 자동 로드
llm = GeminiClient(model_name="gemini-1.5-flash")

# 또는 API 키 직접 지정
llm = GeminiClient(model_name="gemini-1.5-pro", api_key="AIza...")
```

### 지원 모델
- `gemini-1.5-flash` - 빠르고 경량 (권장)
- `gemini-1.5-pro` - 고성능 모델
- `gemini-2.0-flash-exp` - 실험적 최신 버전

### 장점
- 무료 티어 제공 (일일 한도 내)
- 높은 품질
- 멀티모달 지원

### 단점
- API 키 필요
- 인터넷 필요

---

## 사용 예시 (main.py)

```python
import asyncio
from llm_interface import OllamaClient, OpenAIClient, GeminiClient
from rag_engine import RAGService
from git_analyzer import GitManager
from review_agents import ReviewAgent


async def main():
    rag = RAGService()
    git = GitManager()

    # === Provider 선택 (택 1) ===
    
    # 1. Ollama (로컬)
    llm = OllamaClient(model_name="qwen2.5-coder:14b")
    
    # 2. OpenAI
    # llm = OpenAIClient(model_name="gpt-4o-mini")
    
    # 3. Google Gemini
    # llm = GeminiClient(model_name="gemini-1.5-flash")
    
    # 에이전트 초기화
    agents = [
        ReviewAgent("Domain Verifier", llm, rag, category="domain"),
        ReviewAgent("Security Auditor", llm, rag, category="security"),
        ReviewAgent("Convention Checker", llm, rag, category="convention"),
    ]
    
    # ... 나머지 코드 ...


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 비용 비교

| Provider | 모델 | 1M 입력 토큰 | 1M 출력 토큰 | 무료 티어 |
|----------|------|-------------|-------------|----------|
| Ollama | qwen2.5-coder:14b | 무료 | 무료 | ✅ 무제한 |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 | ❌ |
| OpenAI | gpt-4o | $2.50 | $10.00 | ❌ |
| Gemini | gemini-1.5-flash | 무료* | 무료* | ✅ 15 RPM |
| Gemini | gemini-1.5-pro | 무료* | 무료* | ✅ 2 RPM |

*Gemini 무료 티어: 분당 요청 제한 있음 (RPM = Requests Per Minute)

---

## 권장 설정

### 개발/테스트
- **Ollama** (qwen2.5-coder:14b)
  - 로컬에서 빠르게 테스트 가능
  - 무료

### 프로덕션 (소규모)
- **Gemini** (gemini-1.5-flash)
  - 무료 티어로 시작 가능
  - 높은 품질

### 프로덕션 (대규모)
- **OpenAI** (gpt-4o-mini)
  - 안정적인 서비스
  - 합리적인 비용

---

## 트러블슈팅

### Ollama 연결 실패
```bash
# Ollama 서비스 상태 확인
ollama list

# Ollama 재시작
ollama serve
```

### OpenAI API 키 오류
```bash
# API 키 확인
echo $OPENAI_API_KEY

# API 키 설정 (.zshrc 또는 .bashrc에 추가)
export OPENAI_API_KEY="sk-..."
```

### Gemini API 키 오류
```bash
# API 키 확인
echo $GOOGLE_API_KEY

# API 키 발급: https://aistudio.google.com/apikey
export GOOGLE_API_KEY="AIza..."
```

---

## 성능 비교 (코드 리뷰 기준)

| Provider | 모델 | 속도 | 품질 | 비용 |
|----------|------|------|------|------|
| Ollama | qwen2.5-coder:14b | ⭐⭐⭐ | ⭐⭐⭐⭐ | 무료 |
| OpenAI | gpt-4o-mini | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$ |
| OpenAI | gpt-4o | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$$$ |
| Gemini | gemini-1.5-flash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 무료* |
| Gemini | gemini-1.5-pro | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 무료* |

*무료 티어 한도 내

