# -*- coding: utf-8 -*-
"""
DSS 검수 시스템 - Streamlit 버전
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import json
import sys
import requests
from PyPDF2 import PdfReader
from io import BytesIO

from src.financial_parser import FinancialDataParser

# 페이지 설정
st.set_page_config(
    page_title="DSS 검수 시스템",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'item_statuses' not in st.session_state:
    st.session_state.item_statuses = {}
if 'edited_texts' not in st.session_state:
    st.session_state.edited_texts = {}

# CSS 스타일
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    .danger-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        color: #856404;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def extract_text_from_pdf_url(url: str) -> str:
    """PDF URL에서 텍스트 추출"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        st.error(f"PDF 다운로드 실패: {str(e)}")
        return ""


def reset_app():
    """앱 초기화"""
    st.session_state.validation_result = None
    st.session_state.item_statuses = {}
    st.session_state.edited_texts = {}
    st.rerun()


def main():
    """메인 함수"""

    # 헤더
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📊 DSS 검수 시스템")
        st.caption("어닝콜 원문과 DSS 요약본을 자동으로 검증합니다")
    with col2:
        if st.session_state.validation_result is not None:
            if st.button("🔄 새로 시작하기"):
                reset_app()

    # 사이드바 - 입력
    with st.sidebar:
        st.header("📝 입력")

        # 어닝콜 입력
        st.subheader("1. 어닝콜 원문")
        ec_input_type = st.radio(
            "입력 방식",
            ["URL", "텍스트"],
            key="ec_input_type",
            horizontal=True
        )

        if ec_input_type == "URL":
            ec_url = st.text_input("PDF URL", placeholder="https://...")
            ec_text = ""
            if ec_url:
                with st.spinner("PDF 다운로드 중..."):
                    ec_text = extract_text_from_pdf_url(ec_url)
                if ec_text:
                    st.success(f"✅ {len(ec_text)} 글자 로드됨")
        else:
            ec_text = st.text_area(
                "어닝콜 텍스트",
                height=200,
                placeholder="어닝콜 원문을 입력하세요..."
            )

        st.divider()

        # DSS 입력
        st.subheader("2. DSS 요약본")
        dss_text = st.text_area(
            "DSS 텍스트",
            height=200,
            placeholder="""### 실적 발표
## 문장 1
## 문장 2

### 가이던스
## 문장 3"""
        )

        st.divider()

        # 검증 버튼
        if st.button("🔍 검증 시작", type="primary", use_container_width=True):
            if not ec_text or not dss_text:
                st.error("⚠️ 모든 필드를 입력해주세요")
            else:
                validate_dss(ec_text, dss_text)

    # 메인 영역 - 결과
    if st.session_state.validation_result is None:
        st.info("👈 좌측 사이드바에서 어닝콜과 DSS를 입력하고 검증을 시작하세요.")
    else:
        display_results()


