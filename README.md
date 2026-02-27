# DSS 검수 시스템 (Streamlit 버전)

어닝콜 원문과 DSS(Daily Stock Summary) 요약본을 비교하여 수치 오류, 문맥 이슈를 자동으로 검증하는 AI 기반 웹 검수 시스템입니다.

## 🌟 주요 기능

- **자동 검증**: Claude AI를 사용하여 DSS 문장을 하나씩 검증
- **수치 불일치 탐지**: 어닝콜 원문과 DSS의 숫자, 단위 불일치 자동 탐지
- **문맥 이슈 검출**: 과장, 축소, 누락된 정보 감지
- **실시간 수정**: 승인, 거부, 수동 편집 기능
- **최종 수정안 생성**: DSS 형식으로 최종 수정안 자동 생성
- **Streamlit UI**: 직관적인 웹 인터페이스

## 📋 검증 항목

### 수치 이슈 (빨간색 ❌)
- 매출, 이익, 가이던스 등의 숫자 불일치
- 단위 오류 (억원 vs 조원)
- 기간 정보 오류

### 문맥 이슈 (노란색 ⚠️)
- 과장 또는 축소된 표현
- 조건 누락 (단서 조항 생략)
- 불완전한 정보

### 일치함 (초록색 ✅)
- 어닝콜 원문과 일치하는 정확한 문장

## 🚀 로컬 실행

### 1. 저장소 클론

\`\`\`bash
git clone https://github.com/your-username/dss-validation-system.git
cd dss-validation-system
\`\`\`

### 2. 패키지 설치

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. 환경변수 설정

\`.env\` 파일 생성:

\`\`\`env
ANTHROPIC_API_KEY=your_actual_api_key_here
\`\`\`

**API 키 발급**: [Anthropic Console](https://console.anthropic.com/)

### 4. 서버 실행

\`\`\`bash
streamlit run streamlit_app.py
\`\`\`

브라우저에서 자동으로 열립니다: **http://localhost:8501**

## 🌐 Streamlit Cloud 배포 (무료)

### 1. GitHub에 코드 업로드

\`\`\`bash
git init
git add .
git commit -m "Initial commit: DSS validation Streamlit app"
git branch -M main
git remote add origin https://github.com/your-username/dss-validation-system.git
git push -u origin main
\`\`\`

### 2. Streamlit Cloud 배포

1. **[Streamlit Cloud](https://share.streamlit.io/) 접속**
   - GitHub 계정으로 로그인

2. **New app 클릭**

3. **설정 입력**:
   - **Repository**: your-username/dss-validation-system
   - **Branch**: main
   - **Main file path**: streamlit_app.py

4. **Secrets 추가** (Advanced settings):
   \`\`\`toml
   ANTHROPIC_API_KEY = "your_actual_api_key_here"
   \`\`\`

5. **Deploy!** 클릭
   - 2-3분 후 배포 완료
   - URL 예시: `https://your-app.streamlit.app`

### 자동 재배포

GitHub에 코드를 푸시하면 자동으로 재배포됩니다:

\`\`\`bash
git add .
git commit -m "Update features"
git push origin main
\`\`\`

## 📁 프로젝트 구조

\`\`\`
dss-validation-system/
├── streamlit_app.py            # Streamlit 메인 애플리케이션
├── src/
│   └── financial_parser.py     # DSS 검증 로직
├── .streamlit/
│   └── config.toml             # Streamlit 설정
├── requirements.txt            # Python 패키지 목록
├── .env                        # 환경변수 (로컬용, Git 제외)
├── .gitignore                  # Git 제외 파일 목록
└── README.md                   # 프로젝트 문서
\`\`\`

## 🎯 사용 방법

### 1. 입력
- **좌측 사이드바**에서 어닝콜 원문과 DSS 요약본 입력
- PDF URL 또는 텍스트 직접 입력 가능

### 2. 검증
- "🔍 검증 시작" 버튼 클릭
- AI가 자동으로 문장별 검증 수행

### 3. 검토
- 각 탭(실적발표, 가이던스, Q&A)에서 이슈 확인
- 승인(✅), 거부(❌), 수동 편집(✏️) 선택

### 4. 최종안
- "최종 수정안" 탭에서 결과 확인
- DSS 형식으로 자동 생성
- 파일 다운로드 가능

## ⚙️ 환경변수

| 변수명 | 설명 | 필수 |
|--------|------|------|
| \`ANTHROPIC_API_KEY\` | Claude API 키 | ✅ |

## 🛠️ 기술 스택

- **Framework**: Streamlit
- **AI**: Claude 3 Haiku (Anthropic API)
- **Language**: Python 3.8+
- **파일 처리**: PyPDF2, pdfplumber
- **배포**: Streamlit Cloud (무료)

## 📊 API 사용량

Claude Haiku 기준:
- **입력**: 약 $0.25 / 1M tokens
- **출력**: 약 $1.25 / 1M tokens
- DSS 문장 1개당 평균 500 tokens 사용
- 50문장 검증 시 약 $0.05 예상

## 🔒 보안

- **API 키 보호**: .gitignore로 secrets.toml 제외
- **Streamlit Secrets**: 안전한 환경변수 관리
- **HTTPS**: Streamlit Cloud 자동 제공

## 🆚 Flask 버전과 비교

| 항목 | Streamlit 버전 | Flask 버전 |
|------|---------------|-----------|
| 코드 복잡도 | ⭐⭐ 간단 | ⭐⭐⭐⭐ 복잡 |
| 배포 | ⭐⭐⭐⭐⭐ 매우 쉬움 | ⭐⭐⭐ 보통 |
| UI 커스터마이징 | ⭐⭐⭐ 제한적 | ⭐⭐⭐⭐⭐ 자유로움 |
| 개발 속도 | ⭐⭐⭐⭐⭐ 매우 빠름 | ⭐⭐⭐ 보통 |

## 📝 라이센스

MIT License

## 🤝 기여

이슈 및 PR 환영합니다!

1. Fork the Project
2. Create your Feature Branch (\`git checkout -b feature/AmazingFeature\`)
3. Commit your Changes (\`git commit -m 'Add some AmazingFeature'\`)
4. Push to the Branch (\`git push origin feature/AmazingFeature\`)
5. Open a Pull Request

## 📧 문의

문제가 발생하면 [Issues](https://github.com/your-username/dss-validation-system/issues)에 등록해주세요.

## 🙏 감사의 말

- Claude API by Anthropic
- Streamlit
- Python Community

---

**최종 업데이트**: 2026-02-27
**버전**: 2.0.0 (Streamlit)
