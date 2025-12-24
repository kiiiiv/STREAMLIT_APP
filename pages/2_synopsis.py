"""
pages/2_synopsis.py

줄거리 탐색 페이지
- 영화/드라마 탭으로 구분
- TF-IDF 분석
- BERTopic 클러스터/토픽 분석 (원본 UMAP)
- 대표 작품 탭 추가
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

# ✅ 폰트 경로를 상대 경로로 변경 (배포 환경 호환)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # pages/ → streamlit_app/
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "MaruBuri-Bold.ttf")

# 폰트 파일이 없으면 None 사용 (기본 폰트)
if not os.path.exists(FONT_PATH):
    FONT_PATH = None

# =============================================================================
# 페이지 헤더
# =============================================================================
page_header(
    title="📝 줄거리 탐색",
    subtitle="TF-IDF 분석 및 BERTopic 클러스터 분석"
)

st.markdown(
    """
    <style>
    /* Selectbox / Multiselect 완전 흰색 */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }
    span[data-baseweb="tag"] {
        background-color: #e6f0ff !important;
        color: black !important;
        border-radius: 6px;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #d0d0d0 !important;
    }
    div[data-baseweb="menu"] * { color: black !important; }
    li[role="option"] {
        background-color: white !important;
        color: black !important;
    }
    li[role="option"]:hover { background-color: #f2f2f2 !important; }
    li[aria-selected="true"] {
        background-color: #e6f0ff !important;
        font-weight: 600;
    }
    
    /* 키워드 태그 스타일 - 크기 증가 */
    .keyword-tag {
        display: inline-block;
        padding: 8px 16px;  /* 증가: 4px 12px → 8px 16px */
        margin: 6px;  /* 증가: 4px → 6px */
        background-color: #2596be;
        color: white;
        border-radius: 20px;  /* 증가: 16px → 20px */
        font-size: 16px;  /* 증가: 13px → 16px */
        font-weight: 600;  /* 증가: 500 → 600 */
    }
    
    /* 대표 작품 카드 */
    .rep-work-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .rep-work-card h4 {
        color: #2596be;
        margin-bottom: 12px;
        font-size: 18px;
    }
    
    /* 영화 제목 크기 증가 */
    .movie-title {
        font-size: 20px !important;
        font-weight: 600 !important;
        text-align: left !important;
        margin-top: 4px !important;
        margin-bottom: 20px !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
        color: #333;
        line-height: 1.5;
        width: 100%;
        display: block;
    }
    
    /* Streamlit 이미지 아래 여백 제거 */
    .stImage {
        margin-bottom: 0px !important;
    }
    
    img {
        margin-bottom: 0px !important;
        display: block;
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
    """UMAP 토픽 맵 생성"""
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
        df['display_name'] = df['cluster'].apply(
            lambda x: get_cluster_name(content_type, category, x) if x != -1 else "Noise"
        )
        df['color_group'] = df['display_name']
        color_seq = px.colors.qualitative.Set2
    else:
        df['display_name'] = df['topic'].apply(
            lambda x: get_topic_name(content_type, category, x) if x != -1 else "Noise"
        )
        df['color_group'] = df['display_name']
        color_seq = px.colors.qualitative.Light24
    
    # 정렬
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
            font=dict(color='black')
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
            textfont=dict(color='black')
        ), row=1, col=1)
    
    flop_kw = df[df['flop_unique_keyword'].notna() & (df['flop_unique_keyword'] != '')]
    if len(flop_kw) > 0:
        fig.add_trace(go.Bar(
            y=flop_kw['flop_unique_keyword'], x=flop_kw['flop_unique_score'],
            orientation='h', marker_color='indianred', name='비흥행작', showlegend=False,
            textfont=dict(color='black')
        ), row=1, col=2)
    
    fig.update_layout(
        height=600, 
        plot_bgcolor='white',
        paper_bgcolor='white',
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
        # 👇👇 여기 추가
        yaxis=dict(
            tickfont=dict(color='black', size=16)   # ← 기본 12 → 14
        ),
        yaxis2=dict(
            tickfont=dict(color='black', size=16)
        ),
        annotations=[
            dict(
                text="🟢 흥행작 고유 키워드",
                xref="paper", yref="paper",
                x=0.22, y=1.08,
                xanchor="center", yanchor="bottom",
                showarrow=False,
                font=dict(size=18, color='black')
            ),
            dict(
                text="🔴 비흥행작 고유 키워드",
                xref="paper", yref="paper",
                x=0.78, y=1.08,
                xanchor="center", yanchor="bottom",
                showarrow=False,
                font=dict(size=18, color='black')
            )
        ]
    )
    return fig


