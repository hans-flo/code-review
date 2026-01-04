# API 키 설정 가이드

## 1. .env 파일 생성

프로젝트 루트에 `.env` 파일을 만들고 아래와 같이 API 키를 입력하세요:

```bash
# .env 파일 예시
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxx
```

## 2. API 키 발급 방법

### OpenAI API Key
1. https://platform.openai.com/api-keys 접속
2. 로그인 후 "Create new secret key" 클릭
3. 생성된 키를 `.env` 파일의 `OPENAI_API_KEY`에 입력

### Google Gemini API Key
1. https://aistudio.google.com/app/apikey 접속
2. 로그인 후 "Create API key" 클릭
3. 생성된 키를 `.env` 파일의 `GOOGLE_API_KEY`에 입력

## 3. 의존성 설치

```bash
pip install -r requirements.txt
```

## 4. 사용 방법

```python
from llm_interface import OpenAIClient, GeminiClient

# API 키는 자동으로 .env 파일에서 로드됨
client = OpenAIClient()
response = await client.generate(
    system_prompt="You are a helpful assistant",
    user_prompt="Hello!"
)
```

## 보안 주의사항

- ⚠️ `.env` 파일은 **절대 Git에 커밋하지 마세요**
- `.gitignore`에 `.env`가 추가되어 있는지 확인하세요
- API 키가 노출되면 즉시 재발급하세요

