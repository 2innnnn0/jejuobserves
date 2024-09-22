import time
import requests
import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import numpy as np
import os
import json

# OpenAI API 키 설정 (환경 변수로 설정하거나 여기에 직접 추가)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# OpenAI API 호출 함수
def analyze_ndvi(ndvi_result):
    with st.spinner("AI가 농지를 검토하고 있어요! 🥕"):
        time.sleep(2)  # 인코딩 작업 (모의)
        # base64_image = encode_image(image)

        # OpenAI API 헤더 및 페이로드 설정
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # OpenAI API에 보낼 페이로드
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                            {"type": "text", "text": f"""
                                    주어진 NDVI 데이터를 기반으로 농지 활용 상태를 분류해 주세요.
                                    NDVI 값: {ndvi_result.tolist()}
                                    """}
                            # {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
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