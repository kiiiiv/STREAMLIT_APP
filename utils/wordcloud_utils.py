from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
import io
from PIL import Image
import hashlib
import streamlit as st


@st.cache_data(show_spinner=False)
def generate_wordcloud_image(df, color_palette, font_path):
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

    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=800,
        height=500,
        max_words=60,          # ⬅️ 중요 (기존 80 → 60)
        prefer_horizontal=0.9,
        collocations=False,    # ⬅️ BIG 효과
        color_func=color_func
    ).generate_from_frequencies(freq)

    img = wc.to_image()
    return img


