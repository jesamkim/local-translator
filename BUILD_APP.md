# macOS 앱 빌드 가이드

PyQt6 번역기를 macOS .app 번들 및 .dmg로 패키징하는 방법입니다.

## 빠른 시작 (Quick Start)

```bash
# 1. 가상환경 활성화 및 py2app 설치
source venv/bin/activate
pip install py2app

# 2. 아이콘 생성 (이미 있으면 생략)
python create_icon.py

# 3. 테스트용 빌드 (빠름, alias 모드)
python setup.py py2app -A

# 4. 배포용 빌드 (느림, standalone 모드)
rm -rf build dist
python setup.py py2app

# 5. DMG 생성
hdiutil create -volname "Local Translator" \
  -srcfolder "dist/Local Translator.app" \
  -ov -format UDZO \
  "Local-Translator-1.0.0.dmg"

# 6. 테스트
open "dist/Local Translator.app"
```

**빌드 시간**:
- Alias 모드 (-A): ~30초
- Standalone 모드: ~8분 (첫 빌드)

**결과물 크기**:
- .app 번들: ~1.0 GB
- DMG 파일: ~475 MB (압축됨)

---

## 1. 사전 준비

### py2app 설치

```bash
source venv/bin/activate
pip install py2app
```

### 아이콘 생성

프로젝트에는 이미 아이콘이 포함되어 있습니다 (`icons/icon.icns`).
새로운 아이콘을 만들고 싶다면:

```bash
python create_icon.py
```

## 2. setup.py 확인

프로젝트 루트에 `setup.py` 파일이 이미 생성되어 있습니다:

```python
from setuptools import setup
import sys

# Increase recursion limit for py2app (PyTorch/transformers 빌드 시 필요)
sys.setrecursionlimit(5000)

APP = ['src/desktop/translator_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'PyQt6',
        'transformers',
        'torch',
        'sentencepiece',
    ],
    'includes': [
        'src.translator',
    ],
    'excludes': [
        'matplotlib',
        'numpy.distutils',
        'scipy',
        'pytest',
        'sphinx',
        'IPython',
    ],
    'iconfile': 'icons/icon.icns',
    'plist': {
        'CFBundleName': 'Local Translator',
        'CFBundleDisplayName': 'Local Translator',
        'CFBundleIdentifier': 'com.localtranslator.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='Local Translator',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

**중요**:
- `sys.setrecursionlimit(5000)`: PyTorch/transformers 빌드 시 recursion error 방지
- `excludes`: 불필요한 패키지 제외로 앱 크기 감소

## 3. .app 빌드

```bash
# 개발 모드 (빠름, 테스트용)
python setup.py py2app -A

# 배포 모드 (느림, 독립 실행 가능)
python setup.py py2app
```

빌드 완료 후 `dist/Local Translator.app` 생성됩니다.

## 4. .app 테스트

```bash
# .app 실행
open "dist/Local Translator.app"

# 또는 직접 실행
./dist/Local\ Translator.app/Contents/MacOS/Local\ Translator
```

## 5. .dmg 생성 (배포용)

### 방법 1: hdiutil 사용 (권장)

가장 간단하고 추가 설치가 필요 없는 방법:

```bash
hdiutil create -volname "Local Translator" \
  -srcfolder "dist/Local Translator.app" \
  -ov -format UDZO \
  "Local-Translator-1.0.0.dmg"
```

**결과**:
- DMG 크기: ~475MB (압축됨)
- 원본 .app 크기: ~1.0GB

### 방법 2: create-dmg 사용 (고급)

더 세련된 DMG 레이아웃이 필요한 경우:

```bash
# create-dmg 설치
brew install create-dmg

# DMG 생성
create-dmg \
  --volname "Local Translator" \
  --volicon "icons/icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "Local Translator.app" 200 190 \
  --hide-extension "Local Translator.app" \
  --app-drop-link 600 185 \
  "Local-Translator-1.0.0.dmg" \
  "dist/"
