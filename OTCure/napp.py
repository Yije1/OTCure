import streamlit as st
from datetime import datetime, date
from collections import defaultdict


# 1. 성분별 일일 최대 복용량 데이터베이스 추가 (mg)
MAX_DOSE_DB = {
    "아세트아미노펜": 4000, 
    "이부프로펜": 3200,          
    "나프록센": 1250,
    "덱시부프로펜": 1200
}

# 1. 의약품 정보를 관리하는 클래스 정의
class Medication:
    """
    약품의 분류 정보(class_type)와 작용 그룹(effect_group)을 포함하는 클래스
    """
    def __init__(self, name, description, usage, ingredients, class_type, preg, age, url):
        self.name = name
        self.description = description
        self.usage = usage
        self.ingredients = ingredients
        self.class_type = class_type  # 예: "진통제", "감기약", "소화제"
        self.preg = preg # 0: 해당없음, 1: 임부 금기, 2: 임부 주의
        self.age = age # 0: 해당없음, 1: 연령주의
        self.url = url

# 2. 약품 데이터베이스
MED_DB = {
    "타이레놀500mg": Medication(
        name="타이레놀500mg",
        description="해열 및 진통 효과가 있는 약품입니다.",
        usage="만 12세 이상 소아 및 성인: 1회 1-2정 (4-6시간 간격), 1일 최대 8정",
        ingredients={
            '아세트아미노펜': 500
            },
        class_type="해열진통제",
        preg = 0,
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021082400002"
    ),
    "타이레놀콜드에스정": Medication(
        name="타이레놀콜드에스정",
        description="종합 감기약 (콧물, 코막힘, 재채기, 두통, 발열 등)",
        usage="성인 기준 1회 1정, 1일 3회 식후 30분",
        ingredients={
            '아세트아미노펜': 325, 
            '슈도에페드린염산염': 30, 
            '클로르페니라민말레산염': 2,
            '덱스트로메토르판브롬화수소산염수화물': 15
        },
        class_type="감기약",
        preg = 2, 
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021101800010"
    ),
    "타이레놀8시간이알서방정": Medication(
        name="타이레놀8시간이알서방정",
        description="해열 및 진통 작용을 하는 서방형 아세트아미노펜 제제로, 통증이 오래 지속될 때 사용됩니다.",
        usage="성인 기준 아세트아미노펜으로서 1회 650mg 복용(서방정 1정 기준)이며, 1일 최대 복용량을 초과하지 않도록 주의하세요.",
        ingredients={'아세트아미노펜': 650},
        class_type="해열진통제", 
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2022020300026"
    ),
    "게보린정": Medication(
        name="게보린정",
        description="해열 및 진통 작용을 가진 복합 진통제입니다. 두통, 발열, 신경통, 근육통 등에 사용됩니다.",
        usage="성인 기준 1회 1정, 필요 시 4시간 이상 간격을 두고 복용. 공복을 피해 복용.",
        ingredients={
            '아세트아미노펜': 300, 
            '이소프로필안티피린': 150, 
            '카페인무수물': 50
        },  
        class_type="해열진통제",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A1270A0060"
    ),
    "챔프시럽": Medication(
        name = "챔프시럽",
        description = "어린이용 해열진통제. 감기나 발열, 통증 시 해열 목적으로 사용됩니다.",
        usage = "체중 1kg당 10~15mg 기준으로 4~6시간 간격 복용 (1일 5회 이하)",
        ingredients = {
            "아세트아미노펜": 160  # per 5mL
        },
        class_type = "해열진통제",
        preg = 0,
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2012091000002"
    ),
    "콜대원콜드큐시럽": Medication(
        name="콜대원콜드큐시럽",
        description="감기의 제증상(콧물, 코막힘, 재채기, 인후통, 기침, 가래, 오한, 발열, 두통, 관절통, 근육통) 완화를 위한 종합감기약 시럽제입니다.",
        usage="성인 및 만 15세 이상: 1회 1포(20 mL), 1일 3회 식후 30분 복용. 복용간격은 최소 4시간 이상.",
        ingredients={
            '아세트아미노펜': 325,     # mg per 1포20mL 
            '카페인무수물': 25,      
            '덱스트로메토르판브롬화수소산염수화물': 16, 
            'DL‑메틸에페드린염산염': 21, 
            '구아이페네신': 83,      
            '클로르페니라민말레산염': 2.5
        },
        class_type="감기약",
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021070200002"
    ),
    "콜대원노즈큐에스시럽": Medication(
        name="콜대원 노즈큐에스시럽",
        description="콧물, 코막힘, 재채기 등의 증상을 중심으로 한 코감기 증상 완화를 위한 일반의약품 시럽제입니다.",
        usage="1회 1포 1일 3회 식후 복용",
        ingredients={
            '아세트아미노펜': 325,   
            '카페인무수물': 25,   
            '클로르페니라민말레산염': 2.5,
            '구아이페네신': 42,
            '슈도에페드린염산염': 30
        },  
        class_type="감기약",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2023101900005"
    ),
    "콜대원코프큐시럽": Medication(
        name = "콜대원코프큐시럽",
        description = "기침, 가래, 발열, 두통 등 감기 증상을 완화하는 종합 감기약입니다.",
        usage = "성인 기준 1회 20mL, 1일 3회 식후 복용",
        ingredients = {
            "아세트아미노펜": 325,
            "덱스트로메토르판브롬화수소산염": 16,
            "DL-메틸에페드린염산염": 21,
            "구아이페네신": 83,
            "카페인무수물": 25
        },
        class_type = "감기약",
        preg = 0,
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021061700005"
    ),
    "판콜에스내복액": Medication(
        name="판콜에스내복액",
        description="감기로 인한 여러 증상(콧물, 코막힘, 재채기, 기침, 가래, 두통, 발열 등)을 완화하는 종합감기약입니다.",
        usage="성인 기준 1회 30mL(1병), 1일 3회 식후 복용",
        ingredients={
            '아세트아미노펜': 300,
            'DL‑메틸에페드린염산염': 17.5,
            '클로르페니라민말레산염': 2.5,
            '카페인무수물': 30,
            '구아이페네신': 83.3
        },
        class_type="감기약",
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0570A0353"
    ),
    "판피린큐액": Medication(
        name="판피린큐액",
        description="감기의 여러 증상(콧물, 코막힘, 재채기, 인후통, 기침, 가래, 오한, 발열, 관절통, 두통, 근육통)을 완화하는 종합감기약입니다.",
        usage="성인 1회 20mL, 1일 3회 식후 30분 복용.",
        ingredients={
            '아세트아미노펜': 300,   
            'DL-메틸에페드린염산염': 18,  
            '구아이페네신': 42,  
            '티페피딘시트르산염': 10,  
            '카페인무수물': 30,  
            '클로르페니라민말레산염': 2.5  
        },
        class_type="감기약",
        preg = 0, # 임부 주의
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11AKP08F0397"
    ),
    "모드콜에스연질캡슐": Medication(
        name="모드콜에스연질캡슐",
        description="감기의 여러 증상(콧물, 코막힘, 기침, 가래, 발열, 두통, 근육통 등)을 완화하는 복합감기약입니다.",
        usage="성인 및 만 15세 이상: 1회 2캡슐, 1일 3회 식후 30분 복용. 만 8세 이상~만 15세 미만: 1회 1캡슐, 1일 3회 식후 30분 복용.",
        ingredients={
            '아세트아미노펜': 200,  
            '클로르페니라민말레산염': 1.25, 
            '덱스트로메토르판브롬화수소산염': 8, 
            'DL-메틸에페드린염산염': 12.5,  
            '구아이페네신': 41.6, 
            '슈도에페드린염산염': 15 
        },
        class_type="감기약",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2012050900002"
    ),
    "부루펜정200mg": Medication(
        name="부루펜정200mg",
        description="해열, 진통 및 소염 작용을 하는 비스테로이드성 소염진통제입니다.",
        usage="성인 기준 1회 1-2정 (200-400mg), 1일 3-4회",
        ingredients={
            '이부프로펜': 200
        },
        class_type="소염진통제",
        preg = 2,
        age = 1, 
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0500A0097"
    ),
    "탁센연질캡슐": Medication(
        name="탁센연질캡슐",
        description="진통·소염 작용을 하는 일반의약품으로, 두통·근육통·생리통 등 통증 완화에 사용됩니다.",
        usage="성인 기준 1회 1정, 필요 시 1일 여러 회 복용 가능하나 복용간격 등은 약사 상담 필수.",
        ingredients={
            '나프록센': 250
            },  
        class_type="소염진통제",
        preg = 2, 
        age = 1,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=4mmn5udgx7cjw"
    ),
    "탁센레이디연질캡슐": Medication(
        name="탁센레이디연질캡슐",
        description="생리통을 포함한 각종 통증 및 발열, 붓기, 속쓰림 증상을 완화하도록 고안된 일반의약품 소염진통제 복합제입니다.",
        usage="만 15세 이상 및 성인: 1일 1~3회, 1회 1~2캡슐. 단, 공복 복용을 피해야 함.",
        ingredients={
            '이부프로펜': 200,
            '파마브롬': 25, 
            '산화마그네슘': 83 
        },
        class_type="소염진통제",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2021110500006"
    ),
    "이지엔6프로연질캡슐": Medication(
        name="이지엔6프로연질캡슐",
        description="통증 및 염증, 발열을 수반하는 여러 질환(감염, 관절염 등)에 사용되는 진통·소염제입니다.",
        usage="성인 기준 1회 300mg(덱시부프로펜 기준), 1일 2~4회 복용. 단, 1일 1,200mg을 초과하지 않아야 합니다.",
        ingredients={'덱시부프로펜': 300}, 
        class_type="소염진통제",
        preg = 2,
        age = 1,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11AOOOOO7737"
    ),
    "이지엔6이브연질캡슐": Medication(
        name="이지엔6이브연질캡슐",
        description="생리통·두통·치통·근육통 등에 사용되는 진통제입니다.",
        usage="성인 및 만 15세 이상: 1회 1-2캡슐, 1일 1-3회 복용. 복용간격은 최소 4시간 이상. 공복을 피해서 복용.",
        ingredients={
            '이부프로펜': 200,
            '파마브롬': 25
        },
        class_type="소염진통제",
        preg = 2,
        age = 1,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2013011800015"
    ),
    "지르텍정": Medication(
        name="지르텍정",
        description="알레르기성 비염, 피부염 등 알레르기 증상 완화에 사용됩니다.",
        usage="성인 기준 1일 1회 1정(10mg) 취침 전 복용",
        ingredients={
            '세티리진염산염': 10
        },
        class_type="항히스타민제",
        preg = 0, 
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11ABBBBB2527"
    ),
    "코메키나캡슐": Medication(
        name="코메키나캡슐",
        description="비염(코감기 포함), 부비강염 등에 의한 코막힘·콧물·재채기 등의 증상을 완화하는 복합 비염치료제입니다.",
        usage="성인(15세 이상) 기준 1회 1캡슐, 1일 3회 식후 복용. 복용간격은 최소 4시간 이상.",
        ingredients={
            '벨라돈나총알칼로이드': 0.13, 
            '슈도에페드린염산염': 25, 
            '카페인무수물': 50,  
            '메퀴타진': 1.33,  
            '글리시리진산이칼륨': 20  
        },
        class_type="항히스타민제",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2017072700010"
    ),
    "펙소페나딘정": Medication(
        name="펙소페나딘정",
        description="알레르기성 비염 또는 만성 특발 두드러기의 증상을 완화하는 항히스타민제입니다.",
        usage="성인 및 12세 이상: 1일 1회 1정(180 mg 기준) 또는 제품 라벨 참조.",
        ingredients={
            "펙소페나딘염산염": 180
        },
        class_type="항히스타민제",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11AOOOOO7731"
    ),
    "클라리틴정": Medication(
        name="클라리틴정",
        description="알레르기성 비염 및 만성 원인불명의 두드러기 증상을 완화하는 항히스타민제입니다.",
        usage="성인 기준 1일 1정 식사와 관계없이 복용.",
        ingredients={"로라타딘": 10},
        class_type="항히스타민제",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2009091800015"
    ),
    "훼스탈플러스정": Medication(
        name="훼스탈플러스정",
        description="소화 불량 증상(과식, 체함)을 완화하는 소화제입니다.",
        usage="성인 기준 1회 1정, 1일 3회 식후 복용",
        ingredients={
            '판크레아틴': 315, 
            '셀룰라제': 10, 
            '우르소데옥시콜산': 10, 
            '시메티콘': 30
        },
        class_type="소화제",
        preg = 0,
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0740B0009"
    ),
    "베아제정": Medication(
        name="베아제정",
        description="소화불량, 식욕감퇴, 과식·체함, 위부팽만감 등을 완화하는 소화촉진제입니다.",
        usage="성인 기준 1회 1정, 1일 3회 식후 복용. ",
        ingredients={
            "디아스타제·프로테아제·셀룰라제": 50,
            "판셀라제": 30,
            "판프로신": 20,
            "우르소데옥시콜산": 10,
            "리파제": 15,
            "판크레아틴장용과립": 78.6,
            "시메티콘": 40
        },
        class_type="소화제",
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0430A0267"
    ),
    "돌코락스에스장용정": Medication(
        name="돌코락스‑에스장용정",
        description="간헐성 변비 증상의 완화를 위한 자극성 완하제입니다. 밤사이 배변을 유도하는 작용이 있습니다.",
        usage="성인 및 만 15세 이상은 1회 1-2정 적절한 물과 함께 복용. 씹지 않고 삼킵니다.",
        ingredients={
            '비사코딜': 5,  
            '도큐세이트나트륨': 16.75  
        },
        class_type="완하제",
        preg = 2,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2009092300055"
    ),
    "메이킨큐장용정": Medication(
        name = "메이킨큐장용정",
        description = "장운동을 촉진하고 배변을 유도하는 변비 치료제입니다.",
        usage = "성인 기준 1회 1~3정(취침 전 복용)",
        ingredients = {
            "비사코딜": 5,
            "도큐세이트나트륨": 14,
            "카산트라놀": 14,
            "우르소데옥시콜산": 6
        },
        class_type = "완하제",
        preg = 2,
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2014103100002"
    ),
    "멜리안정": Medication(
        name="멜리안정",
        description="여성용 피임약으로, 저용량 에스트로겐 및 3세대 프로게스틴을 포함한 경구피임제입니다.",
        usage="성인 여성 기준 1일 1정씩 일정시간에 복용. (21일 복용 후 7일 휴약)",
        ingredients={
            '에티닐에스트라디올': 0.02, 
            '게스토덴': 0.075      
        },
        class_type="피임약",
        preg = 1,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11AKP08G3641"
    ),
    "머시론정": Medication(
        name="머시론정",
        description="저용량 복합 경구피임약으로 임신 예방을 위해 사용됩니다.",
        usage="성인 여성 기준: 1일 1정씩 21일간 복용하고, 이어서 7일간 휴약. 동일 시간대 복용 권장.",
        ingredients={
            "데소게스트렐": 0.15, 
            "에티닐에스트라디올": 0.02
        },
        class_type="피임약",
        preg = 1,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11ABBBBB2499"
    ),
    "트리싹200mg": Medication(
        name="트리싹200mg",
        description="기능성 소화불량, 과민성대장증후군, 위십이지장염 및 식도역류증상 등 위장관 운동조절제로 사용됩니다.",
        usage="성인 및 만 15세 이상: 1회 200mg, 1일 3회 식전에 복용. 증상 및 연령에 따라 적절히 증감. ",
        ingredients={
            '트리메부틴말레산염': 200
        }, 
        class_type="위장관치료제",
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2019102800004"
    ),
    "겔포스엘현탁액": Medication(
        name = "겔포스엘현탁액",
        description = "위산과다, 속쓰림, 위통, 더부룩함을 완화하는 제산제입니다.",
        usage = "성인 기준 1회 1포(20mL), 1일 1~3회 식간 복용",
        ingredients = {
            "인산알루미늄겔": 2500,
            "수산화마그네슘": 20,
            "시메티콘": 45,
            "DL-카르니틴염산염":150
        },
        class_type = "제산제",
        preg = 0,
        age = 0,
        url = "https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2017122900020"
    ),
    
    "알마겔정": Medication(
        name="알마겔정",
        description="위산과다 및 속쓰림 등 위장관 산 관련 증상을 완화하는 제산제입니다.",
        usage="1회 알마게이트로서 1g을 1일 3최 식후 씹어서 복용",
        ingredients={"알마게이트" : 500},
        class_type="제산제",
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0450A0398"
    ),
    
    "부스코판당의정": Medication(
        name="부스코판당의정",
        description="위를 포함한 위·장 평활근의 경련을 완화하고 담도·요로·월경곤란 등에 사용되는 진경제입니다.",
        usage="성인 기준 부틸스코폴라민브롬화물로서 1회 10–20 mg, 1일 3–5회 복용.",
        ingredients={"부틸스코폴라민브롬화물": 10},
        class_type="진경제",
        preg = 0,
        age = 0,
        url="https://www.health.kr/searchDrug/result_drug.asp?drug_cd=A11A0760A0001"
    ),
    
}

