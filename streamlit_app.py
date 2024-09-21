import streamlit as st
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance, ImageFile
import os
import time
import requests
import base64
from io import BytesIO
import json
import boto3
from rasterio.io import MemoryFile

# OpenAI API 키 설정 (환경 변수로 설정하거나 여기에 직접 추가)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Streamlit secrets를 이용하여 자격 증명 설정
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

# boto3 클라이언트를 자격 증명과 함께 생성
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# S3에서 파일 읽는 함수
def read_tif_from_s3(bucket_name, key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_data = response['Body'].read()
    return file_data

    with MemoryFile(file_data) as memfile:
        with memfile.open() as dataset:
            return dataset.read(1), dataset.transform

# S3 버킷 정보 (S3)
# bucket_name = 'datapopcorn'
# nir_key = 'tif/K3A_20230516044713_44934_00084310_L1R_PN.tif'  # S3에 있는 NIR 파일 경로
# red_key = 'tif/K3A_20230516044713_44934_00084310_L1R_PR.tif'  # S3에 있는 RED 파일 경로

# 전체 NIR 및 RED 파일 경로 (로컬)
nir_file = "data/PN.tif"
red_file = "data/PR.tif"
thumbnail_path = "data/adjusted_image.jpg"


# OpenAI API 호출 함수
def analyze_ndvi(ndvi_result):
    with st.spinner("AI가 농지를 검토하고 있어요! 🥕"):
        time.sleep(2)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                    주어진 NDVI 데이터를 기반으로 농지 활용 상태를 분류해 주세요.
                    NDVI 값: {ndvi_result.tolist()}
                    """
                }
            ],
            "max_tokens": 1000
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()  # 에러 발생 시 예외 처리
            result = response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            st.error(f"API 요청에 실패했습니다: {e}")
            return None

    st.success("AI 인식이 끝났습니다")
    return result

# DecompressionBombWarning을 방지하기 위해 사이즈 제한을 제거
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Streamlit Wide Mode 설정
st.set_page_config(layout="wide")

# Streamlit Title
st.title("Jeju Satellite Data NDVI Calculation")

# 파일 읽기 함수 정의
def load_tiff(file_path):
    with rasterio.open(file_path) as src:
        return src.read(1), src.transform, src.width, src.height

# NDVI 계산 함수 정의
def calculate_ndvi(nir_band, red_band):
    nir = nir_band.astype(float)
    red = red_band.astype(float)
    ndvi = (nir - red) / (nir + red)
    return np.clip(ndvi, -1, 1)  # NDVI 범위를 [-1, 1]로 클립

# 전체 NIR 및 RED 밴드 로드
st.subheader("Loading Full NIR and RED Bands")
nir_band, nir_transform, nir_width, nir_height = load_tiff(nir_file)  # NIR 밴드
red_band, red_transform, red_width, red_height = load_tiff(red_file)  # RED 밴드

# NIR 밴드와 RED 밴드 파일을 S3에서 읽어옴
# nir_band, nir_transform = read_tif_from_s3(bucket_name, nir_key)
# red_band, red_transform = read_tif_from_s3(bucket_name, red_key)


# 타일 수를 슬라이더로 선택
st.subheader("Select the number of tiles")
num_tiles = st.slider("Number of tiles per row and column", min_value=2, max_value=16, value=8)

# 이미지 크기 및 타일 크기 계산
tile_width = nir_width // num_tiles
tile_height = nir_height // num_tiles

# 타일 선택 위젯
tile_options = [(row, col) for row in range(num_tiles) for col in range(num_tiles)]
selected_tile = st.selectbox("Select a Tile", tile_options)

# 선택된 타일의 행, 열 번호 추출
tile_row, tile_col = selected_tile

# 좌우 배치 - 썸네일과 NDVI 결과
col1, col2 = st.columns(2)

# 왼쪽: 썸네일 이미지 표시 (타일에 맞게 부분 표시)
with col1:
    st.subheader("Thumbnail (BR.jpg) for Selected Tile")
    
    # BR.jpg 파일 열기
    img = Image.open(thumbnail_path)
    
    # 이미지 크기 계산
    img_width, img_height = img.size
    tile_width_thumb = img_width // num_tiles
    tile_height_thumb = img_height // num_tiles
    
    # 선택된 타일에 맞는 부분 자르기
    left = tile_col * tile_width_thumb
    upper = tile_row * tile_height_thumb
    right = left + tile_width_thumb
    lower = upper + tile_height_thumb
    cropped_img = img.crop((left, upper, right, lower))
    
    # 썸네일 타일 이미지 표시
    st.image(cropped_img, caption=f"BR.jpg Tile ({tile_row}, {tile_col})", use_column_width=True)

# 오른쪽: NDVI 결과 시각화 (X,Y축과 범례 제거)
with col2:
    st.subheader(f"NDVI Result for Tile ({tile_row}, {tile_col})")
    fig, ax = plt.subplots()

    # 선택된 타일에 해당하는 NDVI 부분 가져오기
    ndvi_tile = ndvi_result[
        tile_row * tile_height:(tile_row + 1) * tile_height,
        tile_col * tile_width:(tile_col + 1) * tile_width
    ]

    # NDVI 결과 시각화 (모든 테마 제거)
    cax = ax.imshow(ndvi_tile, cmap='RdYlGn')
    
    # X축, Y축, 범례, 틱 제거
    ax.axis('off')
    
    # 플롯 그리기
    st.pyplot(fig)

# AI 분석하기
if st.button("AI 분석하기"):
    # AI 분석 호출
    ai_result = analyze_ndvi(ndvi_result)

    # AI 결과 출력
    st.subheader("AI Analysis Result")
    st.write(ai_result)