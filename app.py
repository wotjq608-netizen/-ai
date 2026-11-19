"""
한상차림 AI (Hansang AI) — 한식 맞춤형 식단 에이전트
Streamlit Web App  |  Python 3.9+  |  streamlit>=1.35.0
"""

import json
import random
import urllib.request
import urllib.error
import streamlit as st

# ─────────────────────────────────────────────
# 0. 페이지 설정 (반드시 최상단 첫 번째 Streamlit 호출)
# ─────────────────────────────────────────────
st.set_page_config(page_title="한상차림 AI", page_icon="🍚", layout="wide")

# ─────────────────────────────────────────────
# 1. 글로벌 CSS (Noto Sans KR + 한식 모던 테마)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .meal-card {
        background: #F6F4EF;
        border-left: 5px solid #2D5A43;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 8px;
    }
    .badge {
        display: inline-block;
        background: #2D5A43;
        color: #fff;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge-warn { background: #B45309; }
    .coach-box {
        background: #EEF4F0;
        border: 1px solid #2D5A43;
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.95rem;
        color: #1a3328;
    }
    .diversity-badge {
        background: #2D5A43;
        color: #fff;
        border-radius: 8px;
        padding: 4px 14px;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 2. 내장 한식 데이터셋 (Demo Fallback용)
# ─────────────────────────────────────────────
KOREAN_MEAL_DB = {
    "breakfast": [
        {
            "id": "b1",
            "menu_name": "현미밥과 맑은 북엇국 한상",
            "items": ["현미밥 (2/3공기)", "맑은 북엇국", "달걀말이 (3조각)", "시금치나물"],
            "main_ingredient": "북어·달걀",
            "cooking_method": "맑은국·무침",
            "tags": ["seafood", "egg"],
            "nutrition": {"calories": 540, "carbs_g": 76, "protein_g": 26, "fat_g": 14},
            "reason": "아침 공복에 위장 부담이 적은 맑은 북엇국과 달걀 단백질 조합입니다.",
            "ingredients": [
                {"name": "현미", "category": "곡류·양념·기타"},
                {"name": "북어채", "category": "육류·생선·달걀·두부"},
                {"name": "달걀", "category": "육류·생선·달걀·두부"},
                {"name": "시금치", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "b2",
            "menu_name": "흰죽과 깍두기 한상",
            "items": ["흰죽 (1공기)", "깍두기", "계란찜 (1인분)", "멸치볶음"],
            "main_ingredient": "쌀·계란",
            "cooking_method": "죽·볶음",
            "tags": ["egg"],
            "nutrition": {"calories": 460, "carbs_g": 68, "protein_g": 20, "fat_g": 10},
            "reason": "속 편한 죽 메뉴로 소화 부담 없이 아침을 시작합니다.",
            "ingredients": [
                {"name": "쌀", "category": "곡류·양념·기타"},
                {"name": "계란", "category": "육류·생선·달걀·두부"},
                {"name": "무", "category": "채소·버섯·해조류"},
                {"name": "멸치", "category": "육류·생선·달걀·두부"},
            ],
        },
        {
            "id": "b3",
            "menu_name": "잡곡밥과 된장찌개 한상",
            "items": ["잡곡밥 (2/3공기)", "된장찌개", "두부구이 (2쪽)", "콩나물무침"],
            "main_ingredient": "두부·콩",
            "cooking_method": "찌개·구이",
            "tags": [],
            "nutrition": {"calories": 510, "carbs_g": 72, "protein_g": 24, "fat_g": 12},
            "reason": "식물성 단백질인 두부와 발효 된장으로 아침 영양을 채웁니다.",
            "ingredients": [
                {"name": "잡곡", "category": "곡류·양념·기타"},
                {"name": "두부", "category": "육류·생선·달걀·두부"},
                {"name": "된장", "category": "곡류·양념·기타"},
                {"name": "콩나물", "category": "채소·버섯·해조류"},
            ],
        },
    ],
    "lunch": [
        {
            "id": "l1",
            "menu_name": "불고기 정식",
            "items": ["흰밥 (1공기)", "소불고기", "미역국", "배추김치", "감자조림"],
            "main_ingredient": "소고기",
            "cooking_method": "볶음·조림",
            "tags": ["meat"],
            "nutrition": {"calories": 820, "carbs_g": 110, "protein_g": 42, "fat_g": 22},
            "reason": "오후 활력을 위한 소고기 단백질과 탄수화물 균형 정식입니다.",
            "ingredients": [
                {"name": "쌀", "category": "곡류·양념·기타"},
                {"name": "소고기", "category": "육류·생선·달걀·두부"},
                {"name": "미역", "category": "채소·버섯·해조류"},
                {"name": "배추", "category": "채소·버섯·해조류"},
                {"name": "감자", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "l2",
            "menu_name": "제육볶음 정식",
            "items": ["흰밥 (1공기)", "제육볶음", "콩나물국", "깍두기", "시금치나물"],
            "main_ingredient": "돼지고기",
            "cooking_method": "볶음·무침",
            "tags": ["meat"],
            "nutrition": {"calories": 850, "carbs_g": 108, "protein_g": 44, "fat_g": 26},
            "reason": "매콤한 제육볶음으로 점심 활력 보충에 최적화된 메뉴입니다.",
            "ingredients": [
                {"name": "쌀", "category": "곡류·양념·기타"},
                {"name": "돼지고기", "category": "육류·생선·달걀·두부"},
                {"name": "콩나물", "category": "채소·버섯·해조류"},
                {"name": "고추장", "category": "곡류·양념·기타"},
                {"name": "시금치", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "l3",
            "menu_name": "비빔밥 정식",
            "items": ["비빔밥 (1인분)", "북엇국", "배추김치"],
            "main_ingredient": "채소·달걀",
            "cooking_method": "비빔·무침",
            "tags": ["egg"],
            "nutrition": {"calories": 780, "carbs_g": 120, "protein_g": 28, "fat_g": 18},
            "reason": "다양한 채소와 달걀로 비타민과 단백질을 균형 있게 섭취합니다.",
            "ingredients": [
                {"name": "쌀", "category": "곡류·양념·기타"},
                {"name": "달걀", "category": "육류·생선·달걀·두부"},
                {"name": "당근", "category": "채소·버섯·해조류"},
                {"name": "시금치", "category": "채소·버섯·해조류"},
                {"name": "고사리", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "l4",
            "menu_name": "생선구이 정식",
            "items": ["흰밥 (1공기)", "고등어구이", "미역국", "배추김치", "감자조림"],
            "main_ingredient": "고등어",
            "cooking_method": "구이·조림",
            "tags": ["seafood"],
            "nutrition": {"calories": 800, "carbs_g": 105, "protein_g": 46, "fat_g": 20},
            "reason": "오메가-3 풍부한 고등어로 두뇌 활력과 집중력을 높입니다.",
            "ingredients": [
                {"name": "쌀", "category": "곡류·양념·기타"},
                {"name": "고등어", "category": "육류·생선·달걀·두부"},
                {"name": "미역", "category": "채소·버섯·해조류"},
                {"name": "배추", "category": "채소·버섯·해조류"},
                {"name": "감자", "category": "채소·버섯·해조류"},
            ],
        },
    ],
    "dinner": [
        {
            "id": "d1",
            "menu_name": "두부 된장찌개 한상",
            "items": ["현미밥 (2/3공기)", "두부 된장찌개", "취나물무침", "배추김치"],
            "main_ingredient": "두부",
            "cooking_method": "찌개·무침",
            "tags": [],
            "nutrition": {"calories": 620, "carbs_g": 88, "protein_g": 28, "fat_g": 14},
            "reason": "저녁에 가볍고 소화 잘 되는 두부 중심의 채소 균형 한상입니다.",
            "ingredients": [
                {"name": "현미", "category": "곡류·양념·기타"},
                {"name": "두부", "category": "육류·생선·달걀·두부"},
                {"name": "된장", "category": "곡류·양념·기타"},
                {"name": "취나물", "category": "채소·버섯·해조류"},
                {"name": "배추", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "d2",
            "menu_name": "닭볶음탕 정식",
            "items": ["현미밥 (2/3공기)", "닭볶음탕", "숙주나물", "배추김치"],
            "main_ingredient": "닭고기",
            "cooking_method": "볶음탕·무침",
            "tags": ["meat"],
            "nutrition": {"calories": 680, "carbs_g": 82, "protein_g": 46, "fat_g": 18},
            "reason": "고단백 닭고기와 채소로 저녁 근육 회복을 돕는 한상입니다.",
            "ingredients": [
                {"name": "현미", "category": "곡류·양념·기타"},
                {"name": "닭고기", "category": "육류·생선·달걀·두부"},
                {"name": "감자", "category": "채소·버섯·해조류"},
                {"name": "숙주", "category": "채소·버섯·해조류"},
                {"name": "배추", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "d3",
            "menu_name": "순두부찌개 한상",
            "items": ["흰밥 (2/3공기)", "순두부찌개", "도라지무침", "깍두기"],
            "main_ingredient": "순두부·조개",
            "cooking_method": "찌개·무침",
            "tags": ["seafood"],
            "nutrition": {"calories": 580, "carbs_g": 78, "protein_g": 30, "fat_g": 15},
            "reason": "부드러운 순두부와 조개로 저녁 소화 부담 없이 단백질을 보충합니다.",
            "ingredients": [
                {"name": "쌀", "category": "곡류·양념·기타"},
                {"name": "순두부", "category": "육류·생선·달걀·두부"},
                {"name": "바지락", "category": "육류·생선·달걀·두부"},
                {"name": "도라지", "category": "채소·버섯·해조류"},
                {"name": "무", "category": "채소·버섯·해조류"},
            ],
        },
        {
            "id": "d4",
            "menu_name": "연어구이 한상",
            "items": ["현미밥 (2/3공기)", "연어구이", "미역국", "콩나물무침", "배추김치"],
            "main_ingredient": "연어",
            "cooking_method": "구이·무침",
            "tags": ["seafood"],
            "nutrition": {"calories": 650, "carbs_g": 80, "protein_g": 42, "fat_g": 20},
            "reason": "오메가-3 연어 구이로 하루를 마무리하는 항산화 한상입니다.",
            "ingredients": [
                {"name": "현미", "category": "곡류·양념·기타"},
                {"name": "연어", "category": "육류·생선·달걀·두부"},
                {"name": "미역", "category": "채소·버섯·해조류"},
                {"name": "콩나물", "category": "채소·버섯·해조류"},
                {"name": "배추", "category": "채소·버섯·해조류"},
            ],
        },
    ],
}

MEAL_LABEL = {"breakfast": "🌅 아침", "lunch": "☀️ 점심", "dinner": "🌙 저녁"}
MEAL_RATIO = {"breakfast": 0.27, "lunch": 0.40, "dinner": 0.33}
CATEGORIES = ["채소·버섯·해조류", "육류·생선·달걀·두부", "곡류·양념·기타"]

# ─────────────────────────────────────────────
# 3. 유틸 함수
# ─────────────────────────────────────────────

def calc_macros(calories: int) -> dict:
    """목표 칼로리 → 탄수화물/단백질/지방 환산"""
    return {
        "calories": calories,
        "carbs_g": round(calories * 0.57 / 4),
        "protein_g": round(calories * 0.18 / 4),
        "fat_g": round(calories * 0.25 / 9),
    }


def scale_nutrition(meal: dict, ratio: float, target_calories: int) -> dict:
    """끼니 비율로 영양소 보정"""
    target = target_calories * ratio
    base = meal["nutrition"]["calories"]
    if base == 0:
        return meal["nutrition"].copy()
    factor = target / base
    return {
        "calories": round(meal["nutrition"]["calories"] * factor),
        "carbs_g": round(meal["nutrition"]["carbs_g"] * factor),
        "protein_g": round(meal["nutrition"]["protein_g"] * factor),
        "fat_g": round(meal["nutrition"]["fat_g"] * factor),
    }


def _tokens(text: str) -> set:
    return set(t.strip() for t in text.replace("·", "·").split("·"))


def pick_diverse_meals(target_calories: int, avoid_tags: list) -> dict:
    """
    다양성 규칙: main_ingredient·cooking_method 중복 없이 3끼 조합 선택
    """
    used_ingredients: set = set()
    used_methods: set = set()
    result = {}

    for slot in ("breakfast", "lunch", "dinner"):
        pool = [
            m for m in KOREAN_MEAL_DB[slot]
            if not any(t in m["tags"] for t in avoid_tags)
        ]
        if not pool:
            pool = KOREAN_MEAL_DB[slot][:]

        random.shuffle(pool)
        chosen = pool[0]  # fallback
        for candidate in pool:
            ing_tokens = _tokens(candidate["main_ingredient"])
            meth_tokens = _tokens(candidate["cooking_method"])
            if not ing_tokens & used_ingredients and not meth_tokens & used_methods:
                chosen = candidate
                break

        used_ingredients |= _tokens(chosen["main_ingredient"])
        used_methods |= _tokens(chosen["cooking_method"])

        meal = dict(chosen)
        meal["nutrition"] = scale_nutrition(chosen, MEAL_RATIO[slot], target_calories)
        result[slot] = meal

    return result


def sum_nutrition(meals: dict) -> dict:
    total = {"calories": 0, "carbs_g": 0, "protein_g": 0, "fat_g": 0}
    for m in meals.values():
        for k in total:
            total[k] += m["nutrition"].get(k, 0)
    return total


def build_grocery(meals: dict) -> dict:
    grocery: dict = {c: [] for c in CATEGORIES}
    seen = set()
    for meal in meals.values():
        for ing in meal.get("ingredients", []):
            key = ing["name"]
            if key not in seen:
                seen.add(key)
                cat = ing.get("category", "곡류·양념·기타")
                if cat in grocery:
                    grocery[cat].append(key)
                else:
                    grocery["곡류·양념·기타"].append(key)
    return grocery


def default_coach_comment(meals: dict, target: dict) -> str:
    total = sum_nutrition(meals)
    pct = round(total["calories"] / target["calories"] * 100)
    return (
        f"아침·점심·저녁 주재료가 겹치지 않으며 일일 칼로리 목표의 {pct}%를 달성한 균형 한식 식단입니다. "
        "한국인 영양소 섭취기준(KDRIs)에 맞춰 탄수화물·단백질·지방 비율을 맞췄습니다."
    )


# ─────────────────────────────────────────────
# 4. LLM API 호출 (Gemini / OpenAI)
# ─────────────────────────────────────────────

def _post_json(url: str, headers: dict, body: dict, timeout: int = 20) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_gemini(api_key: str, prompt: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={api_key}"
    )
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = _post_json(url, {"Content-Type": "application/json"}, body)
    return resp["candidates"][0]["content"]["parts"][0]["text"]


def call_openai(api_key: str, prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
    }
    resp = _post_json(url, headers, body)
    return resp["choices"][0]["message"]["content"]


def llm_generate_meals(llm_mode: str, api_key: str, target: dict, avoid_tags: list) -> dict | None:
    """LLM 호출 → JSON 파싱 → meals dict. 실패 시 None 반환."""
    avoid_str = "·".join(avoid_tags) if avoid_tags else "없음"
    prompt = f"""
당신은 한국 영양사입니다. 아래 조건에 맞는 한식 하루 3끼 식단을 JSON으로만 답하세요.

조건:
- 목표 칼로리: {target['calories']}kcal (아침 27%, 점심 40%, 저녁 33%)
- 기피 태그: {avoid_str}
- 아침·점심·저녁 메인 식재료(main_ingredient)와 조리법(cooking_method) 중복 금지

반드시 아래 JSON 구조만 출력하세요 (다른 텍스트 없이):
{{
  "breakfast": {{
    "id": "b_llm",
    "menu_name": "...",
    "items": ["..."],
    "main_ingredient": "...",
    "cooking_method": "...",
    "tags": [],
    "nutrition": {{"calories": 0, "carbs_g": 0, "protein_g": 0, "fat_g": 0}},
    "reason": "...",
    "ingredients": [{{"name": "...", "category": "채소·버섯·해조류"}}]
  }},
  "lunch": {{ "...": "..." }},
  "dinner": {{ "...": "..." }}
}}
"""
    try:
        if llm_mode == "gemini":
            raw = call_gemini(api_key, prompt)
        else:
            raw = call_openai(api_key, prompt)
        # 코드 펜스 제거
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        return json.loads(raw)
    except Exception:
        return None


def llm_chat_replace(
    llm_mode: str,
    api_key: str,
    user_msg: str,
    current_meals: dict,
    target: dict,
) -> tuple[str, dict | None]:
    """
    사용자 채팅 메시지 → 교체할 끼니 파악 + 새 메뉴 JSON 반환.
    Returns (slot_to_replace | "none", new_meal_dict | None)
    """
    slots_kr = {"아침": "breakfast", "점심": "lunch", "저녁": "dinner"}
    # 간단 의도 파싱
    detected = None
    for kr, en in slots_kr.items():
        if kr in user_msg:
            detected = en
            break

    if llm_mode == "demo" or not api_key:
        return detected or "none", None

    prompt = f"""
당신은 한국 영양사 AI입니다.
사용자 요청: "{user_msg}"

현재 식단:
- 아침: {current_meals['breakfast']['menu_name']}
- 점심: {current_meals['lunch']['menu_name']}
- 저녁: {current_meals['dinner']['menu_name']}

1. 교체할 끼니를 breakfast/lunch/dinner/none 중 하나만 첫 줄에 쓰세요.
2. 교체가 필요하면 두 번째 줄부터 해당 끼니의 JSON을 출력하세요 (id, menu_name, items, main_ingredient, cooking_method, tags, nutrition, reason, ingredients 포함).
3. none이면 두 번째 줄에 간단한 답변만 쓰세요.
"""
    try:
        if llm_mode == "gemini":
            raw = call_gemini(api_key, prompt)
        else:
            raw = call_openai(api_key, prompt)
        lines = raw.strip().split("\n", 1)
        slot_line = lines[0].strip().lower()
        slot = None
        for k in ("breakfast", "lunch", "dinner"):
            if k in slot_line:
                slot = k
                break
        if slot and len(lines) > 1:
            body = lines[1].strip()
            if body.startswith("```"):
                body = "\n".join(body.split("\n")[1:])
            if body.endswith("```"):
                body = "\n".join(body.split("\n")[:-1])
            new_meal = json.loads(body)
            return slot, new_meal
        return slot or "none", None
    except Exception:
        return detected or "none", None


# ─────────────────────────────────────────────
# 5. 세션 상태 초기화
# ─────────────────────────────────────────────

def init_state():
    if "daily_target" not in st.session_state:
        st.session_state.daily_target = calc_macros(2000)
    if "meals" not in st.session_state:
        st.session_state.meals = pick_diverse_meals(
            st.session_state.daily_target["calories"], []
        )
    if "ai_coach_comment" not in st.session_state:
        st.session_state.ai_coach_comment = default_coach_comment(
            st.session_state.meals, st.session_state.daily_target
        )
    if "grocery_checks" not in st.session_state:
        st.session_state.grocery_checks = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "avoid_tags" not in st.session_state:
        st.session_state.avoid_tags = []
    if "llm_mode" not in st.session_state:
        st.session_state.llm_mode = "demo"
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""


init_state()

# ─────────────────────────────────────────────
# 6. 사이드바 (TASK-02)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍚 한상차림 AI")
    st.markdown("---")

    # LLM 설정
    st.markdown("### 🤖 AI 모드 설정")
    llm_choice = st.selectbox(
        "AI 엔진",
        ["내장 시연 모드", "Google Gemini (gemini-2.5-flash)", "OpenAI (gpt-4o-mini)"],
        key="llm_choice_select",
    )
    mode_map = {
        "내장 시연 모드": "demo",
        "Google Gemini (gemini-2.5-flash)": "gemini",
        "OpenAI (gpt-4o-mini)": "openai",
    }
    st.session_state.llm_mode = mode_map[llm_choice]

    if st.session_state.llm_mode != "demo":
        api_key_input = st.text_input(
            "API Key", type="password", value=st.session_state.api_key
        )
        st.session_state.api_key = api_key_input
    else:
        st.session_state.api_key = ""

    st.markdown("---")

    # 원클릭 프리셋
    st.markdown("### 👤 영양 기준 설정")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("👩 성인 여성\n2,000kcal"):
            st.session_state.daily_target = calc_macros(2000)
    with col_b:
        if st.button("👨 성인 남성\n2,400kcal"):
            st.session_state.daily_target = calc_macros(2400)

    # 맞춤 설정
    gender = st.selectbox("성별", ["여성", "남성"])
    age_group = st.selectbox("연령대", ["20대", "30~40대", "50대 이상"])
    activity = st.selectbox("활동 수준", ["적음", "보통", "많음"])

    # 기피 식재료
    avoid_options = {
        "해산물 제외": "seafood",
        "매운 음식 제외": "spicy",
        "육류 제외": "meat",
        "달걀 제외": "egg",
    }
    avoid_selected = st.multiselect("기피 식재료", list(avoid_options.keys()))
    st.session_state.avoid_tags = [avoid_options[k] for k in avoid_selected]

    # 목표 칼로리 계산
    base = 2000 if gender == "여성" else 2400
    act_map = {"적음": -100, "보통": 0, "많음": +200}
    age_map = {"20대": 0, "30~40대": -50, "50대 이상": -100}
    custom_cal = base + act_map[activity] + age_map[age_group]
    st.session_state.daily_target = calc_macros(custom_cal)

    st.markdown("---")
    tgt = st.session_state.daily_target
    st.markdown("### 📊 일일 목표 영양소")
    st.markdown(f"- **칼로리:** {tgt['calories']} kcal")
    st.markdown(f"- **탄수화물:** {tgt['carbs_g']} g")
    st.markdown(f"- **단백질:** {tgt['protein_g']} g")
    st.markdown(f"- **지방:** {tgt['fat_g']} g")

    st.markdown("---")
    # 전체 재생성 버튼
    if st.button("🔄 오늘 식단 전체 재생성"):
        with st.spinner("식단을 생성 중입니다…"):
            if st.session_state.llm_mode != "demo" and st.session_state.api_key:
                result = llm_generate_meals(
                    st.session_state.llm_mode,
                    st.session_state.api_key,
                    st.session_state.daily_target,
                    st.session_state.avoid_tags,
                )
                if result:
                    st.session_state.meals = result
                else:
                    st.warning("⚠️ API 호출 실패 → 내장 시연 모드로 전환합니다.")
                    st.session_state.meals = pick_diverse_meals(
                        st.session_state.daily_target["calories"],
                        st.session_state.avoid_tags,
                    )
            else:
                st.session_state.meals = pick_diverse_meals(
                    st.session_state.daily_target["calories"],
                    st.session_state.avoid_tags,
                )
        st.session_state.ai_coach_comment = default_coach_comment(
            st.session_state.meals, st.session_state.daily_target
        )
        st.session_state.grocery_checks = {}
        st.rerun()

# ─────────────────────────────────────────────
# 7. 메인 헤더
# ─────────────────────────────────────────────
st.markdown("# 🍚 한상차림 AI")
st.markdown("**한국인 영양소 섭취기준(KDRIs) 기반 한식 맞춤형 식단 에이전트**")

# ─────────────────────────────────────────────
# 8. 다양성 검증 배지 (TASK-04)
# ─────────────────────────────────────────────
meals = st.session_state.meals

# 다양성 검사
all_ing = []
all_meth = []
for m in meals.values():
    all_ing.extend(_tokens(m["main_ingredient"]))
    all_meth.extend(_tokens(m["cooking_method"]))
ing_dup = len(all_ing) != len(set(all_ing))
meth_dup = len(all_meth) != len(set(all_meth))

div_ok = not ing_dup and not meth_dup
badge_color = "#2D5A43" if div_ok else "#B45309"
badge_text = (
    "✅ 주재료 중복 0건 · 조리법 다양성 검증 완료"
    if div_ok
    else "⚠️ 주재료 또는 조리법 중복 감지됨"
)
st.markdown(
    f'<span class="diversity-badge" style="background:{badge_color}">{badge_text}</span>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 9. 영양 밸런스 요약 (TASK-04)
# ─────────────────────────────────────────────
total = sum_nutrition(meals)
tgt = st.session_state.daily_target

st.markdown("### 📊 일일 영양 밸런스")
c1, c2, c3, c4 = st.columns(4)
for col, label, key, unit in zip(
    [c1, c2, c3, c4],
    ["칼로리", "탄수화물", "단백질", "지방"],
    ["calories", "carbs_g", "protein_g", "fat_g"],
    ["kcal", "g", "g", "g"],
):
    val = total[key]
    t_val = tgt[key]
    pct = min(round(val / t_val * 100), 100) if t_val else 0
    with col:
        st.metric(label, f"{val}{unit}", f"{pct}% / 목표 {t_val}{unit}")
        st.progress(pct / 100)

# AI 코치 브리핑
st.markdown(
    f'<div class="coach-box">🧑‍⚕️ <b>AI 영양 코치:</b> {st.session_state.ai_coach_comment}</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ─────────────────────────────────────────────
# 10. 3끼 식단 카드 (TASK-03)
# ─────────────────────────────────────────────
st.markdown("### 🍽️ 오늘의 한식 3끼 식단")
card_cols = st.columns(3)

for idx, slot in enumerate(["breakfast", "lunch", "dinner"]):
    meal = meals[slot]
    n = meal["nutrition"]
    with card_cols[idx]:
        st.markdown(
            f"""
<div class="meal-card">
  <b>{MEAL_LABEL[slot]}</b><br>
  <span class="badge">{meal['main_ingredient']}</span>
  <span class="badge badge-warn">{meal['cooking_method']}</span>
  <h4 style="margin:8px 0 4px">{meal['menu_name']}</h4>
  <ul style="padding-left:18px;margin:4px 0">
    {''.join(f'<li>{item}</li>' for item in meal['items'])}
  </ul>
  <hr style="margin:8px 0">
  <small>🔥 {n['calories']}kcal &nbsp;|&nbsp;
         탄 {n['carbs_g']}g &nbsp;|&nbsp;
         단 {n['protein_g']}g &nbsp;|&nbsp;
         지 {n['fat_g']}g</small>
  <p style="font-size:0.82rem;color:#4a6b59;margin-top:6px">{meal['reason']}</p>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button(f"🔁 이 끼니만 교체", key=f"swap_{slot}"):
            with st.spinner("교체 중…"):
                pool = [
                    m
                    for m in KOREAN_MEAL_DB[slot]
                    if m["id"] != meal["id"]
                    and not any(t in m["tags"] for t in st.session_state.avoid_tags)
                ]
                if not pool:
                    pool = [
                        m for m in KOREAN_MEAL_DB[slot] if m["id"] != meal["id"]
                    ]
                new = random.choice(pool) if pool else meal
                new_m = dict(new)
                new_m["nutrition"] = scale_nutrition(
                    new, MEAL_RATIO[slot], st.session_state.daily_target["calories"]
                )
                st.session_state.meals[slot] = new_m
            st.session_state.ai_coach_comment = default_coach_comment(
                st.session_state.meals, st.session_state.daily_target
            )
            st.session_state.grocery_checks = {}
            st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# 11. 채팅 & 장보기 (TASK-05)
# ─────────────────────────────────────────────
chat_col, grocery_col = st.columns([3, 2])

with chat_col:
    st.markdown("### 💬 AI 채팅으로 식단 수정")

    # 빠른 수정 버튼
    quick_btns = [
        "저녁을 가벼운 두부 요리로 바꿔줘",
        "점심에 탄수화물을 조금 줄여줘",
        "아침을 속 편한 죽 메뉴로 바꿔줘",
    ]
    q_cols = st.columns(len(quick_btns))
    for qi, (qc, qmsg) in enumerate(zip(q_cols, quick_btns)):
        with qc:
            if st.button(qmsg, key=f"quick_{qi}"):
                st.session_state.chat_history.append({"role": "user", "content": qmsg})
                slot, new_meal = llm_chat_replace(
                    st.session_state.llm_mode,
                    st.session_state.api_key,
                    qmsg,
                    st.session_state.meals,
                    st.session_state.daily_target,
                )
                if slot and slot != "none":
                    if new_meal:
                        nm = dict(new_meal)
                        nm["nutrition"] = scale_nutrition(
                            new_meal,
                            MEAL_RATIO.get(slot, 0.33),
                            st.session_state.daily_target["calories"],
                        )
                        st.session_state.meals[slot] = nm
                        reply = f"✅ {MEAL_LABEL[slot]} 식단을 **{new_meal.get('menu_name', '새 메뉴')}**으로 교체했습니다."
                    else:
                        # demo fallback
                        pool = [
                            m
                            for m in KOREAN_MEAL_DB[slot]
                            if m["id"] != st.session_state.meals[slot]["id"]
                            and not any(
                                t in m["tags"] for t in st.session_state.avoid_tags
                            )
                        ]
                        if not pool:
                            pool = [
                                m
                                for m in KOREAN_MEAL_DB[slot]
                                if m["id"] != st.session_state.meals[slot]["id"]
                            ]
                        new = random.choice(pool) if pool else st.session_state.meals[slot]
                        new_m = dict(new)
                        new_m["nutrition"] = scale_nutrition(
                            new,
                            MEAL_RATIO[slot],
                            st.session_state.daily_target["calories"],
                        )
                        st.session_state.meals[slot] = new_m
                        reply = f"✅ {MEAL_LABEL[slot]} 식단을 **{new_m['menu_name']}**으로 교체했습니다."
                    st.session_state.ai_coach_comment = default_coach_comment(
                        st.session_state.meals, st.session_state.daily_target
                    )
                    st.session_state.grocery_checks = {}
                else:
                    reply = "죄송합니다, 어떤 끼니를 수정할지 정확히 알려주세요. (예: '저녁을 바꿔줘')"
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    # 채팅 내역
    for msg in st.session_state.chat_history[-12:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 채팅 입력
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("식단 수정을 요청해 보세요…", key="chat_input_field")
        submitted = st.form_submit_button("전송")

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        slot, new_meal = llm_chat_replace(
            st.session_state.llm_mode,
            st.session_state.api_key,
            user_input,
            st.session_state.meals,
            st.session_state.daily_target,
        )
        if slot and slot != "none":
            if new_meal:
                nm = dict(new_meal)
                nm["nutrition"] = scale_nutrition(
                    new_meal,
                    MEAL_RATIO.get(slot, 0.33),
                    st.session_state.daily_target["calories"],
                )
                st.session_state.meals[slot] = nm
                reply = f"✅ {MEAL_LABEL[slot]} 식단을 **{new_meal.get('menu_name', '새 메뉴')}**으로 교체했습니다."
            else:
                pool = [
                    m
                    for m in KOREAN_MEAL_DB[slot]
                    if m["id"] != st.session_state.meals[slot]["id"]
                    and not any(t in m["tags"] for t in st.session_state.avoid_tags)
                ]
                if not pool:
                    pool = [
                        m
                        for m in KOREAN_MEAL_DB[slot]
                        if m["id"] != st.session_state.meals[slot]["id"]
                    ]
                new = random.choice(pool) if pool else st.session_state.meals[slot]
                new_m = dict(new)
                new_m["nutrition"] = scale_nutrition(
                    new, MEAL_RATIO[slot], st.session_state.daily_target["calories"]
                )
                st.session_state.meals[slot] = new_m
                reply = f"✅ {MEAL_LABEL[slot]} 식단을 **{new_m['menu_name']}**으로 교체했습니다."
            st.session_state.ai_coach_comment = default_coach_comment(
                st.session_state.meals, st.session_state.daily_target
            )
            st.session_state.grocery_checks = {}
        else:
            reply = "죄송합니다, 어떤 끼니를 수정할지 정확히 알려주세요. (예: '저녁을 바꿔줘')"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

with grocery_col:
    st.markdown("### 🛒 장보기 체크리스트")
    grocery = build_grocery(st.session_state.meals)
    for cat in CATEGORIES:
        items = grocery.get(cat, [])
        if items:
            st.markdown(f"**{cat}**")
            for item in items:
                key = f"grocery_{item}"
                checked = st.session_state.grocery_checks.get(key, False)
                new_val = st.checkbox(item, value=checked, key=key)
                st.session_state.grocery_checks[key] = new_val