# --- DB 데이터 전처리: 모든 고유 성분 목록 추출 ---
ALL_INGREDIENTS = set()
for med in MED_DB.values():
    ALL_INGREDIENTS.update(med.ingredients.keys())
SORTED_INGREDIENTS = sorted(list(ALL_INGREDIENTS))
# -------------------------------------------------------------


WARNING_RULES = {
    "ClassType_Overlap_General": {
        "type": "class_type_count", # 새로운 타입 정의
        "min_count": 2, # 2개 이상 겹칠 때 경고
        # message는 함수 내에서 동적으로 생성됩니다.
        "level": "warning"
    },
    #  항히스타민제 섭취 경고 (class_type 기준)
    "Multiple_Antihistamine": {
        "type": "class_type_overlap", # 새로운 타입 정의
        "class_types": ["항히스타민제"], 
        "message": "🚨 항히스타민제 계열 약물은 졸음 위험이 높습니다. 운전 등 위험한 작업을 피하세요.",
        "level": "error"
    }
}


def check_custom_warnings(selected_med_names, med_db):
    selected_meds = [med_db[name] for name in selected_med_names if name in med_db]
    
    # 1. 성분 중복 확인을 위한 딕셔너리 생성
    ingredient_counts = defaultdict(int)
    # [추가] 2. 약물 분류 중복 확인을 위한 딕셔너리 생성
    class_type_counts = defaultdict(int)
    
    for med in selected_meds:
        # 성분 카운트
        for ing in med.ingredients.keys():
            ingredient_counts[ing] += 1
        
        # 약물 분류 카운트
        class_type_counts[med.class_type] += 1 # 이 부분이 핵심입니다.
            
    # 3. class_type 중복 확인을 위한 집합 생성
    selected_class_types = set(med.class_type for med in selected_meds)

    for rule_name, rule in WARNING_RULES.items():
        is_triggered = False
        dynamic_message = rule['message'] if 'message' in rule else "" # 동적 메시지 추가를 위해 초기화
        
        # ... (중략: drug_name_set, ingredient 확인 로직) ...
        
        # --- 4. 일반적인 약물 분류 중복 횟수 확인 (ClassType_Overlap_General)
        if rule['type'] == 'class_type_count':
            # 모든 분류를 순회하며 2개 이상 겹치는 분류가 있는지 확인
            for c_type, count in class_type_counts.items():
                if count >= rule['min_count']:
                    is_triggered = True
                    # 동적 메시지 생성
                    dynamic_message = f"⚠️ **{c_type} 분류**의 약물을 **{count}개** 중복 섭취하고 있습니다. 성분 중복 여부를 확인하세요."
                    break # 경고가 발생하면 더 이상 다른 분류를 확인할 필요가 없습니다.

        # --- 5. 특정 클래스 타입 중복 확인 (Multiple_Antihistamine)
        elif rule['type'] == 'class_type_overlap':
            if len(selected_class_types.intersection(rule['class_types'])) >= 1: 
                is_triggered = True

        # 경고 메시지 출력
        if is_triggered:
            # 동적 메시지가 있으면 그것을 사용, 없으면 규칙에 정의된 메시지를 사용
            if rule['level'] == 'error':
                st.error(dynamic_message or rule['message'])
            elif rule['level'] == 'warning':
                st.warning(dynamic_message or rule['message'])

