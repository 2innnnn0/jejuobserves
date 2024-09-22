import time
import requests
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64


# OpenAI API 키 설정 (환경 변수로 설정하거나 여기에 직접 추가)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# NDVI 결과 시각화 함수 (“메시지가 231,331개의 토큰을 초과했다”는 경고가 있습니다. OpenAI GPT 모델에는 최대 토큰 길이 제한이 있으며, 이 제한을 초과하는 데이터는 처리할 수 없습니다. 이 문제를 해결하려면 전송하는 메시지 크기를 줄여야 합니다.)
def visualize_ndvi(ndvi_result):
    # NDVI 결과 시각화
    plt.figure(figsize=(10, 10))
    plt.imshow(ndvi_result, cmap='RdYlGn')
    plt.colorbar(label='NDVI Value')
    plt.title('NDVI Result')

    # 이미지를 바이트 스트림으로 변환
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=50)
    buf.seek(0)
    
    # 바이트 스트림을 base64 인코딩
    # image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return image_base64


# OpenAI API 호출 함수
def analyze_ndvi(ndvi_result):
    with st.spinner("AI가 농지를 검토하고 있어요! 🥕"):
        time.sleep(2)  # 인코딩 작업 (모의)
        
        # NDVI 결과 시각화 후 base64로 변환
        image_base64 = visualize_ndvi(ndvi_result)
        
        # OpenAI API 헤더 및 페이로드 설정
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # OpenAI API에 보낼 페이로드 (NDVI 시각화 이미지 포함)
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": "주어진 NDVI 데이터를 기반으로 농지 활용 상태를 분류해 주세요."
                },
                {
                    "role": "user",
                    "content": f"data:image/png;base64,{image_base64}"
                }
            ],
            "max_tokens": 1000
        }

        # OpenAI API 요청 전송
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        # API 응답 처리
        result = response.json()['choices'][0]['message']['content']
    
    st.success("AI 인식이 끝났습니다")
    return result