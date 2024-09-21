import streamlit as st
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
from PIL import ImageFile
import os

# DecompressionBombWarning을 방지하기 위해 사이즈 제한을 제거
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Streamlit Wide Mode 설정
st.set_page_config(layout="wide")

# Streamlit Title
st.title("Jeju Satellite Data NDVI Calculation with Tiles")

# 제주 위성 데이터 타일 경로 및 썸네일 경로
tiles_folder = "data/tiles/"
thumbnail_path = "data/adjusted_image.jpg"

# 타일 목록 가져오기
tile_files = [f for f in os.listdir(tiles_folder) if f.endswith(".tif") and "PN_tile" in f]

# 타일 파일 이름에서 숫자를 추출하여 오름차순 정렬
tile_files.sort(key=lambda x: (int(x.split('_')[-2]), int(x.split('_')[-1].replace('.tif', ''))))

# 타일 선택 위젯
selected_tile = st.selectbox("Select a Tile", tile_files)


# 선택된 타일의 행, 열 번호 추출
try:
    # 파일 이름에서 확장자를 제거하고, 행과 열 번호 추출
    tile_row, tile_col = map(int, selected_tile.replace('.tif', '').split('_')[-2:])
except ValueError as e:
    st.error(f"Error parsing tile file: {e}")
    st.stop()

# 파일 읽기 함수 정의
def load_tiff(file_path):
    with rasterio.open(file_path) as src:
        return src.read(1), src.transform

# NDVI 계산 함수 정의
def calculate_ndvi(nir_band, red_band):
    nir = nir_band.astype(float)
    red = red_band.astype(float)
    ndvi = (nir - red) / (nir + red)
    return np.clip(ndvi, -1, 1)  # NDVI 범위를 [-1, 1]로 클립

# 선택된 타일 로드
st.subheader(f"Loading Selected Tile: {selected_tile}")
nir_band, nir_transform = load_tiff(os.path.join(tiles_folder, selected_tile))  # NIR 밴드 타일

# 같은 타일 이름 패턴을 가진 적색(RED) 밴드 로드
red_tile = selected_tile.replace("PN_tile", "PR_tile")
red_band, red_transform = load_tiff(os.path.join(tiles_folder, red_tile))  # RED 밴드 타일

# NDVI 계산
ndvi = calculate_ndvi(nir_band, red_band)

# 좌우 배치 - 썸네일과 NDVI 결과
col1, col2 = st.columns(2)

# 왼쪽: 썸네일 이미지 표시 (타일에 맞게 부분 표시)
with col1:
    st.subheader("Thumbnail (BR.jpg) for Selected Tile")
    
    # BR.jpg 파일 열기
    img = Image.open(thumbnail_path)
    
    # 이미지 크기 및 타일 크기 계산 (8x8 타일 기준)
    img_width, img_height = img.size
    tile_width = img_width // 8
    tile_height = img_height // 8
    
    # 선택된 타일에 맞는 부분 자르기
    left = tile_col * tile_width
    upper = tile_row * tile_height
    right = left + tile_width
    lower = upper + tile_height
    cropped_img = img.crop((left, upper, right, lower))
    
    # 썸네일 타일 이미지 표시
    st.image(cropped_img, caption=f"BR.jpg Tile ({tile_row}, {tile_col})", use_column_width=True)

# 오른쪽: NDVI 결과 시각화 (X,Y축과 범례 제거)
with col2:
    st.subheader(f"NDVI Result for {selected_tile}")
    fig, ax = plt.subplots()
    
    # NDVI 결과 시각화 (모든 테마 제거)
    cax = ax.imshow(ndvi, cmap='RdYlGn')
    
    # X축, Y축, 범례, 틱 제거
    ax.axis('off')
    
    # 플롯 그리기
    st.pyplot(fig)

# NDVI 저장 옵션 제공
if st.button("Save NDVI Result"):
    ndvi_file_path = tiles_folder + selected_tile.replace("PN_tile", "NDVI_tile")
    with rasterio.open(
        ndvi_file_path,
        'w',
        driver='GTiff',
        height=nir_band.shape[0],
        width=nir_band.shape[1],
        count=1,
        dtype=rasterio.float32,
        crs='+proj=latlong',
        transform=nir_transform,
    ) as dst:
        dst.write(ndvi, 1)
    st.success(f"NDVI result saved to {ndvi_file_path}")