# --- 복용 기록 저장 콜백 함수 (생략) ---
def on_log_save(selected_names, log_time_key, log_desc_key):
    """
    st.button의 on_click 콜백으로 실행됩니다.
    선택된 약품을 기록하고 일일 최대 복용량을 검사하며, 성공 시 체크박스를 초기화합니다.
    """
    
    # 1. Streamlit Session State에서 값 불러오기
    log_time_val = st.session_state[log_time_key]
    log_desc_val = st.session_state[log_desc_key]
    
    new_entry = {
        "time": log_time_val.strftime("%H:%M"),
        "description": log_desc_val if log_desc_val else "기록 없음",
        "medications": [MED_DB[name] for name in selected_names],
        "date": date.today().strftime("%Y-%m-%d")
    }
    
    # 2. 일일 누적 복용량 계산 (오늘 기록 + 새로운 기록)
    daily_cumulative_ingredients = defaultdict(float)
    
    temp_log = st.session_state['medication_log'] + [new_entry]
    
    for log in temp_log:
        if log["date"] == date.today().strftime("%Y-%m-%d"):
            for med in log["medications"]:
                for ing, amount in med.ingredients.items():
                    daily_cumulative_ingredients[ing] += amount

    # 3. 최대 복용량 초과 검사
    dose_warning_triggered = False
    
    for ing, total_amount in daily_cumulative_ingredients.items():
        max_dose = MAX_DOSE_DB.get(ing)
        
        if max_dose and total_amount > max_dose:
            dose_warning_triggered = True
            break # 하나라도 초과하면 저장하지 않음

    # 4. 결과 저장 및 체크박스 초기화
    if not dose_warning_triggered:
        st.session_state['medication_log'].append(new_entry)
        
        for key in MED_DB.keys():
            cb_key = f"cb_{key}"
            if cb_key in st.session_state:
                st.session_state[cb_key] = False
        
        st.session_state['log_status'] = "success"
    else:
        st.session_state['log_status'] = "failure"
        st.session_state['failed_ingredients'] = daily_cumulative_ingredients


