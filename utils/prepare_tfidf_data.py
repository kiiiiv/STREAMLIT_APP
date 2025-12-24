"""
TF-IDF Delta 키워드 데이터 준비 스크립트

"""

import os
import shutil

# 경로 설정 (utils 폴더 기준)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # utils 폴더
STREAMLIT_DIR = os.path.dirname(SCRIPT_DIR)  # 스트림릿 폴더
BASE_DIR = os.path.dirname(STREAMLIT_DIR)  # 최종데이터셋 폴더

# 소스 파일
DRAMA_DELTA_SRC = os.path.join(BASE_DIR, "TF-IDF_Drama", "04_keywords_delta_len150_p20.csv")
MOVIE_DELTA_SRC = os.path.join(BASE_DIR, "TF-IDF_Movie", "04_keywords_delta_len150_p20.csv")

# 대상 파일 (파일명 그대로 유지)
DRAMA_DELTA_DST = os.path.join(STREAMLIT_DIR, "data", "02_synopsis", "drama", "tfidf_delta_keywords.csv")
MOVIE_DELTA_DST = os.path.join(STREAMLIT_DIR, "data", "02_synopsis", "movie", "tfidf_delta_keywords.csv")

# 디렉토리 생성
os.makedirs(os.path.dirname(DRAMA_DELTA_DST), exist_ok=True)
os.makedirs(os.path.dirname(MOVIE_DELTA_DST), exist_ok=True)

# 파일 복사
print("=" * 70)
print("📁 TF-IDF Delta 키워드 데이터 준비")
print("=" * 70)
print(f"📂 스크립트 위치: {SCRIPT_DIR}")
print(f"📂 스트림릿 폴더: {STREAMLIT_DIR}")
print(f"📂 데이터 폴더: {BASE_DIR}")
print()

if os.path.exists(DRAMA_DELTA_SRC):
    shutil.copy2(DRAMA_DELTA_SRC, DRAMA_DELTA_DST)
    print(f"✓ 드라마 Delta 복사 완료")
    print(f"  FROM: {DRAMA_DELTA_SRC}")
    print(f"  TO:   {DRAMA_DELTA_DST}")
else:
    print(f"❌ 드라마 Delta 파일 없음: {DRAMA_DELTA_SRC}")

print()

if os.path.exists(MOVIE_DELTA_SRC):
    shutil.copy2(MOVIE_DELTA_SRC, MOVIE_DELTA_DST)
    print(f"✓ 영화 Delta 복사 완료")
    print(f"  FROM: {MOVIE_DELTA_SRC}")
    print(f"  TO:   {MOVIE_DELTA_DST}")
else:
    print(f"❌ 영화 Delta 파일 없음: {MOVIE_DELTA_SRC}")

print()
print("=" * 70)
print("✅ 데이터 준비 완료!")
print("=" * 70)
print("\n다음 명령어로 Streamlit 실행:")
print(f"cd {STREAMLIT_DIR}")
print("streamlit run app.py")
