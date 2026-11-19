# 🍚 한상차림 AI (Hansang AI)

한국인 영양소 섭취기준(KDRIs) 기반 한식 맞춤형 식단 에이전트 Streamlit 웹 앱

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 한식 3끼 생성 | 아침·점심·저녁 주재료·조리법 중복 없는 맞춤 식단 |
| 영양 밸런스 | 칼로리·탄수화물·단백질·지방 목표 대비 달성률 시각화 |
| AI 채팅 수정 | 자연어로 특정 끼니만 교체, 나머지 유지 |
| 장보기 리스트 | 식재료 카테고리별 체크리스트, 식단 변경 시 자동 동기화 |
| Demo Fallback | API Key 없이도 내장 데이터셋으로 100% 동작 |

---

## 설치 및 실행

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속하세요.

---

## LLM 연동 (선택)

사이드바에서 AI 엔진을 선택하고 API Key를 입력하면 실시간 LLM 식단 생성이 활성화됩니다.

| 엔진 | 모델 | API Key 발급 |
|------|------|-------------|
| Google Gemini | gemini-2.5-flash | [Google AI Studio](https://aistudio.google.com) |
| OpenAI | gpt-4o-mini | [OpenAI Platform](https://platform.openai.com) |

API Key가 없거나 호출 오류 시 자동으로 내장 시연 모드로 전환됩니다.

---

## 프로젝트 구조

```
hansang-ai-streamlit/
├── app.py           # 메인 앱
├── requirements.txt # 의존성 (streamlit>=1.35.0)
└── README.md        # 본 문서
```

---

## 영양 비율 기준

- **끼니 비율:** 아침 27% · 점심 40% · 저녁 33%
- **3끼 합산 오차:** 목표 칼로리 ±10% 이내
- **다양성 규칙:** 아침·점심·저녁 메인 식재료·조리법 중복 금지