# --- 세션 상태 초기화  ---
if 'profile_complete' not in st.session_state:
    st.session_state['profile_complete'] = False
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {}
if 'medication_log' not in st.session_state:
    st.session_state['medication_log'] = []
if 'exclude_multiselect' not in st.session_state:
    st.session_state['exclude_multiselect'] = []
if 'log_status' not in st.session_state:
    st.session_state['log_status'] = None
if 'failed_ingredients' not in st.session_state:
    st.session_state['failed_ingredients'] = None


st.set_page_config(page_title="OTCure", page_icon="💊")

# 2. 프로필 입력 로직
if not st.session_state['profile_complete']:
    
    st.title("👤 프로필 입력")
    st.markdown("사용자 정보를 입력해 주세요.")

    user_name = st.text_input("이름", key='input_name')
    
    col_age, col_gender = st.columns(2)
    with col_age:
        user_age = st.number_input("나이", min_value=1, max_value=120, value=30, step=1, key='input_age')
    with col_gender:
        user_gender = st.selectbox("성별", ["선택 안 함", "남성", "여성"], key='input_gender')
    
    user_pregnant = "해당 없음"
    if st.session_state.get('input_gender') == "여성":
        st.markdown("---") 
        st.subheader("추가 정보")
        user_pregnant = st.selectbox(
            "임신 여부", 
            ["해당 없음", "임신 중"], 
            key='input_pregnant'
        )

    with st.form(key='profile_form'):
        st.write("⬆️ 위 정보를 확인하고 저장합니다.")
        submit_button = st.form_submit_button(label='프로필 저장 및 시작')

    if submit_button:
        final_gender = st.session_state.get('input_gender', '선택 안 함')
        final_pregnant = st.session_state.get('input_pregnant', '해당 없음')
        final_age = st.session_state.get('input_age', 0)   
        if not st.session_state.get('input_name'):
            st.error("이름을 입력해주세요.")
        elif final_gender == "선택 안 함":
             st.error("성별을 선택해주세요.")
        else:
            ageornot = "고령자" if final_age >= 60 else "일반" 
            
            st.session_state['user_profile'] = {
                'name': st.session_state.get('input_name'),
                'age': st.session_state.get('input_age'),
                'gender': final_gender,
                'pregnant': final_pregnant,
                'ageornot': ageornot
            }
            st.session_state['profile_complete'] = True
            st.success("프로필이 저장되었습니다. 잠시 후 앱을 시작합니다.")
            
            st.rerun()
            
    st.stop()


