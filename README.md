# 로컬 번역기 (Local Translator)

로컬 환경에서 동작하는 한글-영어 번역기입니다. HuggingFace의 NLLB-200-distilled-600M 모델을 사용합니다.

A local Korean-English translator powered by HuggingFace's NLLB-200-distilled-600M model.

## 주요 기능 (Features)

- ✅ 한글 ↔ 영어 양방향 번역
- ✅ 언어 자동 감지
- ✅ CLI 인터페이스 지원
- ✅ 파일 번역 지원
- ✅ 대화형 모드
- ✅ GPU 가속 지원
- 🔜 Streamlit UI (개발 예정)

## 설치 (Installation)

### 1. 가상환경 생성 (Create Virtual Environment)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치 (Install Dependencies)

```bash
pip install -r requirements.txt
```

### 3. 모델 다운로드 (Model Download)

첫 실행 시 자동으로 모델이 다운로드됩니다 (~2.5GB).

The model will be automatically downloaded on first run (~2.5GB).

## 사용법 (Usage)

### Alias 설정 (권장)

어디서나 `trans` 명령어로 번역기를 사용할 수 있도록 설정:

```bash
# ~/.bashrc 또는 ~/.zshrc 파일에 추가
trans() {
    local TRANS_DIR="/Workshop/local-translator"
    (cd "$TRANS_DIR" && source venv/bin/activate && python -m src.cli "$@")
}

# 설정 적용
source ~/.bashrc  # 또는 source ~/.zshrc
```

이제 어디서든 사용 가능합니다:

```bash
# 대화형 모드
trans

# 직접 번역
trans -t "Hello, World!"
trans -t "안녕하세요"

# 파일 번역
trans -f input.txt -o output.txt
```

### 대화형 모드 (Interactive Mode)

가장 간단한 사용 방법입니다:

```bash
python -m src.cli
# 또는 alias 설정 후
trans
```

대화형 모드에서는:
- 텍스트를 입력하면 자동으로 언어를 감지하여 번역합니다
- `quit`, `exit`, `q`를 입력하면 종료됩니다

### 직접 텍스트 번역 (Direct Text Translation)

```bash
# 영어 → 한글
trans -t "Hello, World!"
# 또는
python -m src.cli -t "Hello, World!"

# 한글 → 영어
trans -t "안녕하세요, 세계!"

# 언어 명시
trans -t "Hello" -s en -d ko --no-auto-detect
```

### 파일 번역 (File Translation)

```bash
# 입력 파일 번역 (출력 파일 자동 생성)
trans -f input.txt

# 출력 파일 지정
trans -f input.txt -o output.txt

# 언어 명시하여 파일 번역
trans -f english.txt -o korean.txt -s en -d ko --no-auto-detect
```

### GPU 사용 설정 (GPU Configuration)

```bash
# GPU 사용 (기본값)
trans

# CPU만 사용
trans --no-gpu
```

## CLI 옵션 (CLI Options)

```
옵션:
  -h, --help            도움말 표시
  -t TEXT, --text TEXT  번역할 텍스트
  -f FILE, --file FILE  번역할 파일 경로
  -o OUTPUT, --output OUTPUT
                        출력 파일 경로
  -s {en,ko}, --source {en,ko}
                        원본 언어 (기본값: 자동감지)
  -d {en,ko}, --destination {en,ko}
                        목적 언어 (기본값: 자동감지)
  --auto-detect         언어 자동 감지 (기본값)
  --no-auto-detect      언어 자동 감지 비활성화
  --no-gpu              GPU 사용 안함
```

## 프로젝트 구조 (Project Structure)

```
local-translator/
├── src/
│   ├── translator/
│   │   ├── __init__.py
│   │   └── core.py          # 핵심 번역 모듈
│   ├── ui/                   # Streamlit UI (개발 예정)
│   └── cli.py                # CLI 인터페이스
├── tests/                    # 테스트 코드
├── requirements.txt          # 의존성 목록
└── README.md
```

## 예제 (Examples)

### 예제 1: 간단한 번역

```bash
$ trans -t "Hello, how are you?"
안녕하세요, 어떻게 지내세요?
```

### 예제 2: 대화형 모드

```bash
$ trans
============================================================
   로컬 번역기 (Local Translator)
   한글 ↔ 영어 번역 (Korean ↔ English)
============================================================

대화형 모드 (Interactive Mode)
종료하려면 'quit', 'exit', 또는 'q'를 입력하세요.
언어 자동 감지 활성화됨 (Auto language detection enabled)
------------------------------------------------------------

번역할 텍스트 입력 (Enter text): Good morning!

[감지된 언어 방향: 영어 → 한글]

좋은 아침입니다!

------------------------------------------------------------

번역할 텍스트 입력 (Enter text): 감사합니다

[감지된 언어 방향: 한글 → 영어]

Thank you

------------------------------------------------------------
```

## 시스템 요구사항 (System Requirements)

- Python 3.8 이상
- RAM: 최소 4GB (권장 8GB)
- 저장 공간: 3GB 이상 (모델 포함)
- GPU: 선택사항 (CUDA 지원 시 더 빠른 번역)

## 문제 해결 (Troubleshooting)

### Out of Memory 오류

GPU 메모리가 부족한 경우:
```bash
trans --no-gpu
```

### 모델 다운로드 실패

인터넷 연결을 확인하고 재시도하거나, HuggingFace 토큰이 필요한 경우 설정하세요.

### 번역 속도가 느림

- GPU를 사용하면 훨씬 빠릅니다
- 첫 번역은 모델 로딩으로 시간이 걸릴 수 있습니다

## 지원 언어 (Supported Languages)

현재 버전:
- 🇰🇷 한국어 (Korean)
- 🇺🇸 영어 (English)

추가 예정:
- 일본어, 중국어, 스페인어, 프랑스어 등

## 라이선스 (License)

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여 (Contributing)

기여를 환영합니다! 이슈나 PR을 자유롭게 제출해주세요.

## 향후 계획 (Roadmap)

- [ ] Streamlit 기반 웹 UI 추가
- [ ] 다국어 지원 확장
- [ ] 번역 품질 개선 옵션
- [ ] 번역 히스토리 저장 기능
- [ ] API 서버 모드 추가
