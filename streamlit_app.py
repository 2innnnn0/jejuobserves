import numpy as np
import matplotlib.pyplot as plt
import rasterio

# NDVI 계산 함수
def calculate_ndvi(nir_band, red_band):
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    return ndvi

# 위성 이미지 파일 경로 (예시 파일 경로)
red_band_path = 'imagesets/Clipping_16/K3A_20231031050356_47479_00072313_L1R_PS-011/K3A_20231031050356_47479_00072313_L1R_PR.tif'
nir_band_path = 'imagesets/Clipping_16/K3A_20231031050356_47479_00072313_L1R_PS-011/K3A_20231031050356_47479_00072313_L1R_PN.tif'

# Red 밴드와 NIR 밴드 읽기 및 크기 확인
with rasterio.open(red_band_path) as red_src:
    red_band = red_src.read(1).astype(float)
    width = red_src.width
    height = red_src.height
    print(f"Red band image size: {width} x {height}")

with rasterio.open(nir_band_path) as nir_src:
    nir_band = nir_src.read(1).astype(float)
    nir_width = nir_src.width
    nir_height = nir_src.height
    print(f"NIR band image size: {nir_width} x {nir_height}")

# 원하는 영역 지정 (예: x_min, x_max, y_min, y_max)
x_min, x_max = 5000, 10000  # 가로 방향 범위
y_min, y_max = 5000, 10000  # 세로 방향 범위

# 선택한 영역에 대해 NDVI 계산
red_band_cropped = red_band[y_min:y_max, x_min:x_max]
nir_band_cropped = nir_band[y_min:y_max, x_min:x_max]

ndvi_cropped = calculate_ndvi(nir_band_cropped, red_band_cropped)

# 선택한 영역의 NDVI 시각화
plt.figure(figsize=(10, 10))
plt.imshow(ndvi_cropped, cmap='RdYlGn')
plt.colorbar()
plt.title('NDVI (Cropped Area)')
plt.show()