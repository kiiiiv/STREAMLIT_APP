# utils/loader.py
# 1. 캐시를 데이터 단위로 관리하려고 -> 파일은 한 번만 읽고 재사용
# 2. 데이터 계약서 역할
# 3. 페이지 코드 쉽게 읽을려고
# 4. 협업에서 사고 안 나게 방지

import pandas as pd
import streamlit as st


# ========== Page 1 (Overview) ==========


# ========== Page 2 (Synopsis - TF-IDF) ==========
# ---------- TF-IDF (Synopsis) ----------

@st.cache_data
def load_tfidf_keywords(content_type, category):
    """
    content_type: 'movie' | 'drama'
    category: 'hit' | 'flop'
    
    Delta 키워드 CSV에서 direction에 따라 필터링
    """
    # Delta CSV 파일 로드
    df = pd.read_csv(f"data/02_synopsis/{content_type}/tfidf_delta_keywords.csv")
    
    # category에 따라 필터링
    if category == 'hit':
        df_filtered = df[df['direction'] == 'hit+'].copy()
        df_filtered = df_filtered.rename(columns={'delta_value': 'score'})
    else:  # flop
        df_filtered = df[df['direction'] == 'nonhit+'].copy()
        df_filtered = df_filtered.rename(columns={'delta_value': 'score'})
    
    # keyword, score 컬럼만 반환
    return df_filtered[['keyword', 'score']].reset_index(drop=True)


# ========== Page 2/3 (Synopsis - BERTopic) ==========

# ---------- 드라마 BERTopic 데이터 ----------
@st.cache_data
def load_bertopic_drama_hit_map():
    """드라마 흥행작 UMAP 좌표 + 토픽/클러스터 정보"""
    return pd.read_csv("data/02_synopsis/drama/hit_umap_map.csv")


@st.cache_data
def load_bertopic_drama_flop_map():
    """드라마 비흥행작 UMAP 좌표 + 토픽/클러스터 정보"""
    return pd.read_csv("data/02_synopsis/drama/flop_umap_map.csv")


@st.cache_data
def load_bertopic_drama_hit_clusters():
    """드라마 흥행작 클러스터 정보"""
    return pd.read_csv("data/02_synopsis/drama/hit_clusters.csv")


@st.cache_data
def load_bertopic_drama_flop_clusters():
    """드라마 비흥행작 클러스터 정보"""
    return pd.read_csv("data/02_synopsis/drama/flop_clusters.csv")


@st.cache_data
def load_bertopic_drama_hit_topic_info():
    """드라마 흥행작 토픽 상세 정보 (대표 드라마 포함)"""
    return pd.read_csv("data/02_synopsis/drama/hit_topic_info.csv")


@st.cache_data
def load_bertopic_drama_flop_topic_info():
    """드라마 비흥행작 토픽 상세 정보"""
    return pd.read_csv("data/02_synopsis/drama/flop_topic_info.csv")


@st.cache_data
def load_bertopic_drama_keyword_comparison():
    """드라마 흥행/비흥행 키워드 비교"""
    return pd.read_csv("data/02_synopsis/drama/keyword_comparison.csv")


# ---------- 영화 BERTopic 데이터 ----------
@st.cache_data
def load_bertopic_movie_hit_map():
    """영화 흥행작 UMAP 좌표 + 토픽/클러스터 정보"""
    return pd.read_csv("data/02_synopsis/movie/hit_umap_map.csv")


@st.cache_data
def load_bertopic_movie_flop_map():
    """영화 비흥행작 UMAP 좌표 + 토픽/클러스터 정보"""
    return pd.read_csv("data/02_synopsis/movie/flop_umap_map.csv")


@st.cache_data
def load_bertopic_movie_hit_clusters():
    """영화 흥행작 클러스터 정보"""
    return pd.read_csv("data/02_synopsis/movie/hit_clusters.csv")


@st.cache_data
def load_bertopic_movie_flop_clusters():
    """영화 비흥행작 클러스터 정보"""
    return pd.read_csv("data/02_synopsis/movie/flop_clusters.csv")


@st.cache_data
def load_bertopic_movie_hit_topic_info():
    """영화 흥행작 토픽 상세 정보"""
    return pd.read_csv("data/02_synopsis/movie/hit_topic_info.csv")


@st.cache_data
def load_bertopic_movie_flop_topic_info():
    """영화 비흥행작 토픽 상세 정보"""
    return pd.read_csv("data/02_synopsis/movie/flop_topic_info.csv")


@st.cache_data
def load_bertopic_movie_keyword_comparison():
    """영화 흥행/비흥행 키워드 비교"""
    return pd.read_csv("data/02_synopsis/movie/keyword_comparison.csv")


# ========== Page 4 (Review Analysis) ==========
@st.cache_data 
def load_review_tfidf_keywords():
    """Review TF-IDF Keywords"""
    return pd.read_parquet("data/03_review/review_tfidf_keywords_all.parquet")


@st.cache_data
def load_review_topic_summary():
    """Review Topic Summary (전체)"""
    return pd.read_parquet("data/03_review/review_topic_summary_30w_all.parquet")


@st.cache_data
def load_review_topic_summary_by_type():
    """Review Topic Summary (타입별: Movie / TV)"""
    return pd.read_parquet("data/03_review/review_topic_summary_30w_by_type.parquet")


# ========== Page 5 (Prediction) ==========