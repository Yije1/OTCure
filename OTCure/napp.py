import streamlit as st
from collections import defaultdict

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

st.set_page_config(page_title="의약품 사용 관리", page_icon="💊")
st.title("💊 의약품 사용 관리")
st.write("복용하려는 약물을 선택하면, 성분별 총 섭취량과 약물별 상세 정보를 확인합니다.")

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
    # 5. 구조화된 경고 로직 호출
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