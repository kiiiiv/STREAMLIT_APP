"""
components/style.py

전역 스타일 설정
- 배경색: 흰색
- 글자색: 검정색
- 사이드바 스타일링
- 그래프/테이블 배경 흰색
"""

import streamlit as st


def apply_global_styles():
    """전역 스타일 적용"""
    st.markdown("""
    <style>
        /* ========== Streamlit 상단 헤더 제거 ========== */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        /* 상단 여백 조정 */
        .main > div:first-child {
            padding-top: 0 !important;
        }
        
        /* ========== 전체 배경 흰색, 글자 검정색 ========== */
        .stApp {
            background-color: white !important;
            color: black !important;
        }
        
        .main .block-container {
            background-color: white !important;
            color: black !important;
        }
        
        /* ========== 사이드바 배경 흰색 ========== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffe4cc 0%, #fff4e6 25%, #fffacd 50%, #f0fff0 75%, #e8f5e9 100%) !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
            padding-bottom: 100px; /* footer 공간 확보 */
        }
        
        /* ========== 사이드바 메뉴 항목 스타일 ========== */
        /* 기본 상태 - 회색 볼드체 */
        [data-testid="stSidebarNav"] li a {
            color: #808080 !important;  /* 회색 */
            font-weight: 700 !important;  /* 볼드 */
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        /* 호버 상태 */
        [data-testid="stSidebarNav"] li a:hover {
            background-color: #f0f2f6 !important;
            color: #2596be !important;
        }
        
        /* 선택된 상태 - #2596be 배경, 흰색 볼드 */
        [data-testid="stSidebarNav"] li a[aria-current="page"] {
            background-color: #2596be !important;
            color: white !important;
            font-weight: 700 !important;
        }
        
        /* ========== 헤더/타이틀 스타일 ========== */
        h1, h2, h3, h4, h5, h6 {
            color: black !important;
        }
        
        /* ========== 텍스트 색상 ========== */
        p, span, div, label {
            color: black !important;
        }
        
        /* ========== 위젯 스타일 - 깔끔한 흰색 배경 ========== */
        /* Selectbox */
        .stSelectbox {
            background-color: white !important;
        }
        
        .stSelectbox > div > div {
            background-color: white !important;
            border: 1px solid #d0d0d0 !important;
            border-radius: 4px !important;
        }
        
        .stSelectbox label {
            color: black !important;
            font-weight: 600 !important;
        }
        
        /* MultiSelect */
        .stMultiSelect {
            background-color: white !important;
        }
        
        .stMultiSelect > div > div {
            background-color: white !important;
            border: 1px solid #d0d0d0 !important;
            border-radius: 4px !important;
        }
        
        .stMultiSelect label {
            color: black !important;
            font-weight: 600 !important;
        }
        
        /* 선택된 태그 스타일 */
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #2596be !important;
            color: white !important;
        }
        
        /* 드롭다운 메뉴 배경 - 연한 베이지색 */
        [data-baseweb="select"] > div,
        [data-baseweb="popover"] {
            background-color: #faf8f3 !important;  /* 연한 베이지 */
            color: black !important;
        }
        
        /* 드롭다운 옵션 */
        [data-baseweb="select"] li,
        [data-baseweb="menu"] li {
            background-color: #faf8f3 !important;
            color: black !important;
        }
        
        /* 드롭다운 옵션 호버 */
        [data-baseweb="select"] li:hover,
        [data-baseweb="menu"] li:hover {
            background-color: #f5f0e8 !important;
            color: black !important;
        }
        
        /* Slider */
        .stSlider {
            background-color: white !important;
        }
        
        .stSlider label {
            color: black !important;
            font-weight: 600 !important;
        }
        
        /* Radio */
        .stRadio {
            background-color: white !important;
        }
        
        .stRadio label {
            color: black !important;
            font-weight: 600 !important;
        }
        
        /* Checkbox */
        .stCheckbox label {
            color: black !important;
        }
        
        /* ========== 데이터프레임/테이블 - 완전 흰색 배경 ========== */
        .stDataFrame,
        [data-testid="stDataFrame"],
        .stDataFrame > div,
        .dataframe {
            background-color: white !important;
        }
        
        /* 테이블 전체 */
        .stDataFrame table,
        .dataframe table {
            background-color: white !important;
        }
        
        /* 테이블 헤더 */
        .stDataFrame thead tr th,
        .dataframe thead tr th {
            background-color: #f8f9fa !important;
            color: black !important;
            border-bottom: 2px solid #dee2e6 !important;
        }
        
        /* 테이블 바디 */
        .stDataFrame tbody tr td,
        .dataframe tbody tr td {
            background-color: white !important;
            color: black !important;
            border-bottom: 1px solid #e9ecef !important;
        }
        
        /* 짝수 행 배경색 (zebra striping) */
        .stDataFrame tbody tr:nth-child(even),
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa !important;
        }
        
        /* ========== 메트릭 스타일 ========== */
        [data-testid="stMetricValue"] {
            color: black !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #666 !important;
        }
        
        [data-testid="metric-container"] {
            background-color: white !important;
            border: 1px solid #d3d3d3 !important;  /* 연한 회색 */
            border-radius: 8px !important;
            padding: 1rem !important;
        }
        
        /* ========== 탭 스타일 ========== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: white !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: black !important;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            background-color: white !important;
            border: 1px solid #d0d0d0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #2596be !important;
            color: white !important;
            border: 1px solid #2596be !important;
        }
        
        /* ========== 버튼 스타일 ========== */
        .stButton button {
            color: white !important;
            background-color: #2596be !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
        }
        
        .stButton button:hover {
            background-color: #1e7a9e !important;
        }
        
        /* ========== 경고/정보 박스 ========== */
        .stAlert {
            color: black !important;
            background-color: white !important;
            border: 1px solid #d0d0d0 !important;
        }
        
        /* ========== 사이드바 너비 ========== */
        [data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 250px;
            max-width: 250px;
        }
        
    
        
        /* Streamlit 이미지 아래 여백 제거 */
        .stImage {
            margin-bottom: 0px !important;
        }
        
        img {
            margin-bottom: 0px !important;
            display: block !important;
        }
        
        /* 키워드 태그 스타일 */
        .keyword-tag {
            display: inline-block !important;
            padding: 8px 16px !important;
            margin: 6px !important;
            background-color: #2596be !important;
            color: white !important;
            border-radius: 20px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
        }
        
        /* 대표 작품 카드 */
        .rep-work-card {
            background: white !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
        }
        
        .rep-work-card h4 {
            color: #2596be !important;
            margin-bottom: 12px !important;
            font-size: 18px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def add_sidebar_footer():
    """사이드바 하단에 고정 텍스트 추가"""
    # CSS로 하단 고정
    st.markdown("""
    <style>
        .sidebar-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 250px;
            padding: 1rem;
            background-color: rgba(232, 245, 233, 0.95);  /* 연한 녹색 */
            border-top: 1px solid #a5d6a7;
            text-align: center;
            color: #2e7d32;  /* 진한 녹색 */
            font-size: 0.9rem;
            font-weight: 600;
            z-index: 999;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바에 고정 텍스트 추가
    st.sidebar.markdown(
        """
        <div class="sidebar-footer">
            © 2023 Team Yukapjang |<br>
            Streamlit Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )