import rasterio
from rasterio.windows import Window
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# TIF 이미지 자르기 함수 (위경도 관련 내용 삭제)
def cut_satellite_image(tif_file, width=5000, height=5000):
    with rasterio.open(tif_file) as src:
        # 이미지 중심을 기준으로 가로 세로 자르기
        center_col = src.width // 2
        center_row = src.height // 2
        window = Window(
            center_col - width // 2, center_row - height // 2,
            width, height
        )
        image_data = src.read(window=window)
    
    return image_data

# 이미지 스케일링 함수 (0~255 범위로 변환)
def scale_image(image_data):
    image_min = image_data.min()
    image_max = image_data.max()
    
    # 데이터가 0~255 범위 안에 있도록 스케일링
    scaled_image = (255 * (image_data - image_min) / (image_max - image_min)).astype(np.uint8)
    return scaled_image

# NDVI 계산 함수
def calculate_ndvi(nir_band, red_band):
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    return ndvi

# Streamlit UI 구현
def main():
    st.title("Jeju Satellite Data Viewer")
    
    # TIF 파일 경로 지정
    br_file = 'data/br.jpg'
    pb_file = 'data/PB.tif'
    pg_file = 'data/PG.tif'
    pn_file = 'data/PN.tif'
    pr_file = 'data/PR.tif'
    
    # TIF 파일 자르기 (중앙 부분 1024x1024 크기로 자름)
    br_image = cut_satellite_image(br_file)
    pb_image = cut_satellite_image(pb_file)
    pg_image = cut_satellite_image(pg_file)
    pn_image = cut_satellite_image(pn_file)
    pr_image = cut_satellite_image(pr_file)
    
    # 이미지 스케일링
    br_image_scaled = scale_image(br_image)
    pb_image_scaled = scale_image(pb_image)
    pg_image_scaled = scale_image(pg_image)
    pn_image_scaled = scale_image(pn_image)
    pr_image_scaled = scale_image(pr_image)
    
    # NDVI 계산 (PR은 적외선, PB는 적색)
    ndvi = calculate_ndvi(pr_image[0], pb_image[0])
    
    # 이미지 미리보기
    st.subheader("Satellite Images Preview")
    st.image(br_image.transpose(1, 2, 0), caption="BR Image (Thumbnail)", use_column_width=True)
    st.image(br_image_scaled.transpose(1, 2, 0), caption="BR Image (Thumbnail)", use_column_width=True)
    # st.image(pb_image_scaled.transpose(1, 2, 0), caption="PB Image", use_column_width=True)
    # st.image(pg_image_scaled.transpose(1, 2, 0), caption="PG Image", use_column_width=True)
    # st.image(pn_image_scaled.transpose(1, 2, 0), caption="PN Image", use_column_width=True)
    # st.image(pr_image_scaled.transpose(1, 2, 0), caption="PR Image", use_column_width=True)
    
    # NDVI 결과 미리보기
    st.subheader("NDVI Preview")
    plt.imshow(ndvi, cmap='RdYlGn')
    plt.colorbar()
    st.pyplot()

if __name__ == "__main__":
    main()