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
    time.sleep(2)
    # NDVI 결과 시각화
    plt.figure(figsize=(10, 10))
    plt.imshow(ndvi_result, cmap='RdYlGn')
    plt.colorbar(label='NDVI Value')
    plt.title('NDVI Result')

    # 이미지를 바이트 스트림으로 변환
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=30)
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
                    "content": """
                            올린 이미지들은 같은 장소의 위성이미지야. 하나는 그냥 RGB, 하나는 NVDI로 계산한 이미지야.
                            먼저 이미지를 설명해주세요. 그 후 주어진 NDVI 데이터를 기반으로 농지 활용 상태를 분류해 주세요. 
                            1. 해당 지역이 농지로 잘 활용되고 있을 확률을 계산해 주세요.
                            2. 농지로 잘 활용되고 있는지(잘 활용됨 / 잘 활용되지 않음) 분류하고, 각 범주에 대한 신뢰도(확률)도 제공해 주세요.

                            출력 포맷은 다음과 같습니다.
                            1. 요약
                            - 간단명료하게 테이블 형태로 한눈에 이해할 수 있게 작성해주세요.
                            - 농지 활용 상태, 활용 확률%, 근거
                            2. 상세 설명
                            - 초보자를 위해 NVDI를 해석하는 방법 안내
                            - 그 외 확률값에 따른 상세 설명 

                            모든 답은 한글로 해주세요.
                            """
                },
                {
                    "role": "user",
                    "content": f"data:image/png;base64,{image_base64}"
                }
            ],
            "max_tokens": 1000
        }

        try:
            # OpenAI API 요청 전송
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_json = response.json()

            # 'choices' 키가 있는지 확인하고 처리
            if 'choices' in response_json:
                result = response_json['choices'][0]['message']['content']
            else:
                # 로그 출력 및 예외 발생
                st.error(f"OpenAI API 응답에 'choices' 키가 없습니다. 응답 내용: {json.dumps(response_json, indent=2)}")
                raise KeyError("'choices' 키가 OpenAI API 응답에 존재하지 않습니다.")
        
        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 오류가 발생했습니다: {e}")
            st.error(f"응답 내용: {response.text}")
            raise
        except KeyError as e:
            st.error(f"응답 데이터 처리 중 오류가 발생했습니다: {e}")
            raise
    
    st.success("AI 인식이 끝났습니다")
    return result