def validate_dss(ec_text: str, dss_text: str):
    """DSS 검증 실행"""

    with st.spinner("🔄 검증 중... 잠시만 기다려주세요."):
        try:
            # API 키 확인
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                st.error("⚠️ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
                st.stop()

            # Parser 초기화
            parser = FinancialDataParser(api_key=api_key)

            # DSS 검증
            validation_result = parser.validate_dss_interpretation(ec_text, dss_text)

            # 세션에 저장
            st.session_state.validation_result = validation_result
            st.session_state.item_statuses = {}
            st.session_state.edited_texts = {}

            st.success("✅ 검증이 완료되었습니다!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ 검증 중 오류 발생: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def display_results():
    """검증 결과 표시"""

    result = st.session_state.validation_result

    if not result:
        return

    # 탭 생성
    tabs = st.tabs(["📋 실적발표", "🎯 가이던스", "💬 Q&A", "✅ 최종 수정안"])

    # 섹션별 이슈 수집
    sections = {
        '실적발표': [],
        '가이던스': [],
        'Q&A': []
    }

    for issue in result.get('interpretation_issues', []):
        section = issue.get('type', '실적발표')
        if section in sections:
            sections[section].append(issue)

    # 각 탭에 내용 표시
    for idx, (section_name, tab) in enumerate(zip(['실적발표', '가이던스', 'Q&A'], tabs[:3])):
        with tab:
            display_section(section_name, sections[section_name])

    # 최종 수정안 탭
    with tabs[3]:
        display_final_draft(sections)


def display_section(section_name: str, issues: list):
    """섹션별 이슈 표시"""

    if not issues:
        st.info(f"✅ {section_name} 섹션에 문제가 없습니다.")
        return

    st.subheader(f"📊 {section_name} - {len(issues)}개 항목")

    for idx, issue in enumerate(issues):
        item_id = f"{section_name}-{idx}"

        # 상태 가져오기
        status = st.session_state.item_statuses.get(item_id, 'pending')

        # 아이콘 및 색상 결정
        metric = issue.get('metric', '항목')
        validation_status = issue.get('validation_status', 'issue_found')
        issue_type = issue.get('issue_type', '')

        if validation_status == 'passed' or metric == '일치함':
            icon = "✅"
            color = "success"
        elif issue_type in ['수치오류', '수치']:
            icon = "❌"
            color = "danger"
        else:
            icon = "⚠️"
            color = "warning"

        # 카드 생성
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {icon} {metric}")

            with col2:
                if status == 'accepted':
                    st.success("승인됨")
                elif status == 'rejected':
                    st.error("거부됨")
                elif status == 'manual':
                    st.info("수동 편집")

            # DSS 원본
            st.markdown("**현재 (DSS 원본):**")
            dss_sentence = issue.get('dss_sentence', issue.get('dss_statement', ''))

            if validation_status == 'passed':
                st.markdown(f'<div class="success-box">{dss_sentence}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="{color}-box">{dss_sentence}</div>', unsafe_allow_html=True)

            # 권장 수정안
            st.markdown("**권장 수정안:**")
            recommendation = issue.get('recommendation', '')

            if validation_status == 'passed':
                st.markdown(f'<div class="success-box">✅ 문제 없음</div>', unsafe_allow_html=True)
            else:
                st.text_area(
                    "수정안",
                    value=st.session_state.edited_texts.get(item_id, recommendation),
                    key=f"edit_{item_id}",
                    height=100,
                    label_visibility="collapsed"
                )

            # 발견된 문제
            if issue.get('issue'):
                with st.expander("🔍 발견된 문제"):
                    st.write(issue.get('issue', ''))

            # 어닝콜 원문
            if issue.get('earning_call_context'):
                with st.expander("📄 어닝콜 원문"):
                    st.write(issue.get('earning_call_context', ''))

            # 액션 버튼
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("✅ 승인", key=f"accept_{item_id}", use_container_width=True):
                    st.session_state.item_statuses[item_id] = 'accepted'
                    st.rerun()

            with col_b:
                if st.button("❌ 거부", key=f"reject_{item_id}", use_container_width=True):
                    st.session_state.item_statuses[item_id] = 'rejected'
                    st.rerun()

            with col_c:
                if st.button("✏️ 수동", key=f"manual_{item_id}", use_container_width=True):
                    edited_text = st.session_state.get(f"edit_{item_id}", recommendation)
                    st.session_state.edited_texts[item_id] = edited_text
                    st.session_state.item_statuses[item_id] = 'manual'
                    st.rerun()

            st.divider()


def display_final_draft(sections: dict):
    """최종 수정안 표시"""

    st.subheader("📝 최종 수정안")

    # 승인된 항목 수집
    final_sentences = {
        '실적발표': [],
        '가이던스': [],
        'Q&A': []
    }

    for section_name, issues in sections.items():
        for idx, issue in enumerate(issues):
            item_id = f"{section_name}-{idx}"
            status = st.session_state.item_statuses.get(item_id, 'pending')

            if status == 'accepted':
                # 승인: 수정안 사용
                recommendation = issue.get('recommendation', '')
                final_sentences[section_name].append(recommendation)
            elif status == 'manual':
                # 수동 편집: 편집된 텍스트 사용
                edited = st.session_state.edited_texts.get(item_id, issue.get('recommendation', ''))
                final_sentences[section_name].append(edited)
            elif status == 'rejected':
                # 거부: 원본 사용
                original = issue.get('dss_sentence', issue.get('dss_statement', ''))
                final_sentences[section_name].append(original)

    # DSS 형식으로 출력
    dss_output = ""
    for section_name in ['실적발표', '가이던스', 'Q&A']:
        sentences = final_sentences[section_name]
        if sentences:
            dss_output += f"### {section_name}\n"
            for sentence in sentences:
                dss_output += f"## {sentence}\n\n"

    if not dss_output:
        st.info("승인된 항목이 없습니다. 검증 결과에서 항목을 승인하거나 수동 편집하세요.")
    else:
        st.text_area(
            "최종 수정안 (DSS 형식)",
            value=dss_output,
            height=400
        )

        # 통계
        total_count = sum(len(s) for s in final_sentences.values())
        st.success(f"✅ 총 {total_count}개 항목이 최종안에 반영되었습니다.")

        # 복사 버튼
        st.download_button(
            label="📥 DSS 파일 다운로드",
            data=dss_output,
            file_name=f"dss_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )


if __name__ == "__main__":
    main()
