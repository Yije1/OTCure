import streamlit as st
from datetime import datetime, date
from collections import defaultdict


# 1. 성분별 일일 최대 복용량 데이터베이스 추가 (mg)
MAX_DOSE_DB = {
    "아세트아미노펜": 4000,  # mg
    "이부프로펜": 3200,      # mg
    "세티리진염산염": 10,     # mg
    "나프록센": 1250
}

# 1. 의약품 정보를 관리하는 클래스 정의
class Medication:
    """
    약물의 분류 정보(class_type)와 작용 그룹(effect_group)을 포함하는 클래스
    """
    def __init__(self, name, description, usage, ingredients, class_type, effect_group, url):
        self.name = name
        self.description = description
        self.usage = usage
        self.ingredients = ingredients
        self.class_type = class_type  # 예: "진통제", "감기약", "소화제"
        self.effect_group = effect_group # 예: "Acetaminophen", "Ibuprofen", "Antihistamine"
        self.url = url

# 2. 약물 데이터베이스
MED_DB = {
    "타이레놀 500mg": Medication(
        name="타이레놀 500mg",
        description="해열 및 진통 효과가 있는 약물입니다.",
        usage="성인 기준 1회 1-2정 (4-6시간 간격), 1일 최대 8정",
        ingredients={'아세트아미노펜': 500},
        class_type="진통제",
        effect_group="Acetaminophen",
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021082400002"
    ),
    "부루펜 정 200mg": Medication(
        name="부루펜 정 200mg",
        description="해열, 진통 및 소염 작용을 하는 비스테로이드성 소염진통제입니다.",
        usage="성인 기준 1회 1-2정 (200-400mg), 1일 3-4회",
        ingredients={'이부프로펜': 200},
        class_type="진통제/소염제",
        effect_group="Ibuprofen",
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0500A0097"
    ),
    "지르텍 정": Medication(
        name="지르텍 정",
        description="알레르기성 비염, 피부염 등 알레르기 증상 완화에 사용됩니다.",
        usage="성인 기준 1일 1회 1정(10mg) 취침 전 복용",
        ingredients={'세티리진염산염': 10},
        class_type="알레르기약",
        effect_group="Antihistamine",
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11ABBBBB2527"
    ),
    "훼스탈 플러스 정": Medication(
        name="훼스탈 플러스 정",
        description="소화 불량 증상(과식, 체함)을 완화하는 소화제입니다.",
        usage="성인 기준 1회 1-2정, 1일 3회 식후 복용",
        ingredients={'판크레아틴': 150, '셀룰라제': 50, '우르소데옥시콜산': 10},
        class_type="소화제",
        effect_group="DigestiveEnzyme",
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0740B0009"
    ),
    "타이레놀 콜드-에스 정": Medication(
        name="타이레놀 콜드-에스 정",
        description="종합 감기약 (콧물, 코막힘, 재채기, 두통, 발열 등)",
        usage="성인 기준 1회 1정, 1일 3회 식후 30분",
        ingredients={
            '아세트아미노펜': 300, 
            '슈도에페드린염산염': 30, 
            '클로르페니라민말레산염': 2
        },
        class_type="감기약",
        effect_group="Cold_Multi",
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021101800010"
    )
}

# 3. 경고 규칙 데이터 구조화
WARNING_RULES = {
    # 1. 성분 중복에 기반한 경고 (기존 로직이 더 적합하지만, 일반화 예시)
    "Acetaminophen_Overlap": {
        "type": "ingredient",
        "ingredients": ["아세트아미노펜"],
        "min_count": 2, # 최소 2개 이상의 약물이 해당 성분을 포함할 때
        "message": "🚨 **아세트아미노펜 성분을 중복**하여 섭취합니다. 간 손상 위험!",
        "level": "error"
    },
    
    # 2. 효능 그룹 간의 경고 (요청하신 기능 일반화)
    "Tylenol_Cold_Combination": {
        "type": "drug_name_set",
        "names": ["타이레놀 500mg", "타이레놀 콜드-에스 정"],
        "message": "🚨 **유사한 약을 중복**으로 섭취하게 됩니다. 두 약 모두 해열/진통 효과가 있어 권장되지 않습니다.",
        "level": "error"
    },
    
    # 3. 새로운 규칙: NSAIDs(이부프로펜)와 아스피린 조합 경고
    "NSAID_Aspirin_Conflict": {
        "type": "effect_group_set",
        "groups": ["Ibuprofen", "Aspirin"], # 약물 그룹 중 2개 이상이 선택되면
        "message": "⚠️ **NSAIDs(이부프로펜 계열)와 아스피린을 함께 복용**하면 위장 출혈 위험이 높아집니다.",
        "level": "warning"
    },
    "Multiple_Antihistamine": {
        "type": "effect_group_overlap",
        "groups": ["Antihistamine", "Cold_Multi"],
        "message": "**졸음을 유발하는 항히스타민 성분을 중복 섭취**할 위험이 있습니다. 운전 등 위험한 작업을 피하세요.",
        "level": "error"
    }
}

