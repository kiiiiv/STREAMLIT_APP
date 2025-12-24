from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
import io
from PIL import Image
import hashlib
import streamlit as st
import os


@st.cache_data(show_spinner=False)
def generate_wordcloud_image(df, color_palette, font_path=None):
    """워드클라우드 이미지 생성 - 폰트 경로 optional"""
    # score 컬럼 자동 인식
    if "score" in df.columns:
        score_col = "score"
    elif "hit_mean_tfidf" in df.columns:
        score_col = "hit_mean_tfidf"
    elif "nonhit_mean_tfidf" in df.columns:
        score_col = "nonhit_mean_tfidf"
    else:
        raise ValueError("TF-IDF score 컬럼 없음")

    freq = dict(zip(df["keyword"], df[score_col]))

    def color_func(*args, **kwargs):
        return random.choice(color_palette)

    # ✅ 폰트 경로 처리: 파일이 존재하면 사용, 아니면 기본 폰트
    wordcloud_params = {
        "background_color": "white",
        "width": 800,
        "height": 500,
        "max_words": 60,
        "prefer_horizontal": 0.9,
        "collocations": False,
        "color_func": color_func
    }
    
    # 폰트 파일이 존재하면 사용
    if font_path and os.path.exists(font_path):
        wordcloud_params["font_path"] = font_path
    
    wc = WordCloud(**wordcloud_params).generate_from_frequencies(freq)

    img = wc.to_image()
    return img