# --- 메인 앱 시작 ---
st.title("💊 OTCure")
st.write("복용하려는 약품을 선택하면, 성분별 총 섭취량과 약품별 상세 정보를 확인합니다.")


profile = st.session_state['user_profile']
st.sidebar.info(
    f"**{profile['name']}**님 프로필:\n"
    f"나이: {profile['age']}세, 성별: {profile['gender']}\n"
    f"임신여부: {profile['pregnant']}"
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
                        
                ing_list = [f"-  {ing} : {amount} mg" for ing, amount in total_ing.items()]
                st.markdown("\n".join(ing_list))
                
                st.caption("복용 약품:")
                med_list = [med.name for med in entry["medications"]]
                st.markdown("- " + "\n- ".join(med_list))
else:
    st.sidebar.caption("오늘 기록된 복용 기록이 없습니다.")


# --- 오늘 하루 섭취 성분 총합 리스트 출력 ---
# 1. 일일 누적 성분량 계산
daily_total_ingredients = defaultdict(float)
today_date = date.today().strftime("%Y-%m-%d")

for log in st.session_state['medication_log']:
    if log["date"] == today_date:
        for med in log["medications"]:
            for ing, amount in med.ingredients.items():
                daily_total_ingredients[ing] += amount

# 2. 사이드바에 출력
st.sidebar.markdown("---")
st.sidebar.subheader("🧪 오늘 하루 섭취 성분 총합")

if daily_total_ingredients:
    # 성분명을 기준으로 정렬하여 출력
    sorted_ingredients = sorted(daily_total_ingredients.keys())
    
    for ing in sorted_ingredients:
        total_amount = daily_total_ingredients[ing]
        max_dose = MAX_DOSE_DB.get(ing)
        
        display_text = f"- **{ing}**: {total_amount:.1f} mg"
        
        if max_dose:
            if total_amount > max_dose:
                # 최대 복용량 초과 시 경고 표시
                display_text += f" (🚨 최대 권장량 {max_dose}mg 초과!)"
            else:
                display_text += f" (최대 {max_dose}mg)"
        
        st.sidebar.markdown(display_text)
else:
    st.sidebar.caption("오늘 섭취한 성분 기록이 없습니다.")

# --- 끝 ---

# --- [Feature 1 & 3] 탭 UI 생성 ---
tab_selection, tab_ingredient_info, tab_ingredient_exclude = st.tabs([
    "💊 약품 복용 기록", 
    "🧪 성분 정보", 
    "🚫 제외할 성분"
])

# --- [Feature 1] "성분 정보 보기" 탭 ---
with tab_ingredient_info:
    st.subheader("🧪 DB 내 전체 성분 정보")
    st.write("데이터베이스에 등록된 모든 성분과 해당 성분을 포함하는 약품 목록입니다.")
    
    for ing in SORTED_INGREDIENTS:
        with st.expander(f"**{ing}**"):
            max_dose_str = "정보 없음"
            if ing in MAX_DOSE_DB:
                max_dose_str = f"{MAX_DOSE_DB[ing]} mg"
            st.markdown(f"일일 최대 복용량: {max_dose_str}")
            
            st.markdown("포함된 약품:")
            meds_with_ing = [
                med.name for med in MED_DB.values() if ing in med.ingredients
            ]
            if meds_with_ing:
                st.markdown("- " + "\n- ".join(meds_with_ing))
            else:
                st.caption("포함된 약품 정보가 없습니다.")

# --- [Feature 3] "성분으로 약품 제외" 탭 ---
with tab_ingredient_exclude:
    st.subheader("🚫 특정 성분 포함 약품 제외하기")
    st.info("여기서 성분을 선택하면 '약품 복용 기록' 탭에서 해당 성분이 포함된 약품이 자동으로 비활성화됩니다.")
    
    st.multiselect(
        "제외할 성분을 선택하세요",
        options=SORTED_INGREDIENTS,
        key='exclude_multiselect' # 세션 상태 키
    )
    st.caption(f"현재 총 {len(st.session_state['exclude_multiselect'])}개 성분이 제외 목록에 있습니다.")
    st.markdown("---")
    # st.write("성분 선택 후 '약품 선택 및 기록' 탭으로 돌아가 체크박스가 비활성화된 것을 확인하세요.")


# --- "약품 선택 및 기록" 탭 ---
with tab_selection:
    
    # 3. 약품 선택 UI (체크박스)
    st.subheader("💊 복용할 약품을 선택하세요 (1회 복용 기준):")
    selected_med_names = []

    col1, col2 = st.columns(2)
    med_names = list(MED_DB.keys())
    half_point = (len(med_names) + 1) // 2
    
    # --- [Feature 2 & 3] 비활성화를 위한 프로필 및 제외 목록 가져오기 ---
    profile = st.session_state['user_profile']
    is_pregnant = profile['pregnant'] in ["임신 중"]
    is_elderly = profile['ageornot'] == "고령자"
    excluded_ingredients = set(st.session_state['exclude_multiselect'])
    # -------------------------------------------------------------

    def render_checkboxes(med_list):
        for name in med_list:
            med = MED_DB[name]
            
            # --- [수정된 로직] 임산부/수유부 주의 및 금기 처리 ---
            is_disabled = False
            reason = "" # 비활성화 사유
            
            # 1. 임산부/수유부 체크
            if is_pregnant:
                if med.preg == 1: # 임부 금기
                    is_disabled = True
                    reason = " (임부 금기)"
                elif med.preg == 2: # 임부 금기: 선택 가능 + 안내 문구만
                    is_disabled = False
                    reason = " (임부 주의)" 
            
            # 2. 고령자 주의 (기존 로직 유지)
            if not is_disabled and is_elderly and med.age == 1:
                is_disabled = True
                reason = " (연령주의)"
            
            # 3. 제외 성분 포함 (기존 로직 유지)
            if not is_disabled and any(ing in excluded_ingredients for ing in med.ingredients):
                is_disabled = True
                reason = f" (제외 성분 포함)"
            # ---------------------------------------------------

            label = f"{name}{reason}"
            
            # disabled=is_disabled 매개변수를 사용하여 체크박스를 비활성화
            if st.checkbox(label, key=f"cb_{name}", disabled=is_disabled):
                selected_med_names.append(name)

    with col1:
        render_checkboxes(med_names[:half_point])

    with col2:
        render_checkboxes(med_names[half_point:])
    
    
    # --- [저장 후 상태 메시지 표시] ---
    if st.session_state['log_status'] == "success":
        st.success("✅ 복용 기록이 성공적으로 저장되었습니다. 사이드바에서 확인하세요.")
        st.session_state['log_status'] = None 
    elif st.session_state['log_status'] == "failure":
        st.error("⚠️ 일일 최대 복용량 초과 경고! 기록이 저장되지 않았습니다. 복용량을 확인해 주세요.")
        
        # 실패 사유 (초과 성분) 상세 표시
        for ing, total_amount in st.session_state['failed_ingredients'].items():
            max_dose = MAX_DOSE_DB.get(ing)
            if max_dose and total_amount > max_dose:
                st.markdown(f"-   {ing}   성분: 현재 복용량 **{total_amount}mg   (최대 권장량   {max_dose}mg  ) - 🚨  초과  ")
        
        st.session_state['log_status'] = None 
        st.session_state['failed_ingredients'] = None
    # ------------------------------------------------------------------------------------------
    
    
    if not selected_med_names:
        st.info("목록에서 약품을 선택해주세요.")
    else:
        # 5. 구조화된 경고 로직 호출
        check_custom_warnings(selected_med_names, MED_DB) 


        # 5. 선택된 약품 정보 처리 및 성분 분석 (생략)
        total_ingredients = defaultdict(float)
        ingredient_sources = defaultdict(list)
        meds_by_type = defaultdict(list) 

        for name in selected_med_names:
            med = MED_DB[name]
            meds_by_type[med.class_type].append(med)
            
            for ingredient, amount in med.ingredients.items():
                total_ingredients[ingredient] += amount
                ingredient_sources[ingredient].append(name)

        # 6. 일반적인 중복 성분 경고 표시
        duplicate_ingredients = {
            ing: sources for ing, sources in ingredient_sources.items() if len(sources) > 1
        }

        if duplicate_ingredients:
            st.error("🚨 중복 성분 경고: 동일한 유효 성분을 중복 섭취합니다.")
            #st.warning("과다 복용의 위험이 있으니 복용 전 반드시 전문가와 상의하세요.")
            
            duplicate_list = []
            for ing, sources in duplicate_ingredients.items():
                sources_str = ", ".join(sources)
                duplicate_list.append(f"- **{ing}** 성분: {sources_str}에 모두 포함됨")
            
            st.markdown("\n".join(duplicate_list))
        
        st.markdown("---")    
        
        
        # 7. 총 성분 섭취량 결과 표시
        st.subheader("🧪 성분별 총 섭취량 (1회분 기준)")
        if not total_ingredients:
            st.write("선택된 약품에 유효 성분 정보가 없습니다.")
        else:
            for ingredient, total_amount in total_ingredients.items():
                if ingredient in duplicate_ingredients:
                    st.markdown(f"-   {ingredient}  :   {total_amount:.1f} mg   (중복 합산됨)")
                else:
                    st.write(f"-   {ingredient}  : {total_amount:.1f} mg")
        
        st.markdown("---") 

        # 8. 상세 정보 (생략)
        sorted_types = sorted(meds_by_type.keys()) 
        cols = st.columns(2)
        col_index = 0
        
        for med_type in sorted_types:
            current_col = cols[col_index]
            
            with current_col:
                st.markdown(f"#### 🗂️ {med_type} ({len(meds_by_type[med_type])}개)")
                
                for med in meds_by_type[med_type]:
                    with st.expander(f"{med.name}의 상세 정보"):
                        #st.markdown(f"분류: {med.class_type}")
                        # st.markdown(f"**작용 그룹:** {med.effect_group}")
                        st.markdown(f"설명: {med.description}")
                        st.markdown(f"복용 방법: {med.usage}")
                        
                        ingredients_str = ", ".join([f"**{k}** {v}mg" for k, v in med.ingredients.items()])
                        st.markdown(f"주요 성분: {ingredients_str}")
                        st.link_button(
                            label=f"상세 정보",
                            url=med.url,
                            #help=f"새 탭에서 '{med.name}'에 대한 구글 검색 결과를 엽니다.",
                            type="secondary"
                        )
                st.markdown("---") 
                
            col_index = 1 - col_index 


    # 9. 복용 기록 저장 폼
        st.markdown("---")
        st.subheader("📝 복용 기록 저장하기")
        st.write(f"선택된 약품 ({len(selected_med_names)}개)의 복용 시간과 간단한 설명을 기록합니다.")
        
        with st.form(key='log_form', clear_on_submit=True):
            col_time, col_desc = st.columns([1, 2])
            
            log_time_key = 'log_time_input_key'
            log_desc_key = 'log_description_input_key'
            
            with col_time:
                now = datetime.now().time()
                st.time_input("복용 시간", value=now, key=log_time_key) 

            with col_desc:
                st.text_input( 
                    "설명 (예: 두통 심해서, 식후)",
                    key=log_desc_key
                )
            
            st.form_submit_button(
                label=f"✅ 선택된 {len(selected_med_names)}개 약품 복용 기록 저장",
                on_click=on_log_save,
                kwargs={
                    'selected_names': selected_med_names,
                    'log_time_key': log_time_key,
                    'log_desc_key': log_desc_key
                }
            )


# --- 앱 하단 (탭 외부에 공통 적용) ---
st.caption("⚠️ 중요: 본 애플리케이션의 정보는 부정확할 수 있습니다. "
           "의학적 조언을 대체할 수 없으며, 실제 의약품 복용 전에는 반드시 의사 또는 약사와 상의하세요.")

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.link_button(
        label="약학정보원\n(약품검색하기)",
        url="https://www.health.kr/",
        type="secondary",
        use_container_width=True
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