def create_distribution_chart(df_map, view_mode, category, content_type, content_type_label="드라마"):
    """클러스터/토픽별 분포 차트 - Noise 제거, 색상 변경, y축 조정"""
    if view_mode == 'cluster':
        group_col = 'cluster'
        label = '클러스터'
        df_map = df_map.copy()
        df_map['display_name'] = df_map[group_col].apply(
            lambda x: get_cluster_name(content_type, category, x) if x != -1 else "Noise"
        )
    else:
        group_col = 'topic'
        label = '토픽'
        df_map = df_map.copy()
        df_map['display_name'] = df_map[group_col].apply(
            lambda x: get_topic_name(content_type, category, x) if x != -1 else "Noise"
        )
    
    # ✅ 1. Noise 제거
    summary = df_map[df_map['display_name'] != 'Noise'].groupby('display_name').size().reset_index(name='count')
    
    category_label = "흥행작" if category == 'hit' else "비흥행작"
    
    # ✅ 2. 색상: 연녹색(낮은 값) → 연주황(높은 값)
    fig = px.bar(
        summary, x='display_name', y='count',
        title=f"{category_label} {content_type_label} {label}별 분포",
        labels={'display_name': label, 'count': f'{content_type_label} 수'},
        color='count',
        color_continuous_scale=[[0, '#c8e6c9'], [0.5, '#ffeb3b'], [1, '#ffcc80']],  # 연녹 → 연노랑 → 연주황
        text='count'
    )
    
    # ✅ 3. y축 설정
    if content_type == "drama":
        yaxis_config = dict(
            title_font=dict(color='black'),
            tickfont=dict(color='black'),
            range=[0, 250],
            dtick=50
        )
    else:
        yaxis_config = dict(
            title_font=dict(color='black'),
            tickfont=dict(color='black'),
            range=[0, 1600],  # 변경: 2000 → 1600
            dtick=400
        )

    fig.update_layout(
        height=600,
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font=dict(color='black', size=16),
        xaxis=dict(
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        yaxis=yaxis_config
    )
    fig.update_traces(textfont=dict(color='black'), textposition='outside')
    return fig



# ========== 새로운 함수: 대표 작품 렌더링 ==========
def render_representative_works(data, content_type, content_type_label="드라마", key_prefix="drama"):
    """토픽/클러스터별 대표 작품 3개 + 포스터 이미지 + 키워드 태그"""
    
    st.markdown("### ⚙️ 표시 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "분석 대상",
            options=['hit', 'flop'],
            format_func=lambda x: '🟢 흥행작 (상위 20%)' if x == 'hit' else '🔴 비흥행작 (하위 20%)',
            key=f'{key_prefix}_rep_category'
        )
    
    with col2:
        view_mode = st.selectbox(
            "보기 모드",
            options=['topic', 'cluster'],
            format_func=lambda x: '🎨 토픽별' if x == 'topic' else '📦 클러스터별',
            key=f'{key_prefix}_rep_view'
        )
    
    # 데이터 로드
    df_clusters = data['hit_clusters'] if category == 'hit' else data['flop_clusters']
    df_topic_info = data['hit_topic_info'] if category == 'hit' else data['flop_topic_info']
    df_map = data['hit_map'] if category == 'hit' else data['flop_map']
    
    # 컬럼명 표준화
    if '클러스터' in df_clusters.columns:
        cluster_col = '클러스터'
        topic_col = '토픽번호'
        keywords_col = '키워드'
    else:
        cluster_col = 'cluster'
        topic_col = 'topic_id'
        keywords_col = 'keywords'
    
    # ========== 필터 드롭다운 추가 (단일 선택) ==========
    if view_mode == 'topic':
        # 토픽 필터
        df_topic_info_filtered = df_topic_info[df_topic_info['Topic'] != -1].copy()
        all_topics = sorted(df_topic_info_filtered['Topic'].tolist())
        
        # 토픽 ID → 이름 매핑
        topic_options = {
            topic_id: get_topic_name(content_type, category, topic_id)
            for topic_id in all_topics
        }
        
        # 단일 선택 드롭다운
        selected_topic = st.selectbox(
            "🎨 토픽 선택",
            options=['전체'] + all_topics,
            format_func=lambda x: '전체 토픽' if x == '전체' else topic_options[x],
            key=f'{key_prefix}_topic_filter'
        )
        
        # 선택된 토픽만 필터링
        if selected_topic != '전체':
            selected_topics = [selected_topic]
        else:
            selected_topics = all_topics
    else:
        # 클러스터 필터
        all_clusters = sorted(df_clusters[cluster_col].unique().tolist())
        
        # 클러스터 ID → 이름 매핑
        cluster_options = {
            cluster_id: get_cluster_name(content_type, category, cluster_id)
            for cluster_id in all_clusters
        }
        
        # 단일 선택 드롭다운
        selected_cluster = st.selectbox(
            "📦 클러스터 선택",
            options=['전체'] + all_clusters,
            format_func=lambda x: '전체 클러스터' if x == '전체' else cluster_options[x],
            key=f'{key_prefix}_cluster_filter'
        )
        
        # 선택된 클러스터만 필터링
        if selected_cluster != '전체':
            selected_clusters = [selected_cluster]
        else:
            selected_clusters = all_clusters
    
    st.markdown("---")
    
    # ========== 포스터 매핑 (최적화: 필요한 것만 로드) ==========
    title_to_poster = {}
    
    # 필터링된 토픽/클러스터에 해당하는 작품만 추출
    if view_mode == 'topic':
        filtered_topic_info = df_topic_info_filtered[df_topic_info_filtered['Topic'].isin(selected_topics)]
        needed_titles = set()
        for _, row in filtered_topic_info.iterrows():
            rep_titles_raw = row.get('Representative_Docs_Titles', '')
            if isinstance(rep_titles_raw, str) and rep_titles_raw:
                needed_titles.update([t.strip() for t in rep_titles_raw.split('|')][:3])
    else:
        filtered_clusters = df_clusters[df_clusters[cluster_col].isin(selected_clusters)]
        needed_titles = set()
        for cluster_id in selected_clusters:
            cluster_topics = filtered_clusters[filtered_clusters[cluster_col] == cluster_id][topic_col].tolist()
            for topic_id in cluster_topics:
                topic_row = df_topic_info[df_topic_info['Topic'] == topic_id]
                if len(topic_row) > 0:
                    rep_titles_raw = topic_row.iloc[0].get('Representative_Docs_Titles', '')
                    if isinstance(rep_titles_raw, str) and rep_titles_raw:
                        needed_titles.update([t.strip() for t in rep_titles_raw.split('|')][:3])
    
    # ==================== render_representative_works 함수의 포스터 로딩 부분 교체 ====================

    # 필요한 포스터만 로드 (성능 최적화)
    poster_loaded = False
    try:
        # 방법 1: 배포 환경 경로 시도
        if content_type == "drama":
            import_path = os.path.join(BASE_DIR, "data", "embeddings", "drama_text_embedding_poster.parquet")
        else:
            import_path = os.path.join(BASE_DIR, "data", "embeddings", "movie_text_embedding_poster.parquet")

        if os.path.exists(import_path):
            df_original = pd.read_parquet(import_path, columns=["imdb_id", "title", "poster_path"])
            poster_loaded = True
        else:
            # 방법 2: 로컬 환경 경로 시도
            if content_type == "drama":
                import_path = r"C:\Users\lizzy\OneDrive\바탕 화면\최종플젝\최종데이터셋\최종데이터셋_드라마\drama_text_embedding_qwen3.parquet"
            else:
                import_path = r"C:\Users\lizzy\OneDrive\바탕 화면\최종플젝\최종데이터셋\최종데이터셋_영화\movie_text_embedding_qwen3.parquet"
            
            if os.path.exists(import_path):
                df_original = pd.read_parquet(import_path, columns=["imdb_id", "title", "poster_path"])
                poster_loaded = True

        if poster_loaded:
            # 필요한 제목만 매핑
            for title in needed_titles:
                if 'title' not in df_map.columns:
                    continue
                    
                title_row = df_map[df_map['title'] == title]
                if len(title_row) == 0:
                    continue

                imdb_id = title_row.iloc[0]["imdb_id"]
                poster_row = df_original[df_original["imdb_id"] == imdb_id]
                
                if len(poster_row) > 0 and 'poster_path' in poster_row.columns:
                    poster_path = poster_row.iloc[0]["poster_path"]
                    if pd.notna(poster_path) and poster_path:
                        title_to_poster[title] = f"https://image.tmdb.org/t/p/w300{poster_path}"
        else:
            st.info("📌 포스터 이미지 파일을 찾을 수 없습니다. 제목만 표시됩니다.")

    except Exception as e:
        st.warning(f"⚠️ 포스터 로딩 중 오류: {str(e)}")




    
    # ========== 콘텐츠 렌더링 ==========
    
    if view_mode == 'topic':
        # 토픽별 표시
        df_topic_info_display = df_topic_info_filtered[df_topic_info_filtered['Topic'].isin(selected_topics)]
        
        if len(df_topic_info_display) == 0:
            st.info("📭 선택한 토픽이 없습니다. 위에서 토픽을 선택하세요.")
            return
        
        for idx, row in df_topic_info_display.iterrows():
            topic_id = row['Topic']
            topic_name = get_topic_name(content_type, category, topic_id)
            
            # 키워드 추출 (숫자 제거)
            keywords_raw = row.get('Name', '')
            keywords = []
            for kw in keywords_raw.split('_'):
                kw = kw.strip()
                # 숫자만으로 이루어진 키워드 제거
                if kw and not kw.isdigit():
                    keywords.append(kw)
            keywords = keywords[:10]
            
            # 대표 작품
            rep_titles_raw = row.get('Representative_Docs_Titles', '')
            if isinstance(rep_titles_raw, str) and rep_titles_raw:
                rep_titles = [t.strip() for t in rep_titles_raw.split('|')][:3]
            else:
                rep_titles = []
            
            # 카드 헤더
            st.markdown(f"""
            <div class="rep-work-card">
                <h4>📌 {topic_name}</h4>
                <p><strong>작품 수:</strong> {row.get('Count', 0)}개</p>
            """, unsafe_allow_html=True)
            
            # 대표 작품 섹션
            if rep_titles:
                st.markdown("<p><strong>대표 작품:</strong></p>", unsafe_allow_html=True)
                
                # 포스터 이미지 3개 (크기 증가)
                cols = st.columns(len(rep_titles))
                for i, title in enumerate(rep_titles):
                    with cols[i]:
                        poster_url = title_to_poster.get(title)
                        if poster_url:
                            st.image(poster_url, width=260)  # 크기 증가: 220px → 260px
                            st.markdown(f"<p class='movie-title' style='margin-left:0;padding-left:0;'>{title}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                width: 260px;
                                aspect-ratio: 2/3;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-size: 12px;
                                text-align: center;
                                padding: 16px;
                                border-radius: 8px;
                                margin: 0 auto;
                            '>
                                No Poster
                            </div>
                            <p class='movie-title'>{title}</p>
                            """, unsafe_allow_html=True)
            
            # 키워드 섹션
            if keywords:
                st.markdown("<p><strong>키워드:</strong></p>", unsafe_allow_html=True)
                keywords_html = " ".join([f'<span class="keyword-tag">{kw}</span>' for kw in keywords])
                st.markdown(keywords_html, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # 클러스터별 표시
        cluster_ids_display = [c for c in sorted(df_clusters[cluster_col].unique()) if c in selected_clusters]
        
        if len(cluster_ids_display) == 0:
            st.info("📭 선택한 클러스터가 없습니다. 위에서 클러스터를 선택하세요.")
            return
        
        for cluster_id in cluster_ids_display:
            cluster_name = get_cluster_name(content_type, category, cluster_id)
            
            # 해당 클러스터의 토픽들
            cluster_topics = df_clusters[df_clusters[cluster_col] == cluster_id][topic_col].tolist()
            
            # 키워드
            cluster_keywords_raw = df_clusters[df_clusters[cluster_col] == cluster_id][keywords_col].iloc[0] if keywords_col in df_clusters.columns else ''
            cluster_keywords = [kw.strip() for kw in cluster_keywords_raw.split(',') if kw.strip()][:10]
            
            # 대표 작품
            rep_works = []
            for topic_id in cluster_topics:
                topic_row = df_topic_info[df_topic_info['Topic'] == topic_id]
                if len(topic_row) > 0:
                    rep_titles_raw = topic_row.iloc[0].get('Representative_Docs_Titles', '')
                    if isinstance(rep_titles_raw, str) and rep_titles_raw:
                        rep_works.extend([t.strip() for t in rep_titles_raw.split('|')])
            
            rep_works = rep_works[:3]
            
            # 카드 헤더
            st.markdown(f"""
            <div class="rep-work-card">
                <h4>📦 {cluster_name}</h4>
                <p><strong>포함 토픽:</strong> {', '.join([str(t) for t in cluster_topics])}</p>
            """, unsafe_allow_html=True)
            
            # 대표 작품 섹션
            if rep_works:
                st.markdown("<p><strong>대표 작품:</strong></p>", unsafe_allow_html=True)
                
                # 포스터 이미지 (크기 증가)
                cols = st.columns(len(rep_works))
                for i, title in enumerate(rep_works):
                    with cols[i]:
                        poster_url = title_to_poster.get(title)
                        if poster_url:
                            st.image(poster_url, width=260)  # 크기 증가: 220px → 260px
                            st.markdown(f"<p class='movie-title' style='margin-left:0;padding-left:0;'>{title}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                width: 260px;
                                aspect-ratio: 2/3;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-size: 12px;
                                text-align: center;
                                padding: 16px;
                                border-radius: 8px;
                                margin: 0 auto;
                            '>
                                No Poster
                            </div>
                            <p class='movie-title'>{title}</p>
                            """, unsafe_allow_html=True)
            
            # 키워드 섹션
            if cluster_keywords:
                st.markdown("<p><strong>키워드:</strong></p>", unsafe_allow_html=True)
                keywords_html = " ".join([f'<span class="keyword-tag">{kw}</span>' for kw in cluster_keywords])
                st.markdown(keywords_html, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)


def render_bertopic_section(data, content_type, content_type_label="드라마", key_prefix="drama"):
    """BERTopic 분석 섹션 렌더링 - 토픽 상세 정보 제거"""
    
    st.markdown("### ⚙️ 시각화 설정")
    
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
    
    df_map = data['hit_map'] if category == 'hit' else data['flop_map']
    df_clusters = data['hit_clusters'] if category == 'hit' else data['flop_clusters']
    df_topic_info = data['hit_topic_info'] if category == 'hit' else data['flop_topic_info']
    
    if '클러스터' in df_clusters.columns:
        cluster_col = '클러스터'
        topic_col = '토픽번호'
    else:
        cluster_col = 'cluster'
        topic_col = 'topic_id'
    
    if view_mode == 'cluster':
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
    else:
        all_items = sorted([t for t in df_map['topic'].unique().tolist() if t != -1])
        format_func = lambda x: get_topic_name(content_type, category, x)
        filter_label = "토픽 필터 (전체 보려면 비워두세요)"
    
    selected_items = st.multiselect(
        filter_label,
        options=all_items,
        default=all_items,
        format_func=format_func,
        key=f'{key_prefix}_items'
    )
    
    st.markdown("---")
    
    # 메트릭
    col_m1, col_m2 = st.columns(2)
    
    total_items = len(df_map)
    total_groups = len(all_items)
    group_label = "클러스터" if view_mode == 'cluster' else "토픽"
    category_emoji = "🟢" if category == "hit" else "🔴"
    category_text = "흥행작" if category == "hit" else "비흥행작"
    
    with col_m1:
        st.metric(f"{category_emoji} {category_text} {content_type_label}", total_items)
    with col_m2:
        st.metric(f"{category_emoji} {category_text} {group_label}", total_groups)
    
    st.markdown("---")
    
    # Topic Map
    st.markdown(f"#### 📊 {group_label} Map")
    fig_map = create_topic_map(
        df_map, df_clusters, category, selected_items,
        view_mode, content_type, content_type_label
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")

    # ✅ 3. 키워드 비교 (순서 변경: 분포 다음으로)
    if 'keyword_comparison' in data and data['keyword_comparison'] is not None:
        st.markdown("#### 🔍 흥행작 vs 비흥행작 키워드 비교")
        st.markdown('''
        **해석 가이드:**
        - **흥행작 고유 키워드**: 흥행작에서만 자주 등장하는 키워드
        - **비흥행작 고유 키워드**: 비흥행작에서만 자주 등장하는 키워드
        ''')
        top_n = st.slider("표시할 키워드 수", 10, 50, 20, 5, key=f'{key_prefix}_topn')
        fig_kw = create_keyword_comparison_chart(data['keyword_comparison'], top_n)
        st.plotly_chart(fig_kw, use_container_width=True)
    
    # ✅ 2. 분포 (순서 변경: 키워드 비교보다 먼저)
    st.markdown(f"#### 📈 {group_label}별 분포")
    fig_dist = create_distribution_chart(df_map, view_mode, category, content_type, content_type_label)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("---")
    
    
    


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
        if os.path.exists(f"{base_path}/hit_umap_map.csv"):
            hit_map = pd.read_csv(f"{base_path}/hit_umap_map.csv")
        else:
            hit_map = pd.read_csv(f"{base_path}/hit_topic_info.csv")
            hit_map = hit_map.rename(columns={"Topic": "topic"})
            hit_map["title"] = ""

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

        try:
            data["keyword_comparison"] = pd.read_csv(f"{base_path}/keyword_comparison.csv")
        except FileNotFoundError:
            data["keyword_comparison"] = None

        return data

    except FileNotFoundError:
        return None


# =============================================================================
# 메인 콘텐츠
# =============================================================================

main_tab1, main_tab2 = st.tabs(["🎬 영화", "📺 드라마"])

# 영화 탭
with main_tab1:
    st.header("🎬 영화 줄거리 분석")
    
    movie_tab1, movie_tab2, movie_tab3 = st.tabs(["📊 TF-IDF 분석", "🎯 BERTopic 클러스터", "🎬 대표 작품"])
    
    with movie_tab1:
        st.subheader("🎬 영화 TF-IDF 키워드")
        st.markdown("※ 단어 빈도가 높을수록 크게 표현됩니다. 상위 30개 키워드만 표시됩니다.")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 흥행작 키워드")
            df_hit = load_tfidf_keywords("movie", "hit")
            img = generate_wordcloud_image(df_hit, color_palette=["#fc8d59", "#f781bf", "#ff4c42"], font_path=FONT_PATH)
            st.image(img)
        with col2:
            st.markdown("### 🔴 비흥행작 키워드")
            df_flop = load_tfidf_keywords("movie", "flop")
            img = generate_wordcloud_image(df_flop, color_palette=["#4d4d4d", "#91bfdb", "#c2a5cf"], font_path=FONT_PATH)
            st.image(img)

    with movie_tab2:
        st.markdown("***흥행작: hit_score 상위 20% / 비흥행작: hit_score 하위 20%***")
        st.markdown("---")
        
        movie_data = load_movie_bertopic_data()
        if movie_data is None:
            st.error("⚠️ 영화 BERTopic 데이터를 찾을 수 없습니다.")
        else:
            render_bertopic_section(movie_data, content_type="movie", content_type_label="영화", key_prefix="movie")
    
    with movie_tab3:
        st.markdown("***흥행작: hit_score 상위 20% / 비흥행작: hit_score 하위 20%***")
        st.markdown("---")
        
        movie_data = load_movie_bertopic_data()
        if movie_data is None:
            st.error("⚠️ 영화 BERTopic 데이터를 찾을 수 없습니다.")
        else:
            render_representative_works(movie_data, content_type="movie", content_type_label="영화", key_prefix="movie")

# 드라마 탭
with main_tab2:
    st.header("📺 드라마 줄거리 분석")
    
    drama_tab1, drama_tab2, drama_tab3 = st.tabs(["📊 TF-IDF 분석", "🎯 BERTopic 클러스터", "🎬 대표 작품"])
    
    with drama_tab1:
        st.subheader("📺 드라마 TF-IDF 키워드")
        st.markdown("※ 단어 빈도가 높을수록 크게 표현됩니다. 상위 30개 키워드만 표시됩니다.")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 흥행작 키워드")
            df_hit = load_tfidf_keywords("drama", "hit")
            img = generate_wordcloud_image(df_hit, color_palette=["#d73027", "#fc8d59", "#f781bf"], font_path=FONT_PATH)
            st.image(img)
        with col2:
            st.markdown("### 🔴 비흥행작 키워드")
            df_flop = load_tfidf_keywords("drama", "flop")
            img = generate_wordcloud_image(df_flop, color_palette=["#4d4d4d", "#91bfdb", "#c2a5cf"], font_path=FONT_PATH)
            st.image(img)
        
    with drama_tab2:
        st.markdown("***흥행작: hit_score 상위 20% / 비흥행작: hit_score 하위 20%***")
        st.markdown("---")
        
        drama_data = load_drama_bertopic_data()
        if drama_data is None:
            st.error("⚠️ 드라마 BERTopic 데이터를 찾을 수 없습니다.")
        else:
            render_bertopic_section(drama_data, content_type="drama", content_type_label="드라마", key_prefix="drama")
    
    with drama_tab3:
        st.markdown("***흥행작: hit_score 상위 20% / 비흥행작: hit_score 하위 20%***")
        st.markdown("---")
        
        drama_data = load_drama_bertopic_data()
        if drama_data is None:
            st.error("⚠️ 드라마 BERTopic 데이터를 찾을 수 없습니다.")
        else:
            render_representative_works(drama_data, content_type="drama", content_type_label="드라마", key_prefix="drama")