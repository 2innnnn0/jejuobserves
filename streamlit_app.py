import streamlit as st
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

# Streamlit Title
st.title("Jeju Satellite Data NDVI Calculation")

# 제주 위성 데이터 폴더 경로
data_folder = "data/"

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

# 데이터 로드
st.subheader("Loading Satellite Data...")

nir_band, nir_transform = load_tiff(data_folder + "PN.tif")  # NIR 밴드 (근적외선)
red_band, red_transform = load_tiff(data_folder + "PR.tif")  # RED 밴드

# NDVI 계산
ndvi = calculate_ndvi(nir_band, red_band)

# NDVI 결과 시각화
st.subheader("NDVI Result")
fig, ax = plt.subplots()
cax = ax.imshow(ndvi, cmap='RdYlGn')  # NDVI 결과를 색상으로 표현
ax.set_title("NDVI Map")
fig.colorbar(cax, ax=ax, orientation='vertical', label='NDVI')
st.pyplot(fig)

# 썸네일 이미지 표시
st.subheader("Thumbnail (BR.jpg)")
st.image(data_folder + "br.jpg", caption="Jeju Satellite Thumbnail")

# NDVI 저장 옵션 제공
if st.button("Save NDVI Result"):
    ndvi_file_path = data_folder + "NDVI_result.tif"
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