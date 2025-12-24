"""
pages/2_synopsis.py

줄거리 탐색 페이지
- 영화/드라마 탭으로 구분
- TF-IDF 분석
- BERTopic 클러스터/토픽 분석 (원본 UMAP)
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from components import page_header
from utils.loader import load_tfidf_keywords
from utils.wordcloud_utils import generate_wordcloud_image
from utils.topic_mappings import get_cluster_name, get_topic_name



# =============================================================================
# 페이지 헤더
# =============================================================================
page_header(
    title="📝 줄거리 탐색",
    subtitle="TF-IDF 분석 및 BERTopic 클러스터 분석"
)

# ✅ 바로 여기!!
st.markdown(
    """
    <style>
    /* ===============================
       Selectbox / Multiselect 완전 흰색 고정
    =============================== */

    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }

    span[data-baseweb="tag"] {
        background-color: #e6f0ff !important;
        color: black !important;
        border-radius: 6px;
    }

    div[data-baseweb="popover"] {
        background-color: white !important;
    }

    div[data-baseweb="menu"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #d0d0d0 !important;
    }

    div[data-baseweb="menu"] * {
        color: black !important;
    }

    li[role="option"] {
        background-color: white !important;
        color: black !important;
    }

    li[role="option"]:hover {
        background-color: #f2f2f2 !important;
    }

    li[aria-selected="true"] {
        background-color: #e6f0ff !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# =============================================================================
# 공통 시각화 함수
# =============================================================================

def create_topic_map(df_map, df_clusters, category, selected_items, 
                     view_mode, content_type, content_type_label="드라마"):
    """
    UMAP 토픽 맵 생성 (원본 UMAP만 사용)
    
    Args:
        view_mode: 'cluster' 또는 'topic'
    """
    df = df_map.copy()
    
    # 컬럼명 표준화
    if '클러스터' in df_clusters.columns:
        cluster_col = '클러스터'
        topic_col = '토픽번호'
    else:
        cluster_col = 'cluster'
        topic_col = 'topic_id'
    
    # 클러스터 매핑
    if 'cluster' not in df.columns:
        topic_to_cluster = dict(zip(
            df_clusters[topic_col], 
            df_clusters[cluster_col]
        ))
        df['cluster'] = df['topic'].map(topic_to_cluster).fillna(-1).astype(int)
    
    # UMAP 좌표 확인
    if 'umap_x' not in df.columns or 'umap_y' not in df.columns:
        st.warning("UMAP 좌표가 없어 시각화를 생성할 수 없습니다.")
        return go.Figure()
    
    x_col, y_col = 'umap_x', 'umap_y'
    
    # 필터링
    if view_mode == 'cluster' and selected_items:
        df = df[df['cluster'].isin(selected_items)]
    elif view_mode == 'topic' and selected_items:
        df = df[df['topic'].isin(selected_items)]
    
    if len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="선택한 항목에 데이터가 없습니다.", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # 색상 그룹 설정
    if view_mode == 'cluster':
        # 클러스터명 매핑
        df['display_name'] = df['cluster'].apply(
            lambda x: get_cluster_name(content_type, category, x) if x != -1 else "Noise"
        )
        df['color_group'] = df['display_name']
        color_seq = px.colors.qualitative.Set2
    else:  # topic
        # 토픽명 매핑
        df['display_name'] = df['topic'].apply(
            lambda x: get_topic_name(content_type, category, x) if x != -1 else "Noise"
        )
        df['color_group'] = df['display_name']
        color_seq = px.colors.qualitative.Light24
    
    # 정렬 (Noise가 마지막)
    if view_mode == 'cluster':
        df['sort_key'] = df['cluster'].apply(lambda x: 999 if x == -1 else x)
    else:
        df['sort_key'] = df['topic'].apply(lambda x: 999 if x == -1 else x)
    df = df.sort_values('sort_key')
    
    # 호버 데이터
    hover_data = {'title': True, 'topic': True, 'display_name': True, x_col: False, y_col: False}
    if 'hit_score' in df.columns:
        df['hit_score_fmt'] = df['hit_score'].round(4)
        hover_data['hit_score_fmt'] = ':.4f'
    
    # 타이틀
    category_label = "🟢 흥행작" if category == 'hit' else "🔴 비흥행작"
    view_label = "클러스터" if view_mode == 'cluster' else "토픽"
    title = f"{category_label} {content_type_label} {view_label} Map"
    
    fig = px.scatter(
        df, x=x_col, y=y_col, color='color_group',
        hover_data=hover_data, title=title,
        color_discrete_sequence=color_seq,
        labels={x_col: 'UMAP X', y_col: 'UMAP Y', 'display_name': view_label}
    )
    
    fig.update_traces(marker=dict(size=10, opacity=0.75, line=dict(width=0.5, color='DarkSlateGray')))
    fig.update_layout(
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="v", 
            yanchor="top", 
            y=0.99, 
            xanchor="left", 
            x=1.02,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#d0d0d0',
            borderwidth=1,
            font=dict(color='black')  # 범례 글자 검정
        ),
        margin=dict(r=250),
        title_font=dict(color='black', size=16),
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        )
    )
    
    return fig


