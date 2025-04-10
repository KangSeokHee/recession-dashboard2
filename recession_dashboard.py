import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

# ✅ 페이지 설정은 맨 위에서 딱 한 번
st.set_page_config(page_title="침체 고점 포착 대시보드", layout="wide")

# ---------------------- 사용자 정보 ----------------------
if "USERS" not in st.session_state:
    st.session_state.USERS = {
        "user1@example.com": "password123",
        "test@naver.com": "abc123",
        "sukhee1015@naver.com": "rkdtjrgml"
    }

# ---------------------- 로그인 상태 ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------------------- 로그인 화면 ----------------------
def show_login():
    st.title("🔐 로그인 필요")
    email = st.text_input("이메일 입력", key="login_email")
    password = st.text_input("비밀번호 입력", type="password", key="login_password")

    if st.button("로그인", key="login_button"):
        if email in st.session_state.USERS and st.session_state.USERS[email] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = email
            st.success(f"환영합니다, {email}님!")
            st.rerun()
        else:
            st.error("이메일 또는 비밀번호가 올바르지 않습니다.")

    st.markdown("---")
    if st.button("회원가입 하러가기", key="to_register_button"):
        st.session_state.page = "register"
        st.rerun()

# ---------------------- 회원가입 화면 ----------------------
def show_register():
    st.title("📝 회원가입")
    new_email = st.text_input("새 이메일 입력", key="register_email")
    new_password = st.text_input("새 비밀번호 입력", type="password", key="register_password")

    if st.button("회원가입 완료", key="register_submit"):
        if new_email in st.session_state.USERS:
            st.error("이미 존재하는 이메일입니다.")
        else:
            st.session_state.USERS[new_email] = new_password
            st.success("회원가입이 완료되었습니다. 로그인 해주세요!")
            st.session_state.page = "login"
            st.rerun()

    if st.button("로그인 화면으로 돌아가기", key="back_to_login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------------- 대시보드 ----------------------
def show_dashboard():
    st.title("📉 침체 고점 포착 대시보드")
    st.caption("📊 실시간 나스닥 지수, 미국 실업률, 공포지수(VIX), 기준금리를 추적합니다.")

    st.sidebar.success(f"🔓 로그인 계정: {st.session_state.current_user}")
    if st.sidebar.button("로그아웃", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.page = "login"
        st.rerun()

    오늘 = datetime.today()
    시작일 = 오늘 - timedelta(days=180)
    나스닥 = yf.download("^IXIC", start=시작일, end=오늘)
    VIX = yf.download("^VIX", start=시작일, end=오늘)

    예시_실업률 = [3.6, 3.8, 4.0, 4.2, 4.3, 4.4]
    예시_금리 = [5.25, 5.25, 5.25, 5.25, 5.25, 5.00]
    예시_날짜 = ["2024년 10월", "2024년 11월", "2024년 12월", "2025년 1월", "2025년 2월", "2025년 3월"]

    좌측, 우측 = st.columns(2)
    with 좌측:
        st.subheader("🟢 나스닥(NASDAQ) 지수")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=나스닥.index, y=나스닥['Close'], mode='lines', name='NASDAQ'))
        fig1.update_layout(height=300)
        st.plotly_chart(fig1, use_container_width=True)

    with 우측:
        st.subheader("🔴 공포지수 (VIX)")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=VIX.index, y=VIX['Close'], mode='lines', name='VIX', line=dict(color='red')))
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🟠 미국 실업률 (예시)")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=예시_날짜, y=예시_실업률, marker_color='orange'))
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🔵 미국 기준금리 (예시)")
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=예시_날짜, y=예시_금리, marker_color='blue'))
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.success("✅ 기준금리가 인하되고, 실업률이 하락하며, VIX가 안정되면 침체 고점 가능성이 높아집니다.")

    # --- 자동 알림 ---
    if not VIX['Close'].dropna().empty:
        vix_value = float(VIX['Close'].dropna().iloc[-1])
    else:
        vix_value = 0.0

    if not 나스닥['Close'].dropna().empty:
        close_series = 나스닥['Close'].dropna()
        nasdaq_value = float(close_series.iloc[-1])
        nasdaq_peak = float(close_series.max())
        nasdaq_drop = ((nasdaq_peak - nasdaq_value) / nasdaq_peak) * 100
    else:
        nasdaq_value = 0.0
        nasdaq_drop = 0.0

    실업률_마지막 = 예시_실업률[-1]
    금리_마지막 = 예시_금리[-1]

    if vix_value >= 30:
        st.warning(f"⚠️ 현재 VIX(공포지수)가 {vix_value:.2f}로 30 이상입니다. 시장 불확실성이 매우 높습니다!")
    if 실업률_마지막 >= 4.5:
        st.warning(f"📉 미국 실업률이 {실업률_마지막:.2f}%로 상승했습니다. 침체 가능성이 커지고 있습니다.")
    if 금리_마지막 <= 5.00:
        st.info(f"💡 기준금리가 {금리_마지막:.2f}%로 낮아지고 있습니다. 금리 전환 신호 가능성!")
    if nasdaq_drop >= 20:
        st.success(f"🟢 나스닥이 고점 대비 {nasdaq_drop:.1f}% 하락했습니다. 저점 매수 기회를 고려할 수 있습니다.")

    # --- 침체 점수 ---
    점수 = 0
    if vix_value >= 30:
        점수 += min((vix_value - 30) * 1.5, 30)
    if 실업률_마지막 >= 4.5:
        점수 += min((실업률_마지막 - 4.5) * 30, 30)
    if 금리_마지막 <= 5.0:
        점수 += (5.0 - 금리_마지막) * 10
    if nasdaq_drop >= 20:
        점수 += min((nasdaq_drop - 20), 20)

    총점수 = round(min(점수, 100), 1)
    st.markdown("---")
    st.subheader("📊 침체 위험 점수: ")
    if 총점수 >= 80:
        st.error(f"🔴 {총점수}점 — 매우 높은 침체 가능성!")
    elif 총점수 >= 50:
        st.warning(f"🟡 {총점수}점 — 주의 필요")
    else:
        st.success(f"🟢 {총점수}점 — 현재 안정적입니다.")

    # --- 종목: SOXL / TSLL ---
    st.markdown("---")
    st.subheader("📈 주요 종목 모니터링 (SOXL / TSLL)")
    soxl = yf.download("SOXL", period="6mo")
    tsll = yf.download("TSLL", period="6mo")

    if not soxl['Close'].dropna().empty:
        soxl_now = float(soxl['Close'].dropna().iloc[-1])
        soxl_peak = float(soxl['Close'].dropna().max())
        soxl_drop = ((soxl_peak - soxl_now) / soxl_peak) * 100
        st.metric("📉 SOXL 현재가", f"${soxl_now:.2f}", f"하락률: {soxl_drop:.1f}%")
        if 총점수 >= 80:
            st.error("⚠️ 침체 가능성이 매우 높습니다. SOXL은 레버리지 상품이므로 보수적 접근 권장!")
        elif 총점수 >= 50:
            st.warning("⏳ 침체 경고 구간입니다. SOXL 비중 확대는 신중하게!")
        else:
            st.success("🟢 시장 안정 구간입니다. SOXL 진입 검토 가능!")

    if not tsll['Close'].dropna().empty:
        tsll_now = float(tsll['Close'].dropna().iloc[-1])
        tsll_peak = float(tsll['Close'].dropna().max())
        tsll_drop = ((tsll_peak - tsll_now) / tsll_peak) * 100
        st.metric("📉 TSLL 현재가", f"${tsll_now:.2f}", f"하락률: {tsll_drop:.1f}%")
        if 총점수 >= 80:
            st.error("⚠️ 침체 위험이 큽니다. TSLL은 고위험 레버리지 상품입니다!")
        elif 총점수 >= 50:
            st.warning("⛔ 테슬라 지수 하락 가능성 주의. TSLL 신중 접근")
        else:
            st.success("🟢 TSLL은 기술주 반등 구간에서 유리할 수 있습니다.")

# ---------------------- 라우팅 ----------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.logged_in:
    if st.session_state.page == "register":
        show_register()
    else:
        show_login()
else:
    show_dashboard()