# --- 경고 규칙 확인 함수 (app.py에서 가져왔음) ---
def check_custom_warnings(selected_med_names, med_db):
    # 선택된 약물 객체와 그룹 정보 미리 추출
    selected_meds = [med_db[name] for name in selected_med_names if name in med_db]
    selected_groups = set(med.effect_group for med in selected_meds)
    # for med in selected_meds:
    #     selected_groups[med.effect_group] += 1

    for rule_name, rule in WARNING_RULES.items():
        is_triggered = False
        
        if rule['type'] == 'drug_name_set':
            # rule['names']의 모든 약물이 selected_med_names에 있는지 확인
            if all(name in selected_med_names for name in rule['names']):
                is_triggered = True
                
        elif rule['type'] == 'effect_group_set':
            # rule['groups']와 selected_groups 간의 교집합 크기가 2 이상인지 확인
            if len(selected_groups.intersection(rule['groups'])) >= 2:
                is_triggered = True
        # elif rule['type'] == 'effect_group_overlap':
        #     count_overlap = sum(1 for group in rule['groups'] if selected_groups[group] >= 1)
        #     if count_overlap >= 2:
        #         is_triggered = True


        # ... (다른 타입의 규칙 추가 가능)

        if is_triggered:
            # 경고 메시지 출력
            if rule['level'] == 'error':
                st.error(rule['message'])
            elif rule['level'] == 'warning':
                st.warning(rule['message'])


 # --- Streamlit 웹 애플리케이션 UI 구성 ---


# 복용 기록 저장 함수 정의
def save_medication_log(selected_names, log_time_val, log_desc_val, med_db, max_dose_db):
    """선택된 약물을 기록하고 일일 최대 복용량을 검사합니다."""
    
    new_entry = {
        "time": log_time_val.strftime("%H:%M"),
        "description": log_desc_val if log_desc_val else "기록 없음",
        "medications": [med_db[name] for name in selected_names],
        "date": date.today().strftime("%Y-%m-%d")
    }
    
    # 1. 일일 누적 복용량 계산 (오늘 기록 + 새로운 기록)
    daily_cumulative_ingredients = defaultdict(float)
    
    for log in st.session_state['medication_log'] + [new_entry]:
        if log["date"] == date.today().strftime("%Y-%m-%d"):
            for med in log["medications"]:
                for ing, amount in med.ingredients.items():
                    daily_cumulative_ingredients[ing] += amount

    # 2. 경고 확인
    dose_warning_triggered = False
    warning_messages = []
    
    # 현재 복용량 정보 출력
    st.markdown("##### 📝 이번 복용 후 **오늘의 누적 섭취량**")
    
    for ing, total_amount in daily_cumulative_ingredients.items():
        max_dose = max_dose_db.get(ing)
        
        if max_dose and total_amount > max_dose:
            warning_messages.append(
                f"**{ing}** 성분: 현재 복용량 **{total_amount}mg** (최대 권장량 **{max_dose}mg**)"
            )
            dose_warning_triggered = True
            st.markdown(f"- **{ing}**: **{total_amount:.1f}mg** (최대 {max_dose}mg) - 🚨 **초과**")
        else:
             st.markdown(f"- **{ing}**: {total_amount:.1f}mg (최대 {max_dose if max_dose else 'N/A'}mg)")


    # 3. 결과 저장 및 경고 출력
    st.markdown("---")
    if not dose_warning_triggered:
        st.session_state['medication_log'].append(new_entry)
        st.success("✅ 복용 기록이 성공적으로 저장되었습니다. 사이드바에서 확인하세요.")
        st.rerun() 
    else:
        st.error("⚠️ **일일 최대 복용량 초과 경고!** 기록이 저장되지 않았습니다. 복용량을 확인해 주세요.")
        for msg in warning_messages:
             st.markdown(f"- {msg}")