```

### 방법 3: 수동 생성

1. 디스크 유틸리티 열기
2. 파일 → 새로운 이미지 → 폴더에서 이미지 생성
3. `dist/` 폴더 선택
4. 이미지 포맷: "압축"
5. 저장

## 6. 앱 서명 (선택사항, 배포 시 필요)

```bash
# 개발자 ID로 서명
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/Local Translator.app"

# 확인
codesign --verify --deep --strict --verbose=2 \
  "dist/Local Translator.app"

# Notarization (공증)
xcrun notarytool submit "Local-Translator-1.0.0.dmg" \
  --apple-id "your@email.com" \
  --team-id "YOUR_TEAM_ID" \
  --password "app-specific-password"
```

## 7. 배포

생성된 `.dmg` 파일을 배포하면:
1. 사용자가 다운로드
2. DMG를 마운트
3. .app을 Applications 폴더로 드래그
4. 실행!

## 트러블슈팅

### RecursionError 발생

`python setup.py py2app` 실행 시 recursion error가 발생하는 경우:

**원인**: PyTorch와 transformers의 복잡한 의존성 트리

**해결 방법**: setup.py에 다음이 포함되어 있는지 확인
```python
import sys
sys.setrecursionlimit(5000)
```

### 모델 파일 포함 문제

py2app이 HuggingFace 모델을 자동으로 포함하지 못할 수 있습니다.

**현재 구현**: 앱 첫 실행 시 모델을 자동으로 다운로드 (~2.5GB)

대안:
```python
# setup.py의 DATA_FILES에 모델 추가
DATA_FILES = [
    ('models', ['path/to/model/files']),
]
```

### 앱 크기가 큼

PyTorch와 Transformers가 포함되면 앱 크기가 1-2GB가 됩니다.

**완화 방법**:
- `excludes` 옵션으로 불필요한 패키지 제외 (이미 적용됨)
- 모델을 외부에서 다운로드 (현재 방식)

**DMG 압축**으로 ~475MB로 감소 (UDZO 포맷)

### "앱이 손상되어 열 수 없습니다" 오류

macOS Gatekeeper 경고입니다.

**해결 방법 1**: 터미널에서 격리 속성 제거
```bash
xattr -cr "dist/Local Translator.app"
# 또는 설치 후
xattr -cr "/Applications/Local Translator.app"
```

**해결 방법 2**: 시스템 설정에서 허용
1. 시스템 설정 → 보안 및 개인 정보
2. "확인 없이 열기" 버튼 클릭

**공식 배포 시**: 앱 서명 및 공증 필요 (섹션 6 참조)

## 대안: PyInstaller

py2app 대신 PyInstaller 사용 가능:

```bash
pip install pyinstaller

# 단일 파일로 번들
pyinstaller --onefile --windowed \
  --name "Local Translator" \
  --icon icon.icns \
  src/desktop/translator_app.py

# 또는 폴더로
pyinstaller --windowed \
  --name "Local Translator" \
  --icon icon.icns \
  src/desktop/translator_app.py
```

## 참고사항

- **첫 실행**: 모델 로딩에 시간이 걸립니다 (~30초-1분)
- **메모리**: 최소 4GB RAM 필요
- **macOS 버전**: macOS 10.14 (Mojave) 이상
- **아키텍처**: Intel 또는 Apple Silicon (M1/M2/M3)

## 아이콘 제작

### 자동 생성 (권장)

프로젝트에 포함된 스크립트 사용:

```bash
python create_icon.py
```

이 스크립트는:
- 파란색-보라색 그라디언트 원형 아이콘 생성
- "KO ⇄ EN" 텍스트 포함
- 다양한 크기의 PNG 파일 생성 (16px ~ 512px)
- macOS .icns 파일 자동 생성

**생성되는 파일**:
- `icons/icon.png` (512x512)
- `icons/icon_{size}.png` (다양한 크기)
- `icons/icon.icns` (macOS 앱 아이콘)

### 수동 생성

자신만의 PNG 아이콘이 있는 경우:

```bash
# 1. iconset 디렉토리 생성
mkdir icons/icon.iconset

