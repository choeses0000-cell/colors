import streamlit as st
import webcolors
import colorsys # Python 표준 라이브러리

# ----------------------------
# CSS/HTML 스타일 및 유틸리티
# ----------------------------
def is_light_color(hex_code):
    """색상의 밝기를 판단하여 텍스트 색상을 결정합니다 (명암 대비)."""
    if hex_code.startswith('#'):
        hex_code = hex_code[1:]
    
    # HEX를 RGB로 변환 (0-255)
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    
    # 휘도 계산 (Luminance)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    
    return luminance > 0.55

def get_color_box_html(hex_code, label):
    """색상 코드와 이름을 표시하는 HTML 상자를 생성합니다."""
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

# ----------------------------
# 색상 조화 계산 로직 (HSV 기반)
# ----------------------------
def get_harmony_colors(hex_code, degrees: list[float]):
    """
    HEX 코드를 입력받아 지정된 각도(degrees)만큼 Hue를 이동하여
    새로운 HEX 코드 목록을 반환합니다.
    """
    # 1. HEX를 RGB (0-1.0)로 정규화
    rgb_255 = webcolors.hex_to_rgb(hex_code)
    r, g, b = rgb_255.red / 255.0, rgb_255.green / 255.0, rgb_255.blue / 255.0
    
    # 2. RGB를 HSV로 변환
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    harmony_hex_list = []
    
    for deg in degrees:
        # 3. Hue 값 계산: 각도를 0.0 ~ 1.0 범위로 변환 후 더하고 modulo 연산
        h_new = (h + (deg / 360.0)) % 1.0
        
        # 4. HSV를 다시 RGB (0-1.0)로 변환
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h_new, s, v)
        
        # 5. RGB (0-255)로 되돌림
        rgb_255_new = (
            int(round(r_new * 255)),
            int(round(g_new * 255)),
            int(round(b_new * 255))
        )
        
        # 6. 최종 HEX 코드로 변환
        harmony_hex = webcolors.rgb_to_hex(rgb_255_new)
        harmony_hex_list.append(harmony_hex)
        
    return harmony_hex_list

# 보색 계산 (Complementary: 180도)
def get_complementary_hex_simple(hex_code):
    return get_harmony_colors(hex_code, [180.0])[0]

# 유사색 계산 (Analogous: 양쪽으로 30도)
def get_analogous_hex(hex_code):
    return get_harmony_colors(hex_code, [-30.0, 30.0])

# 삼각형 보색 계산 (Triadic: 120도, 240도)
def get_triadic_hex(hex_code):
    return get_harmony_colors(hex_code, [120.0, 240.0])

# ----------------------------
# Streamlit 앱
# ----------------------------
def main():
    st.set_page_config(page_title="색상 조화 추천기", layout="centered")
    st.title("🌈 색상 조화 추천기")
    st.markdown("---")
    
    st.markdown("""
        **HEX 코드**를 입력하여 그 색상과 조화로운 색상 팔레트(보색, 유사색, 삼각형 보색)를 확인하세요.
        (예시 코드: `#4682B4`)
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
    if st.button("✨ 색상 분석 및 추천", type="primary"):
        if clean_hex.startswith('#') and len(clean_hex) == 7:
            try:
                # 유효한 HEX 코드인지 확인
                webcolors.hex_to_rgb(clean_hex) 
                
                st.subheader("결과")
                
                # --- [A. 보색 계산 및 표시] ---
                st.markdown("### 1. 보색 (Complementary) 🔄")
                comp_hex = get_complementary_hex_simple(clean_hex)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(get_color_box_html(clean_hex, "Your Color"), unsafe_allow_html=True)
                with col2:
                    st.markdown(get_color_box_html(comp_hex, "Complementary"), unsafe_allow_html=True)
                
                st.info("보색은 색상환에서 180° 반대편에 위치하며, 가장 강한 대비를 이루어 시선을 사로잡습니다.")
                st.markdown("---")

                # --- [B. 유사색 계산 및 표시] ---
                st.markdown("### 2. 유사색 (Analogous) 🤝")
                analogous_list = get_analogous_hex(clean_hex)
                
                # 본인 색상 + 유사색 2개를 3개의 열에 표시
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown(get_color_box_html(analogous_list[0], "-30° Analogous"), unsafe_allow_html=True)
                with col_b:
                    st.markdown(get_color_box_html(clean_hex, "Your Color"), unsafe_allow_html=True)
                with col_c:
                    st.markdown(get_color_box_html(analogous_list[1], "+30° Analogous"), unsafe_allow_html=True)
                
                st.info("유사색은 색상환에서 근접한 색(±30° 이내)으로, 편안하고 통일감 있는 느낌을 줍니다.")
                st.markdown("---")
                
                # --- [C. 삼각형 보색 계산 및 표시] ---
                st.markdown("### 3. 삼각형 보색 (Triadic) 🔺")
                triadic_list = get_triadic_hex(clean_hex)
                
                # 본인 색상 + 삼각형 보색 2개를 3개의 열에 표시
                col_t1, col_t2, col_t3 = st.columns(3)
                
                with col_t1:
                    st.markdown(get_color_box_html(clean_hex, "Your Color"), unsafe_allow_html=True)
                with col_t2:
                    st.markdown(get_color_box_html(triadic_list[0], "+120° Triadic"), unsafe_allow_html=True)
                with col_t3:
                    st.markdown(get_color_box_html(triadic_list[1], "+240° Triadic"), unsafe_allow_html=True)
                
                st.info("삼각형 보색은 120° 간격으로 이루어진 세 가지 색상 조합으로, 풍부하면서도 균형 잡힌 대비를 제공합니다.")
                
            except ValueError:
                st.error("⚠️ 유효하지 않은 HEX 코드 형식입니다. `#RRGGBB` 형식으로 입력해 주세요.")
        else:
            st.warning("HEX 코드는 '#'으로 시작하는 7자리 문자열이어야 합니다 (예: `#AABBCC`).")

if __name__ == "__main__":
    main()
