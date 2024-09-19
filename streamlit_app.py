import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# 이미지 자르기
def main():
    st.title("Jeju Satellite Image Cropper")

    # 이미지 로드
    img_file = 'data/br.jpg'  # 업로드된 파일 경로
    img = Image.open(img_file)
    
    # 이미지 자르기 도구 제공
    cropped_img = st_cropper(img, realtime_update=True, box_color='#0000FF', aspect_ratio=None)
    
    st.subheader("Cropped Image Preview")
    
    # 잘린 이미지 미리보기
    if cropped_img:
        st.image(cropped_img, caption="Cropped Image", use_column_width=True)

    # 다른 처리를 위한 이미지를 numpy로 변환 (원하는 추가 처리를 할 수 있도록)
    np_img = np.array(cropped_img)

    # 추가 처리: 예를 들어, NDVI 계산 등
    # 추가 코드를 여기서 적용할 수 있음

if __name__ == "__main__":
    main()