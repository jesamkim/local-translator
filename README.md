# 로컬 번역기 (Local Translator)

로컬 환경에서 동작하는 다국어 번역기입니다. HuggingFace의 NLLB-200-distilled-600M 모델을 사용합니다.

A local multilingual translator powered by HuggingFace's NLLB-200-distilled-600M model.

**지원 언어**: 한국어, 영어, 일본어, 중국어

## 주요 기능 (Features)

- ✅ **다국어 번역 지원**
  - 한국어 ↔ 영어 (양방향)
  - 일본어 → 영어
  - 중국어 → 영어
- ✅ **언어 감지 및 선택**
  - 자동 언어 감지
  - 수동 언어 선택 (드롭다운)
- ✅ **2가지 인터페이스 지원**
  - CLI (Command Line Interface)
  - 데스크톱 앱 (PyQt6, macOS/Windows/Linux)
- ✅ **macOS 배포**
  - 독립 실행 가능한 .app 번들
  - DMG 설치 파일 생성
  - 커스텀 앱 아이콘
- ✅ 파일 번역 지원
- ✅ 대화형 모드
- ✅ GPU 가속 지원

## 설치 (Installation)

### 방법 1: DMG 파일 사용 (macOS - 가장 쉬운 방법) 🎯

#### 다운로드

**GitHub Release에서 다운로드** (권장):

