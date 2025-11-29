import streamlit as st
import webcolors
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_utils import get_complementary_color

# ----------------------------
# CSS/HTML 스타일 정의
# ----------------------------
def get_color_box_html(hex_code, label):
    """색상 코드와 이름을 표시하는 작은 HTML 상자를 생성합니다."""
    return f"""
    <div style="
        background-color: {hex_code};
        color: {'#FFFFFF' if is_light_color(hex_code) else '#000000'};
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px #888888;
        font-weight: bold;
    ">
        {label}<br>{hex_code.upper()}
    </div>
    """

def is_light_color(hex_code):
    """색상의 밝기를 판단하여 텍스트 색상을 결정합니다 (명암 대비)."""
    if hex_code.startswith('#'):
        hex_code = hex_code[1:]
    
    # HEX를 RGB로 변환 (0-255)
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    
    # 휘도 계산 (Luminance, ITU-R BT.709 기준)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    
    return luminance > 0.55 # 0.55를 기준으로 밝거나 어둡다고 판단

# ----------------------------
# 색상 계산 로직
# ----------------------------
def get_complementary_hex(hex_code):
    """HEX 코드를 입력받아 보색의 HEX 코드를 반환합니다."""
    
    # 1. webcolors로 HEX를 RGB 튜플로 변환 (0-255)
    rgb_255 = webcolors.hex_to_rgb(hex_code)
    
    # 2. sRGBColor 객체 생성 (colormath는 0-1.0 또는 0-255를 사용)
    rgb_obj = sRGBColor(rgb_255.red, rgb_255.green, rgb_255.blue, is_int=True)
    
    # 3. 보색 계산
    # colormath의 get_complementary_color는 RGB, HSV, Lab 등 다양한 색 공간에서 보색을 찾음
    complementary_obj = get_complementary_color(rgb_obj)
    
    # 4. 결과를 sRGB (HEX 표현 가능 형식)로 변환
    # LabColor로 변환 후 다시 sRGB로 오는 것이 더 정확한 색 공간에서의 '보색'이 될 수 있음
    lab_color = convert_color(rgb_obj, LabColor)
    complementary_lab = get_complementary_color(lab_color)
    
    # 결과 Lab 색상을 다시 sRGB (0-255)로 변환
    complementary_rgb = convert_color(complementary_lab, sRGBColor)
    
    # 5. HEX 코드로 최종 변환
    comp_hex = webcolors.rgb_to_hex(
        (int(complementary_rgb.rgb_r), int(complementary_rgb.rgb_g), int(complementary_rgb.rgb_b))
    )
    
    return comp_hex

# ----------------------------
# Streamlit 앱
# ----------------------------
def main():
    st.set_page_config(page_title="색상 조화 추천기", layout="centered")
    st.title("🌈 색상 조화 추천기")
    st.markdown("---")
    
    st.markdown("""
        **HEX 코드**를 입력하여 그 색상과 **보색(Complementary Color)** 관계에 있는 색상을 확인하세요.
        (예: `#4682B4` - 스틸 블루, `#FF5733` - 주황)
    """)
    
    # 1. 색상 입력 위젯
    input_hex = st.text_input(
        "HEX 코드 입력 (# 포함):", 
        value="#4682B4", # 기본값
        max_chars=7
    )

    # 입력 정리 및 유효성 검사
    clean_hex = input_hex.strip().upper()
    
    # 2. 버튼 클릭 시 로직 실행
    if st.button("✨ 색상 분석 및 추천"):
        if clean_hex.startswith('#') and len(clean_hex) == 7:
            try:
                # webcolors를 통해 유효한 HEX 코드인지 확인
                webcolors.hex_to_rgb(clean_hex) 
                
                st.subheader("결과")
                
                # 3. 보색 계산
                comp_hex = get_complementary_hex(clean_hex)
                
                # 4. 시각화 (두 열 사용)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🎨 입력 색상")
                    st.markdown(get_color_box_html(clean_hex, "Your Color"), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 🔄 보색 (Complementary)")
                    st.markdown(get_color_box_html(comp_hex, "Complementary"), unsafe_allow_html=True)
                    
                st.markdown("---")
                st.success(f"입력 색상 **{clean_hex}**의 보색은 **{comp_hex}**입니다.")
                
            except ValueError:
                st.error("⚠️ 유효하지 않은 HEX 코드 형식입니다. `#RRGGBB` 형식으로 입력해 주세요.")
        else:
            st.warning("HEX 코드는 '#'으로 시작하는 7자리 문자열이어야 합니다 (예: `#AABBCC`).")

if __name__ == "__main__":
    main()
