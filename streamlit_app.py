import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from openai import OpenAI
import time
import requests

# OpenAI API 키 설정 (환경 변수로 설정하거나 여기에 직접 추가)
OPENAI_API_KEY = '' # st.secrets["OPENAI_API_KEY"]

# NDVI 계산 함수
def calculate_ndvi(nir_band, red_band):
    # NDVI 공식: (NIR - Red) / (NIR + Red)
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    return ndvi

# OpenAI API 호출 함수
def analyze_ndvi(ndvi_result):
    with st.spinner("AI가 농지를 검토하고 있어요! 🥕"):
        time.sleep(2)  # 인코딩 작업 (모의)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"""
                        주어진 NDVI(정규화된 식생 지수) 데이터를 기반으로, 해당 위치가 농지로 잘 활용되고 있는지 분류해 주세요. NDVI 값이 높을수록(푸른색에 가까움) 해당 지역이 농지로 잘 활용되고 있으며, NDVI 값이 낮을수록(붉은색에 가까움) 농지로 잘 활용되지 않고 있음을 나타냅니다. 주어진 NDVI 배열을 참고하여:

                        1. 해당 지역이 농지로 잘 활용되고 있을 확률을 계산해 주세요.
                        2. 농지로 잘 활용되고 있는지(잘 활용됨 / 잘 활용되지 않음) 분류하고, 각 범주에 대한 신뢰도(확률)도 제공해 주세요.

                        NDVI 값은 -1에서 1 사이이며, 1에 가까울수록 식생이 무성하고, -1에 가까울수록 농지 활용이 적거나 불모지입니다.
                        """}
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        result = response.json()['choices'][0]['message']['content']
        
    st.success("AI 인식이 끝났습니다")
    return result

# 이미지 자르기
def main():
    st.title("Jeju Satellite Image Cropper with NDVI")

    # TIF 파일 경로 (PR: 적외선, PB: 적색)
    pn_file = 'output_images/PN_tile_5_5.tif' # 'data/PN.tif'  # 적색 밴드
    pr_file = 'output_images/PR_tile_5_5.tif' # data/PR.tif'  # 적외선 밴드

    # TIF 파일 불러오기
    with rasterio.open(pn_file) as src_pb:
        pb_image = src_pb.read(1)  # 적색 밴드 불러오기
        pb_width, pb_height = src_pb.width, src_pb.height  # pb.tif의 크기 얻기
    
    with rasterio.open(pr_file) as src_pr:
        pr_image = src_pr.read(1)  # 적외선 밴드 불러오기
        pr_width, pr_height = src_pr.width, src_pr.height  # pr.tif의 크기 얻기

    # Image 불러오기 (브라우저에서 표시할 jpg 이미지를 사용)
    img_file = 'data/br.jpg'  # 업로드된 파일 경로
    img = Image.open(img_file)
    br_width, br_height = img.size  # br.jpg의 크기 얻기
    
    # 이미지 자르기 도구 제공 (디폴트 사이즈 설정 가능)
    cropped_img = st_cropper(img, realtime_update=True, box_color='#0000FF', aspect_ratio=None)
    
    st.subheader("Cropped Image Preview")
    
    # 잘린 이미지 미리보기
    if cropped_img:
        st.image(cropped_img, caption="Cropped Image", use_column_width=True)

        # 잘린 이미지의 크기를 얻음
        crop_width, crop_height = cropped_img.size
        
        # 자르기 좌표 계산 (br.jpg 기준)
        crop_left, crop_top = (br_width - crop_width) // 2, (br_height - crop_height) // 2
        crop_right, crop_bottom = crop_left + crop_width, crop_top + crop_height
        
        # 자른 좌표를 pb.tif와 pr.tif의 비율에 맞춰 변환
        pb_left = int(crop_left * pb_width / br_width)
        pb_top = int(crop_top * pb_height / br_height)
        pb_right = int(crop_right * pb_width / br_width)
        pb_bottom = int(crop_bottom * pb_height / br_height)

        pr_left = int(crop_left * pr_width / br_width)
        pr_top = int(crop_top * pr_height / br_height)
        pr_right = int(crop_right * pr_width / br_width)
        pr_bottom = int(crop_bottom * pr_height / br_height)

        # 이미지 선택 영역에 맞는 부분을 자르기 (적외선 및 적색 밴드에서 같은 영역을 비율로 자름)
        cropped_pb = pb_image[pb_top:pb_bottom, pb_left:pb_right]
        cropped_pr = pr_image[pr_top:pr_bottom, pr_left:pr_right]

        # NDVI 계산
        ndvi_result = calculate_ndvi(cropped_pr, cropped_pb)

        # NDVI 시각화
        st.subheader("NDVI Preview")
        fig, ax = plt.subplots()
        cax = ax.imshow(ndvi_result, cmap='RdYlGn')
        fig.colorbar(cax)
        st.pyplot(fig)

        # OpenAI API로 NDVI 분석
        st.subheader("NDVI Analysis with OpenAI API")
        result = analyze_ndvi(ndvi_result)
        st.write(result)

if __name__ == "__main__":
    main()