def create_keyword_comparison_chart(df_comparison, top_n=20):
    """키워드 비교 차트"""
    df = df_comparison.head(top_n)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("🟢 흥행작 고유 키워드", "🔴 비흥행작 고유 키워드"),
        horizontal_spacing=0.15
    )
    
    hit_kw = df[df['hit_unique_keyword'].notna() & (df['hit_unique_keyword'] != '')]
    if len(hit_kw) > 0:
        fig.add_trace(go.Bar(
            y=hit_kw['hit_unique_keyword'], x=hit_kw['hit_unique_score'],
            orientation='h', marker_color='mediumseagreen', name='흥행작', showlegend=False,
            text=hit_kw['hit_unique_keyword'],
            textfont=dict(color='black')  # 바 안 글자 검정
        ), row=1, col=1)
    
    flop_kw = df[df['flop_unique_keyword'].notna() & (df['flop_unique_keyword'] != '')]
    if len(flop_kw) > 0:
        fig.add_trace(go.Bar(
            y=flop_kw['flop_unique_keyword'], x=flop_kw['flop_unique_score'],
            orientation='h', marker_color='indianred', name='비흥행작', showlegend=False,
            text=flop_kw['flop_unique_keyword'],
            textfont=dict(color='black')  # 바 안 글자 검정
        ), row=1, col=2)
    
    fig.update_layout(
        height=600, 
        title_text="흥행작 vs 비흥행작 고유 키워드",
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font=dict(color='black', size=16),
        xaxis=dict(
            title_text="c-TF-IDF Score",
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        xaxis2=dict(
            title_text="c-TF-IDF Score",
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        yaxis=dict(tickfont=dict(color='black')),
        yaxis2=dict(tickfont=dict(color='black')),
        annotations=[
            dict(
                text="🟢 흥행작 고유 키워드",
                xref="paper", yref="paper",
                x=0.22, y=1.08,
                xanchor="center", yanchor="bottom",
                showarrow=False,
                font=dict(size=14, color='black')
            ),
            dict(
                text="🔴 비흥행작 고유 키워드",
                xref="paper", yref="paper",
                x=0.78, y=1.08,
                xanchor="center", yanchor="bottom",
                showarrow=False,
                font=dict(size=14, color='black')
            )
        ]
    )
    return fig


def create_distribution_chart(df_map, view_mode, category, content_type, content_type_label="드라마"):
    """
    클러스터/토픽별 분포 차트
    
    Args:
        view_mode: 'cluster' 또는 'topic'
    """
    if view_mode == 'cluster':
        group_col = 'cluster'
        label = '클러스터'
        
        # 클러스터명 매핑
        df_map = df_map.copy()
        df_map['display_name'] = df_map[group_col].apply(
            lambda x: get_cluster_name(content_type, category, x) if x != -1 else "Noise"
        )
    else:  # topic
        group_col = 'topic'
        label = '토픽'
        
        # 토픽명 매핑
        df_map = df_map.copy()
        df_map['display_name'] = df_map[group_col].apply(
            lambda x: get_topic_name(content_type, category, x) if x != -1 else "Noise"
        )
    
    summary = df_map.groupby('display_name').size().reset_index(name='count')
    
    category_label = "흥행작" if category == 'hit' else "비흥행작"
    
    fig = px.bar(
        summary, x='display_name', y='count',
        title=f"{category_label} {content_type_label} {label}별 분포",
        labels={'display_name': label, 'count': f'{content_type_label} 수'},
        color='count', color_continuous_scale='Viridis',
        text='count'  # 바 위에 숫자 표시
    )
    # 🔥 content_type에 따라 y축 설정 분기
    if content_type == "drama":
        yaxis_config = dict(
            title_font=dict(color='black'),
            tickfont=dict(color='black'),
            range=[0, 250],   # ✅ 드라마
            dtick=50
        )
    else:
        yaxis_config = dict(
            title_font=dict(color='black'),
            tickfont=dict(color='black'),
            range=[0, 2000],  # ✅ 영화
            dtick=400
        )

    fig.update_layout(
        height=600,  # 높이 증가
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font=dict(color='black', size=16),
        xaxis=dict(
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
         yaxis=yaxis_config   # ✅ 여기만 핵심
    )
    fig.update_traces(textfont=dict(color='black'), textposition='outside')  # 바 위 숫자 검정
    return fig


def render_topic_info_table(topic_info, content_type, category):
    """토픽 정보 테이블을 더 직관적으로 시각화"""
    topic_info = topic_info[topic_info['Topic'] != -1].copy()
    
    # 토픽명 매핑
    topic_info['토픽명'] = topic_info['Topic'].apply(
        lambda x: get_topic_name(content_type, category, x)
    )
    
    # 표시할 컬럼 선택
    display_cols = ['Topic', '토픽명', 'Count', 'Name']
    if 'Representative_Docs_Titles' in topic_info.columns:
        display_cols.append('Representative_Docs_Titles')
    
    topic_display = topic_info[[c for c in display_cols if c in topic_info.columns]].copy()
    
    # 컬럼명 한글화
    topic_display = topic_display.rename(columns={
        'Topic': 'ID',
        'Count': '문서수',
        'Name': '키워드',
        'Representative_Docs_Titles': '대표 작품'
    })
    
    st.dataframe(
        topic_display,
        width='stretch',  # 변경
        hide_index=True,
        height=500,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "토픽명": st.column_config.TextColumn("토픽명", width="large"),
            "문서수": st.column_config.NumberColumn("문서수", width="small"),
            "키워드": st.column_config.TextColumn("키워드", width="medium"),
            "대표 작품": st.column_config.TextColumn("대표 작품", width="large")
        }
    )


def render_bertopic_section(data, content_type, content_type_label="드라마", key_prefix="drama"):
    """BERTopic 분석 섹션 렌더링"""
    
    st.markdown("### ⚙️ 시각화 설정")
    
    # 첫 번째 행: 분석 대상, 보기 모드
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "분석 대상",
            options=['hit', 'flop'],
            format_func=lambda x: '🟢 흥행작 (상위 20%)' if x == 'hit' else '🔴 비흥행작 (하위 20%)',
            key=f'{key_prefix}_category'
        )
    
    with col2:
        view_mode = st.selectbox(
            "보기 모드",
            options=['cluster', 'topic'],
            format_func=lambda x: '📦 클러스터' if x == 'cluster' else '🎨 토픽',
            key=f'{key_prefix}_view_mode'
        )
    
    # 현재 카테고리 데이터
    df_map = data['hit_map'] if category == 'hit' else data['flop_map']
    df_clusters = data['hit_clusters'] if category == 'hit' else data['flop_clusters']
    df_topic_info = data['hit_topic_info'] if category == 'hit' else data['flop_topic_info']
    
    # 컬럼명 표준화
    if '클러스터' in df_clusters.columns:
        cluster_col = '클러스터'
        topic_col = '토픽번호'
    else:
        cluster_col = 'cluster'
        topic_col = 'topic_id'
    
    # 클러스터/토픽 목록
    if view_mode == 'cluster':
        # 클러스터 매핑이 없으면 생성
        if 'cluster' not in df_map.columns:
            topic_to_cluster = dict(zip(
                df_clusters[topic_col], 
                df_clusters[cluster_col]
            ))
            df_map = df_map.copy()
            df_map['cluster'] = df_map['topic'].map(topic_to_cluster).fillna(-1).astype(int)
        
        all_items = sorted([c for c in df_map['cluster'].unique().tolist() if c != -1])
        format_func = lambda x: get_cluster_name(content_type, category, x)
        filter_label = "클러스터 필터 (전체 보려면 비워두세요)"
    else:  # topic
        all_items = sorted([t for t in df_map['topic'].unique().tolist() if t != -1])
        format_func = lambda x: get_topic_name(content_type, category, x)
        filter_label = "토픽 필터 (전체 보려면 비워두세요)"
    
    # 두 번째 행: 필터 (전체 너비)
    selected_items = st.multiselect(
        filter_label,
        options=all_items,
        default=all_items,
        format_func=format_func,
        key=f'{key_prefix}_items'
    )
    
    st.markdown("---")
    
    # 📊 Topic Map 탭에 모든 내용 통합
    
    # 1. 메트릭 (상단)
    col_m1, col_m2 = st.columns(2)
    
    total_items = len(df_map)
    
    if view_mode == 'cluster':
        total_groups = len(all_items)
        group_label = "클러스터"
    else:
        total_groups = len(all_items)
        group_label = "토픽"
    
    category_emoji = "🟢" if category == "hit" else "🔴"
    category_text = "흥행작" if category == "hit" else "비흥행작"
    
    with col_m1:
        st.metric(f"{category_emoji} {category_text} {content_type_label}", total_items)
    with col_m2:
        st.metric(f"{category_emoji} {category_text} {group_label}", total_groups)
    
    st.markdown("---")
    
    # 2. Topic Map
    st.markdown(f"#### 📊 {group_label} Map")
    fig_map = create_topic_map(
        df_map, df_clusters, category, selected_items,
        view_mode, content_type, content_type_label
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")
    
    # 3. 분포
    st.markdown(f"#### 📈 {group_label}별 분포")
    fig_dist = create_distribution_chart(df_map, view_mode, category, content_type, content_type_label)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("---")
    
    # 4. 키워드 비교
    if 'keyword_comparison' in data and data['keyword_comparison'] is not None:
        st.markdown("#### 🔍 키워드 비교")
        top_n = st.slider("표시할 키워드 수", 10, 50, 20, 5, key=f'{key_prefix}_topn')
        fig_kw = create_keyword_comparison_chart(data['keyword_comparison'], top_n)
        st.plotly_chart(fig_kw, use_container_width=True)
        
        st.markdown("""
        **해석 가이드:**
        - **흥행작 고유 키워드**: 흥행작에서만 자주 등장하는 키워드
        - **비흥행작 고유 키워드**: 비흥행작에서만 자주 등장하는 키워드
        """)
        
        st.markdown("---")
    
    # 5. 토픽 상세 정보
    st.markdown("#### 📋 토픽 상세 정보")
    render_topic_info_table(df_topic_info, content_type, category)


# =============================================================================
# 데이터 로드 함수
# =============================================================================

@st.cache_data
def load_drama_bertopic_data():
    """드라마 BERTopic 데이터 로드"""
    try:
        base_path = "data/02_synopsis/drama"
        
        data = {
            'hit_map': pd.read_csv(f"{base_path}/hit_umap_map.csv"),
            'flop_map': pd.read_csv(f"{base_path}/flop_umap_map.csv"),
            'hit_clusters': pd.read_csv(f"{base_path}/hit_clusters.csv"),
            'flop_clusters': pd.read_csv(f"{base_path}/flop_clusters.csv"),
            'hit_topic_info': pd.read_csv(f"{base_path}/hit_topic_info.csv"),
            'flop_topic_info': pd.read_csv(f"{base_path}/flop_topic_info.csv"),
        }
        
        # 키워드 비교 (선택적)
        try:
            data['keyword_comparison'] = pd.read_csv(f"{base_path}/keyword_comparison.csv")
        except FileNotFoundError:
            data['keyword_comparison'] = None
        
        return data
    except FileNotFoundError:
        return None


@st.cache_data
def load_movie_bertopic_data():
    """영화 BERTopic 데이터 로드"""
    base_path = "data/02_synopsis/movie"

    try:
        # hit_map
        if os.path.exists(f"{base_path}/hit_umap_map.csv"):
            hit_map = pd.read_csv(f"{base_path}/hit_umap_map.csv")
        else:
            hit_map = pd.read_csv(f"{base_path}/hit_topic_info.csv")
            hit_map = hit_map.rename(columns={"Topic": "topic"})
            hit_map["title"] = ""

        # flop_map
        if os.path.exists(f"{base_path}/flop_umap_map.csv"):
            flop_map = pd.read_csv(f"{base_path}/flop_umap_map.csv")
        else:
            flop_map = pd.read_csv(f"{base_path}/flop_topic_info.csv")
            flop_map = flop_map.rename(columns={"Topic": "topic"})
            flop_map["title"] = ""

        data = {
            "hit_map": hit_map,
            "flop_map": flop_map,
            "hit_clusters": pd.read_csv(f"{base_path}/hit_clusters.csv"),
            "flop_clusters": pd.read_csv(f"{base_path}/flop_clusters.csv"),
            "hit_topic_info": pd.read_csv(f"{base_path}/hit_topic_info.csv"),
            "flop_topic_info": pd.read_csv(f"{base_path}/flop_topic_info.csv"),
        }

        # 키워드 비교 (선택)
        try:
            data["keyword_comparison"] = pd.read_csv(f"{base_path}/keyword_comparison.csv")
        except FileNotFoundError:
            data["keyword_comparison"] = None

        return data

    except FileNotFoundError:
        return None


# =============================================================================
# 메인 콘텐츠 - 영화/드라마 탭으로 분리
# =============================================================================

main_tab1, main_tab2 = st.tabs(["🎬 영화", "📺 드라마"])

# =============================================================================
# 영화 탭
# =============================================================================
with main_tab1:
    st.header("🎬 영화 줄거리 분석")
    
    movie_tab1, movie_tab2 = st.tabs(["📊 TF-IDF 분석", "🎯 BERTopic 클러스터"])
    
    with movie_tab1:
        st.subheader("🎬 영화 TF-IDF 키워드")
        
        st.markdown("""
        ※ 단어 빈도가 높을수록 크게 표현됩니다.  
        상위 30개 키워드만 표시됩니다.
        """)
        
        st.markdown("---")

        col1, col2 = st.columns(2)

        # 흥행작
        with col1:
            st.markdown("### 🟢 흥행작 키워드")
            df_hit = load_tfidf_keywords("movie", "hit")
            FONT_PATH = r"C:\Users\lizzy\OneDrive\바탕 화면\최종플젝\최종데이터셋\스트림릿\assets\fonts\MaruBuri-Bold.ttf"
            img = generate_wordcloud_image(
                df_hit,
                color_palette=["#fc8d59", "#f781bf", "#ff4c42"],
                font_path=FONT_PATH
            )
            st.image(img)

        # 비흥행작
        with col2:
            st.markdown("### 🔴 비흥행작 키워드")
            df_flop = load_tfidf_keywords("movie", "flop")
            img = generate_wordcloud_image(
                df_flop,
                color_palette=["#4d4d4d", "#91bfdb", "#c2a5cf"],
                font_path=FONT_PATH
            )
            st.image(img)

    
    with movie_tab2:
        st.markdown("""
        ***흥행작: hit_score 상위 20% / 비흥행작: hit_score 하위 20%***
        """)
        st.markdown("---")
        
        movie_data = load_movie_bertopic_data()
        
        if movie_data is None:
            st.error("⚠️ 영화 BERTopic 데이터를 찾을 수 없습니다.")
            st.info("""
            **필요한 파일 (data/02_synopsis/movie/):**
            - hit_umap_map.csv / flop_umap_map.csv
            - hit_clusters.csv / flop_clusters.csv
            - hit_topic_info.csv / flop_topic_info.csv
            
            `BERTOPIC코드/prepare_streamlit_data.py` 스크립트를 실행하세요.
            """)
        else:
            render_bertopic_section(movie_data, content_type="movie", 
                                   content_type_label="영화", key_prefix="movie")


# =============================================================================
# 드라마 탭
# =============================================================================
with main_tab2:
    st.header("📺 드라마 줄거리 분석")
    
    drama_tab1, drama_tab2 = st.tabs(["📊 TF-IDF 분석", "🎯 BERTopic 클러스터"])
    
    with drama_tab1:
        st.subheader("📺 드라마 TF-IDF 키워드")
        
        st.markdown("""
        ※ 단어 빈도가 높을수록 크게 표현됩니다.  
        상위 30개 키워드만 표시됩니다.
        """)
        
        st.markdown("---")

        col1, col2 = st.columns(2)

        # 흥행작
        with col1:
            st.markdown("### 🟢 흥행작 키워드")
            df_hit = load_tfidf_keywords("drama", "hit")
            FONT_PATH = r"C:\Users\lizzy\OneDrive\바탕 화면\최종플젝\최종데이터셋\스트림릿\assets\fonts\MaruBuri-Bold.ttf"
            img = generate_wordcloud_image(
                df_hit,
                color_palette=["#d73027", "#fc8d59", "#f781bf"],
                font_path=FONT_PATH
            )
            st.image(img)

        # 비흥행작
        with col2:
            st.markdown("### 🔴 비흥행작 키워드")
            df_flop = load_tfidf_keywords("drama", "flop")
            img = generate_wordcloud_image(
                df_flop,
                color_palette=["#4d4d4d", "#91bfdb", "#c2a5cf"],
                font_path=FONT_PATH
            )
            st.image(img)

        
    with drama_tab2:
        st.markdown("""
        ***흥행작: hit_score 상위 20% / 비흥행작: hit_score 하위 20%***
        """)
        st.markdown("---")
        
        drama_data = load_drama_bertopic_data()
        
        if drama_data is None:
            st.error("⚠️ 드라마 BERTopic 데이터를 찾을 수 없습니다.")
            st.info("""
            **필요한 파일 (data/02_synopsis/drama/):**
            - hit_umap_map.csv / flop_umap_map.csv
            - hit_clusters.csv / flop_clusters.csv
            - hit_topic_info.csv / flop_topic_info.csv
            
            `BERTOPIC코드/prepare_streamlit_data.py` 스크립트를 실행하세요.
            """)
        else:
            render_bertopic_section(drama_data, content_type="drama", 
                                   content_type_label="드라마", key_prefix="drama")