# --- 1. 세션 상태 초기화 ---
if 'profile_complete' not in st.session_state:
    st.session_state['profile_complete'] = False
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {}
###################################################
if 'medication_log' not in st.session_state:
    st.session_state['medication_log'] = []
######################################################


st.set_page_config(page_title="OTCure", page_icon="💊")

# 2. 프로필 입력 로직
if not st.session_state['profile_complete']:
    
    st.title("👤 사용자 프로필 입력")
    st.markdown("약물 상호작용 및 안전성 검토를 위해 사용자 정보를 입력해 주세요.")

    # 1. 사용자 입력 필드를 먼저 정의 (st.form 외부에 정의하여 상태 변화를 감지)
    user_name = st.text_input("이름", key='input_name')
    
    col_age, col_gender = st.columns(2)
    with col_age:
        user_age = st.number_input("나이", min_value=1, max_value=120, value=30, step=1, key='input_age')
    with col_gender:
        # 이 selectbox의 선택을 Streamlit이 즉시 감지합니다.
        user_gender = st.selectbox("성별", ["선택 안 함", "남성", "여성", "기타"], key='input_gender')
    
    # 2. 임신 여부 필드를 조건부로 표시 (st.form 외부에서 성별 상태를 확인)
    user_pregnant = "해당 없음"
    # st.session_state['input_gender']는 selectbox의 현재 값을 즉시 반영합니다.
    if st.session_state.get('input_gender') == "여성":
        st.markdown("---") # 시각적 구분
        st.subheader("추가 정보")
        user_pregnant = st.selectbox(
            "임신 여부", 
            ["해당 없음", "임신 중", "수유 중"], 
            key='input_pregnant'
        )

    # 3. Form을 사용하여 제출 버튼만 그룹화
    with st.form(key='profile_form'):
        st.write("⬆️ 위 정보를 확인하고 저장합니다.")
        submit_button = st.form_submit_button(label='프로필 저장 및 시작')

    if submit_button:
        # st.session_state에서 최신 값을 가져옵니다.
        final_gender = st.session_state.get('input_gender', '선택 안 함')
        final_pregnant = st.session_state.get('input_pregnant', '해당 없음')
        
        if not st.session_state.get('input_name'):
            st.error("이름을 입력해주세요.")
        elif final_gender == "선택 안 함":
             st.error("성별을 선택해주세요.")
        else:
            # 최종 데이터 저장
            st.session_state['user_profile'] = {
                'name': st.session_state.get('input_name'),
                'age': st.session_state.get('input_age'),
                'gender': final_gender,
                'pregnant': final_pregnant 
            }
            st.session_state['profile_complete'] = True
            st.success("프로필이 저장되었습니다. 잠시 후 앱을 시작합니다.")
            
            st.rerun()
            
    st.stop()


st.title("💊 OTCure")
st.write("복용하려는 약물을 선택하면, 성분별 총 섭취량과 약물별 상세 정보를 확인합니다.")


profile = st.session_state['user_profile']
st.sidebar.info(
    f"**{profile['name']}**님 프로필:\n"
    f"나이: {profile['age']}세, 성별: {profile['gender']}"
)

# 사이드바 복용 기록 누적 출력 
st.sidebar.markdown("---")
st.sidebar.subheader("📅 오늘의 복용 기록")

if st.session_state['medication_log']:
    for entry in reversed(st.session_state['medication_log']):
        if entry["date"] == date.today().strftime("%Y-%m-%d"):
            header_text = f"**[{entry['time']}] {entry['description']}**"
            
            with st.sidebar.expander(header_text):
                st.caption("복용 성분량:")
                total_ing = defaultdict(float)
                for med in entry["medications"]:
                    for ing, amount in med.ingredients.items():
                        total_ing[ing] += amount
                        
                ing_list = [f"- **{ing}**: {amount} mg" for ing, amount in total_ing.items()]
                st.markdown("\n".join(ing_list))
                
                st.caption("복용 약물:")
                med_list = [med.name for med in entry["medications"]]
                st.markdown("- " + "\n- ".join(med_list))
else:
    st.sidebar.caption("오늘 기록된 복용 기록이 없습니다.")



# 3. 약물 선택 UI (체크박스)
st.subheader("💊 복용할 약물을 선택하세요 (1회 복용 기준):")
selected_med_names = []

col1, col2 = st.columns(2)
med_names = list(MED_DB.keys())
half_point = (len(med_names) + 1) // 2

with col1:
    for name in med_names[:half_point]:
        if st.checkbox(name, key=f"cb_{name}"):
            selected_med_names.append(name)

with col2:
    for name in med_names[half_point:]:
        if st.checkbox(name, key=f"cb_{name}"):
            selected_med_names.append(name)

if not selected_med_names:
    st.info("목록에서 약물을 선택해주세요.")
else:
    # 5. 구조화된 경고 로직 호출 (즉시 출력)
    check_custom_warnings(selected_med_names, MED_DB) 

# 5. 선택된 약물 정보 처리 및 성분 분석
    total_ingredients = defaultdict(float)
    ingredient_sources = defaultdict(list)
    selected_med_objects = []

    # 약물 종류별로 그룹화하기 위한 딕셔너리
    meds_by_type = defaultdict(list) 

    for name in selected_med_names:
        med = MED_DB[name]
        selected_med_objects.append(med)
        
        # class_type별로 약물 그룹화
        meds_by_type[med.class_type].append(med) #?????
        
        for ingredient, amount in med.ingredients.items():
            total_ingredients[ingredient] += amount
            ingredient_sources[ingredient].append(name)

    # --- 6. 일반적인 중복 성분 경고 표시 (기존 로직) ---
    duplicate_ingredients = {
        ing: sources for ing, sources in ingredient_sources.items() if len(sources) > 1
    }

    if duplicate_ingredients:
        st.error("🚨 **중복 성분 경고: 동일한 유효 성분을 중복 섭취합니다.**")
        st.warning("과다 복용의 위험이 있으니 복용 전 반드시 전문가와 상의하세요.")
        
        duplicate_list = []
        for ing, sources in duplicate_ingredients.items():
            sources_str = ", ".join(sources)
            duplicate_list.append(f"- **{ing}** 성분: {sources_str}에 모두 포함됨")
        
        st.markdown("\n".join(duplicate_list))
    
    st.markdown("---")    
    
    
    # 7. 총 성분 섭취량 결과 표시
    st.subheader("🧪 성분별 총 섭취량 (1회분 기준)")
    if not total_ingredients:
        st.write("선택된 약물에 유효 성분 정보가 없습니다.")
    else:
        for ingredient, total_amount in total_ingredients.items():
            if ingredient in duplicate_ingredients:
                st.markdown(f"- **{ingredient}**: **{total_amount:.1f} mg** (중복 합산됨)")
            else:
                st.write(f"- **{ingredient}**: {total_amount:.1f} mg")
    
    st.markdown("---") 

    # 8. 각 약물별 상세 정보 표시
    # st.subheader("📋 선택한 약물 상세 정보")
    # for med in selected_med_objects:
    #     with st.expander(f"**{med.name}**의 상세 정보 보기"):
    #         st.markdown(f"**설명:** {med.description}")
    #         st.markdown(f"**복용 방법:** {med.usage}")
            
    #         ingredients_str = ", ".join([f"**{k}** {v}mg" for k, v in med.ingredients.items()])
    #         st.markdown(f"**주요 성분:** {ingredients_str}")

    # class_type 키를 기준으로 정렬하여 출력
    sorted_types = sorted(meds_by_type.keys()) 
    
    # 2열 그리드 구성을 위해 columns 객체를 저장할 리스트를 준비합니다.
    # st.columns(2)를 반복적으로 호출하여 열을 만듭니다.
    
    # 두 개의 열을 만듭니다.
    cols = st.columns(2)
    
    # 순환 인덱스를 사용하여 0번 열과 1번 열을 번갈아 사용합니다.
    col_index = 0
    
    for med_type in sorted_types:
        # 현재 차례의 열(col_index: 0 또는 1)을 선택합니다.
        current_col = cols[col_index]
        
        # 선택된 열(Column) 내부에 내용을 출력합니다.
        with current_col:
            st.markdown(f"#### 🗂️ {med_type} ({len(meds_by_type[med_type])}개)")
            
            for med in meds_by_type[med_type]:
                # Expander 사용
                # 격자 레이아웃에서는 Expander가 길어질 수 있으므로 st.info 또는 st.container 사용도 고려할 수 있습니다.
                with st.expander(f"**{med.name}**의 상세 정보 보기"):
                    st.markdown(f"**분류:** {med.class_type}")
                    st.markdown(f"**작용 그룹:** {med.effect_group}")
                    st.markdown(f"**설명:** {med.description}")
                    st.markdown(f"**복용 방법:** {med.usage}")
                    
                    ingredients_str = ", ".join([f"**{k}** {v}mg" for k, v in med.ingredients.items()])
                    st.markdown(f"**주요 성분:** {ingredients_str}")
                    st.link_button(
                        label=f"'{med.name}' 상세 정보 및 복용법 검색",
                        url=med.url,
                        help=f"새 탭에서 '{med.name}'에 대한 구글 검색 결과를 엽니다.",
                        type="secondary" # 버튼을 강조하여 잘 보이게 합니다.
                    )
                    
            
            # 다음 출력을 위해 열 인덱스를 전환합니다.
            # 0 -> 1, 1 -> 0
            st.markdown("---") # 각 분류 섹션 하단에 구분선을 넣어 구분을 명확히 합니다.
            
        col_index = 1 - col_index # 간단하게 0과 1을 토글합니다.