# 2. 다양한 크기로 변환
sips -z 16 16     icons/icon.png --out icons/icon.iconset/icon_16x16.png
sips -z 32 32     icons/icon.png --out icons/icon.iconset/icon_16x16@2x.png
sips -z 32 32     icons/icon.png --out icons/icon.iconset/icon_32x32.png
sips -z 64 64     icons/icon.png --out icons/icon.iconset/icon_32x32@2x.png
sips -z 128 128   icons/icon.png --out icons/icon.iconset/icon_128x128.png
sips -z 256 256   icons/icon.png --out icons/icon.iconset/icon_128x128@2x.png
sips -z 256 256   icons/icon.png --out icons/icon.iconset/icon_256x256.png
sips -z 512 512   icons/icon.png --out icons/icon.iconset/icon_256x256@2x.png
sips -z 512 512   icons/icon.png --out icons/icon.iconset/icon_512x512.png
sips -z 1024 1024 icons/icon.png --out icons/icon.iconset/icon_512x512@2x.png

# 3. .icns 파일 생성
iconutil -c icns icons/icon.iconset -o icons/icon.icns
```

---

## 전체 워크플로우 요약

### 개발 중 (빠른 테스트)

```bash
# alias 모드로 빌드 (소스 코드를 심볼릭 링크로 참조)
python setup.py py2app -A
open "dist/Local Translator.app"
```

장점: 빠른 빌드, 소스 수정 후 재빌드 없이 테스트 가능  
단점: 다른 Mac에서 실행 불가 (venv 의존)

### 배포 준비

```bash
# 1. 클린 빌드
rm -rf build dist

# 2. standalone 빌드
python setup.py py2app

# 3. 로컬 테스트
open "dist/Local Translator.app"

# 4. DMG 생성
hdiutil create -volname "Local Translator" \
  -srcfolder "dist/Local Translator.app" \
  -ov -format UDZO \
  "Local-Translator-1.0.0.dmg"

# 5. DMG 테스트
open Local-Translator-1.0.0.dmg
# 마운트된 볼륨에서 앱 실행 테스트

# 6. Gatekeeper 우회 (선택사항)
xattr -cr "dist/Local Translator.app"
```

### 체크리스트

배포 전 확인사항:

- [ ] 모든 기능이 정상 작동하는지 테스트
- [ ] 아이콘이 제대로 표시되는지 확인
- [ ] 앱 첫 실행 시 모델 다운로드가 정상적으로 작동하는지 확인
- [ ] 메모리 사용량 확인 (Activity Monitor)
- [ ] DMG 마운트 및 설치 과정 테스트
- [ ] 다른 Mac에서 테스트 (가능한 경우)

### 버전 업데이트

새 버전을 배포할 때:

1. `setup.py`에서 버전 번호 업데이트:
   ```python
   'CFBundleVersion': '1.1.0',
   'CFBundleShortVersionString': '1.1.0',
   ```

2. DMG 파일명 업데이트:
   ```bash
   "Local-Translator-1.1.0.dmg"
   ```

3. README.md의 다운로드 링크 업데이트

### 디버깅 팁

빌드 중 문제가 발생하면:

```bash
# 빌드 로그 저장
python setup.py py2app > build.log 2>&1

# 생성된 앱의 실행 로그 확인
./dist/Local\ Translator.app/Contents/MacOS/Local\ Translator

# 앱 번들 구조 확인
ls -la "dist/Local Translator.app/Contents/"

# 포함된 Python 패키지 확인
ls -la "dist/Local Translator.app/Contents/Resources/lib/python3.11/"
```

### Git 관리

빌드 아티팩트는 Git에서 제외:

```bash
# .gitignore에 추가됨
*.dmg
build/
dist/
```

아이콘과 설정 파일은 포함:
- `icons/` - 아이콘 리소스
- `setup.py` - 빌드 설정
- `create_icon.py` - 아이콘 생성 스크립트

