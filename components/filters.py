import streamlit as st

def sidebar_filters():
    """
    대시보드 전 페이지에서 공통으로 사용하는 사이드바 필터
    반환값은 dict 형태
    """

    st.sidebar.header("🔎 필터")

    content_type = st.sidebar.radio(
        "Content Type",
        ["영화", "드라마"],
        horizontal=True
    )

    # 내부 로직에서 쓰기 좋게 소문자로 변환
    content_type = content_type.lower()

    return {
        "content_type": content_type
    }
