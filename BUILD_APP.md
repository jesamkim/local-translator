# macOS 앱 빌드 가이드

PyQt6 번역기를 macOS .app 번들 및 .dmg로 패키징하는 방법입니다.

## 1. py2app 설치

```bash
source venv/bin/activate
pip install py2app
```

## 2. setup.py 생성

프로젝트 루트에 `setup.py` 파일을 생성:

```python
from setuptools import setup

APP = ['src/desktop/translator_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'PyQt6',
        'transformers',
        'torch',
        'sentencepiece',
    ],
    'includes': [
        'src.translator',
    ],
    'iconfile': 'icon.icns',  # 옵션: 앱 아이콘
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

### 방법 1: create-dmg 사용

```bash
# create-dmg 설치
brew install create-dmg

# DMG 생성
create-dmg \
  --volname "Local Translator" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "Local Translator.app" 200 190 \
  --hide-extension "Local Translator.app" \
  --app-drop-link 600 185 \
  "Local-Translator-1.0.0.dmg" \
  "dist/"
```

### 방법 2: 수동 생성

1. 디스크 유틸리티 열기
2. 파일 → 새로운 이미지 → 폴더에서 이미지 생성
3. `dist/` 폴더 선택
4. 이미지 포맷: "읽기 전용"
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

### 모델 파일 포함 문제

py2app이 HuggingFace 모델을 자동으로 포함하지 못할 수 있습니다.

해결방법:
```python
# setup.py의 DATA_FILES에 모델 추가
DATA_FILES = [
    ('models', ['path/to/model/files']),
]
```

또는 앱 첫 실행 시 모델을 다운로드하도록 설정.

### 앱 크기가 너무 큼

PyTorch와 Transformers 모델이 포함되면 앱 크기가 1-2GB가 될 수 있습니다.

해결방법:
- 불필요한 의존성 제거
- 모델을 외부에서 다운로드
- 경량 모델 사용

### "앱이 손상되어 열 수 없습니다" 오류

macOS Gatekeeper 문제입니다.

해결방법:
```bash
# 격리 속성 제거
xattr -cr "dist/Local Translator.app"

# 또는 사용자에게 안내
# 시스템 설정 → 보안 및 개인 정보 → "확인 없이 열기"
```

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

.icns 파일 생성:
```bash
# PNG를 ICNS로 변환
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

iconutil -c icns icon.iconset
```