1. [Releases 페이지](https://github.com/jesamkim/local-translator/releases) 방문
2. 최신 릴리스에서 `Local-Translator-1.0.0.dmg` 다운로드
3. 아래 설치 단계 진행

또는 직접 링크: [최신 버전 다운로드](https://github.com/jesamkim/local-translator/releases/latest)

#### 설치

1. 다운로드한 `Local-Translator-1.0.0.dmg` 더블클릭
2. `Local Translator.app`을 **Applications** 폴더로 드래그
3. Applications에서 앱 실행

**장점**: Python 설치 불필요, 모든 의존성 포함

### 방법 2: 소스 코드에서 실행 (개발자용)

#### 1. 가상환경 생성 (Create Virtual Environment)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

#### 2. 의존성 설치 (Install Dependencies)

```bash
pip install -r requirements.txt
```

#### 3. 모델 다운로드 (Model Download)

첫 실행 시 자동으로 모델이 다운로드됩니다 (~2.5GB).

The model will be automatically downloaded on first run (~2.5GB).

## 사용법 (Usage)

### 데스크톱 앱 사용 (Desktop App) 🖥️

가장 사용하기 쉬운 방법입니다. 그래픽 인터페이스로 번역할 수 있습니다.

```bash
# 가상환경 활성화
source venv/bin/activate

# PyQt6 설치 (최초 1회)
pip install PyQt6

# 앱 실행
python src/desktop/translator_app.py
```

#### 데스크톱 앱 기능

- 🎨 현대적인 GUI 디자인
- 🌐 **다국어 번역 지원** (한국어, 영어, 일본어, 중국어)
- 🔄 **언어 선택 모드**
  - 자동 감지 모드 (체크박스 ON)
  - 수동 선택 모드 (체크박스 OFF - 드롭다운으로 언어 선택)
- ⚡ 실시간 번역
- 📋 번역 결과 복사
- 🔄 원문/번역문 교환
- 🔢 문자 수 카운트
- 🎯 백그라운드 번역 (UI 반응성)
- 🎨 커스텀 앱 아이콘 ("KO ⇄ EN")

#### macOS .app 번들 및 DMG 배포 파일 만들기

독립 실행 가능한 macOS 앱으로 패키징하려면 [BUILD_APP.md](BUILD_APP.md)를 참조하세요.

**간단 빌드:**
```bash
# 개발/테스트용 (alias 모드)
python setup.py py2app -A

# 배포용 (standalone)
python setup.py py2app

# DMG 파일 생성
hdiutil create -volname "Local Translator" -srcfolder "dist/Local Translator.app" -ov -format UDZO "Local-Translator-1.0.0.dmg"
```

생성된 DMG 파일은 Python이 설치되지 않은 다른 Mac에서도 실행 가능합니다.

### CLI 사용법

#### Alias 설정 (권장)

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
  -s {en,ko,ja,zh}, --source {en,ko,ja,zh}
                        원본 언어 (기본값: 자동감지)
                        en=English, ko=Korean, ja=Japanese, zh=Chinese
  -d {en,ko,ja,zh}, --destination {en,ko,ja,zh}
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
│   │   └── core.py           # 핵심 번역 모듈 (다국어 지원)
│   ├── desktop/
│   │   └── translator_app.py # PyQt6 데스크톱 앱
│   └── cli.py                # CLI 인터페이스
├── icons/
│   ├── icon.png              # 앱 아이콘 (512x512)
│   ├── icon.icns             # macOS 아이콘 파일
│   └── icon.iconset/         # 아이콘 생성 리소스
├── tests/                    # 테스트 코드
├── requirements.txt          # 의존성 목록
├── setup.py                  # macOS 앱 빌드 설정
├── create_icon.py            # 아이콘 생성 스크립트
├── BUILD_APP.md              # macOS 앱 빌드 가이드
└── README.md
```

## 예제 (Examples)

### 예제 1: 데스크톱 앱 사용

1. **자동 감지 모드** (기본):
   - 체크박스 ☑️ "언어 자동 감지" 활성화
   - 한국어 입력 → 자동으로 영어로 번역
   - 일본어 입력 → 자동으로 영어로 번역

2. **수동 선택 모드**:
   - 체크박스 ☐ "언어 자동 감지" 비활성화
   - Source 드롭다운: 한국어 선택
   - Target 드롭다운: 중국어 선택 (같은 언어는 자동 방지)
   - 한국어 입력 → 중국어로 번역

### 예제 2: CLI 간단한 번역

```bash
$ trans -t "Hello, how are you?"
안녕하세요, 어떻게 지내세요?

$ trans -t "こんにちは"
Hello
```

### 예제 3: 대화형 모드

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

### 개발 환경 (소스 코드 실행)
- Python 3.8 이상
- RAM: 최소 4GB (권장 8GB)
- 저장 공간: 3GB 이상 (모델 포함)
- GPU: 선택사항 (CUDA 지원 시 더 빠른 번역)

### macOS 앱 배포 버전 (DMG)
- macOS 10.14 (Mojave) 이상
- RAM: 최소 4GB (권장 8GB)
- 저장 공간: 2GB 이상
- Apple Silicon (M1/M2/M3) 또는 Intel 프로세서
- **Python 설치 불필요** (모든 의존성 포함)

## 문제 해결 (Troubleshooting)

### macOS Gatekeeper 경고 (DMG 설치 시)

DMG에서 설치한 앱을 처음 실행할 때 "손상되었거나 개발자를 확인할 수 없습니다" 경고가 나올 수 있습니다.

**해결 방법 1**: 터미널에서 격리 속성 제거
```bash
xattr -cr "/Applications/Local Translator.app"
```

**해결 방법 2**: 시스템 설정에서 허용
1. 시스템 설정 → 보안 및 개인 정보
2. "확인 없이 열기" 버튼 클릭

### Out of Memory 오류

GPU 메모리가 부족한 경우:
```bash
trans --no-gpu
```

또는 데스크톱 앱은 기본적으로 CPU 모드로 동작합니다.

### 모델 다운로드 실패

인터넷 연결을 확인하고 재시도하거나, HuggingFace 토큰이 필요한 경우 설정하세요.

### 번역 속도가 느림

- GPU를 사용하면 훨씬 빠릅니다
- 첫 번역은 모델 로딩으로 시간이 걸릴 수 있습니다 (~30초)
- DMG 앱의 경우 첫 실행 시 모델 로딩에 시간이 더 걸릴 수 있습니다

## 지원 언어 (Supported Languages)

현재 버전:
- 🇰🇷 한국어 (Korean) - 양방향 번역
- 🇺🇸 영어 (English) - 양방향 번역
- 🇯🇵 일본어 (Japanese) - 영어로 번역
- 🇨🇳 중국어 (Chinese) - 영어로 번역

**데스크톱 앱에서는 드롭다운 메뉴를 통해 언어를 직접 선택할 수 있습니다.**

추가 예정:
- 스페인어, 프랑스어, 독일어 등

## 라이선스 (License)

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여 (Contributing)

기여를 환영합니다! 이슈나 PR을 자유롭게 제출해주세요.

## 향후 계획 (Roadmap)

- [x] PyQt6 기반 데스크톱 앱
- [x] 다국어 지원 확장 (일본어, 중국어)
- [x] 언어 수동 선택 기능
- [x] 커스텀 앱 아이콘
- [x] macOS .app 번들 및 DMG 배포 파일
- [ ] Windows .exe 빌드
- [ ] 더 많은 언어 지원 (스페인어, 프랑스어 등)
- [ ] 번역 품질 개선 옵션
- [ ] 번역 히스토리 저장 기능
- [ ] 번역 결과 즐겨찾기 기능