# 복용 기록 저장 폼
    st.markdown("---")
    st.subheader("📝 복용 기록 저장하기")
    st.write(f"선택된 약물 **({len(selected_med_names)}개)**의 복용 시간과 간단한 설명을 기록합니다. 저장 시 일일 최대 복용량을 검사합니다.")
    
    with st.form(key='log_form', clear_on_submit=True):
        col_time, col_desc = st.columns([1, 2])
        
        with col_time:
            now = datetime.now().time()
            log_time_input = st.time_input("복용 시간", value=now, key='log_time') 

        with col_desc:
            log_description_input = st.text_input( 
                "간단 설명 (예: 두통 심해서, 식후)",
                key='log_description'
            )
            
        log_button = st.form_submit_button(label=f"✅ 선택된 {len(selected_med_names)}개 약물 복용 기록 저장")
        
    if log_button:
        # 복용 기록 저장 함수 호출
        save_medication_log(
            selected_med_names, 
            st.session_state['log_time'], 
            st.session_state['log_description'], 
            MED_DB, 
            MAX_DOSE_DB
        )



# --- 앱 하단에 주의사항 추가 ---
st.caption("⚠️ 중요: 본 애플리케이션의 정보는 예시이며 부정확할 수 있습니다. "
           "의학적 조언을 대체할 수 없으며, 실제 의약품 복용 전에는 반드시 의사 또는 약사와 상의하세요.")



st.markdown("---")
# 1. 3개의 열(Column)을 생성합니다.
# columns 변수는 [col1, col2, col3] 리스트를 담게 됩니다.
col1, col2, col3 = st.columns(3)
with col1:
    st.link_button(
        label="약학정보원\n(약품검색하기)",
        url="https://www.health.kr/",
        type="secondary",
        use_container_width=True # 컨테이너(열)의 너비에 맞게 버튼을 늘립니다.
    )

with col2:
    st.link_button(
        label="한국의약품안전관리원",
        url="https://www.drugsafe.or.kr/ko/index.do",
        type="secondary",
        use_container_width=True
    )

with col3:
    st.link_button(
        label="대한약사회",
        url="https://www.kpanet.or.kr/",
        type="secondary",
        use_container_width=True
    )

st.markdown("---")

st.link_button(
        label="주변약국찾기",
        url="https://map.naver.com/p/search/%EC%95%BD%EA%B5%AD?c=15.00,0,0,0,dh",
        type="secondary",
        use_container_width=True
    )