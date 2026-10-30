"""Streamlit entry point for the group-order service."""

import streamlit as st


st.set_page_config(
    page_title="단체 주문 AI 에이전트",
    page_icon="☕",
    layout="centered",
)

st.title("단체 주문 AI 에이전트")
st.caption("총무의 자연어 주문을 정규화하고 합산 명세서로 정리합니다.")
st.info("주문 입력 화면은 작업 2.1에서 구현합니다.")
