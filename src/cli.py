#!/usr/bin/env python3
"""
CLI interface for local translator.
Supports Korean <-> English translation.
"""
import argparse
import sys
from pathlib import Path
from src.translator import Translator
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Simple language detection based on character analysis.
    Returns 'ko' for Korean, 'en' for English.
    """
    korean_chars = sum(1 for char in text if '\uac00' <= char <= '\ud7a3')
    total_chars = len([char for char in text if char.strip()])

    if total_chars == 0:
        return 'en'

    korean_ratio = korean_chars / total_chars

    # If more than 30% Korean characters, consider it Korean
    return 'ko' if korean_ratio > 0.3 else 'en'


def print_header():
    """Print CLI header."""
    print("=" * 60)
    print("   로컬 번역기 (Local Translator)")
    print("   한글 ↔ 영어 번역 (Korean ↔ English)")
    print("=" * 60)
    print()


def interactive_mode(translator: Translator):
    """
    Interactive translation mode.

    Args:
        translator: Translator instance
    """
    print_header()
    print("대화형 모드 (Interactive Mode)")
    print("종료하려면 'quit', 'exit', 또는 'q'를 입력하세요.")
    print("언어 자동 감지 활성화됨 (Auto language detection enabled)")
    print("-" * 60)
    print()

    while True:
        try:
            # Get input
            text = input("번역할 텍스트 입력 (Enter text): ").strip()

            if not text:
                continue

            # Check for exit commands
            if text.lower() in ['quit', 'exit', 'q']:
                print("\n번역기를 종료합니다. (Exiting translator)")
                break

            # Detect language
            detected_lang = detect_language(text)

            if detected_lang == 'ko':
                src_lang, tgt_lang = 'ko', 'en'
                direction = "한글 → 영어"
            else:
                src_lang, tgt_lang = 'en', 'ko'
                direction = "영어 → 한글"

            print(f"\n[감지된 언어 방향: {direction}]")

            # Translate
            result = translator.translate(text, src_lang=src_lang, tgt_lang=tgt_lang)

            # Display result
            print(f"번역 결과 (Translation): {result}")
            print("-" * 60)
            print()

        except KeyboardInterrupt:
            print("\n\n번역기를 종료합니다. (Exiting translator)")
            break
        except Exception as e:
            logger.error(f"오류 발생 (Error): {e}")
            print()


def translate_text(translator: Translator, text: str, src_lang: str, tgt_lang: str, auto_detect: bool):
    """
    Translate a single text.

    Args:
        translator: Translator instance
        text: Text to translate
        src_lang: Source language
        tgt_lang: Target language
        auto_detect: Whether to auto-detect language
    """
    if auto_detect:
        detected_lang = detect_language(text)
        if detected_lang == 'ko':
            src_lang, tgt_lang = 'ko', 'en'
        else:
            src_lang, tgt_lang = 'en', 'ko'

    result = translator.translate(text, src_lang=src_lang, tgt_lang=tgt_lang)
    print(result)


def translate_file(translator: Translator, input_file: Path, output_file: Path,
                   src_lang: str, tgt_lang: str, auto_detect: bool):
    """
    Translate contents of a file.

    Args:
        translator: Translator instance
        input_file: Input file path
        output_file: Output file path
        src_lang: Source language
        tgt_lang: Target language
        auto_detect: Whether to auto-detect language
    """
    if not input_file.exists():
        logger.error(f"입력 파일을 찾을 수 없습니다 (Input file not found): {input_file}")
        sys.exit(1)

    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    logger.info(f"번역 중... (Translating {len(lines)} lines)")

    translated_lines = []
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            translated_lines.append("")
            continue

        if auto_detect:
            detected_lang = detect_language(line)
            if detected_lang == 'ko':
                current_src, current_tgt = 'ko', 'en'
            else:
                current_src, current_tgt = 'en', 'ko'
        else:
            current_src, current_tgt = src_lang, tgt_lang

        try:
            result = translator.translate(line, src_lang=current_src, tgt_lang=current_tgt)
            translated_lines.append(result)
            print(f"  [{i}/{len(lines)}] 완료 (Completed)", end='\r')
        except Exception as e:
            logger.error(f"라인 {i} 번역 실패 (Failed to translate line {i}): {e}")
            translated_lines.append(line)

    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(translated_lines))

    print()  # New line after progress
    logger.info(f"번역 완료! 결과 저장됨 (Translation complete! Saved to): {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="로컬 번역기 - 한글/영어 번역 (Local Translator - Korean/English)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제 (Examples):
  # 대화형 모드 (Interactive mode)
  python -m src.cli

  # 텍스트 직접 번역 (Direct text translation)
  python -m src.cli -t "Hello, World!"
  python -m src.cli -t "안녕하세요"

  # 언어 명시 (Specify languages)
  python -m src.cli -t "Hello" -s en -d ko

  # 파일 번역 (Translate file)
  python -m src.cli -f input.txt -o output.txt

  # GPU 사용 안함 (Disable GPU)
  python -m src.cli --no-gpu
        """
    )

    parser.add_argument(
        '-t', '--text',
        type=str,
        help='번역할 텍스트 (Text to translate)'
    )

    parser.add_argument(
        '-f', '--file',
        type=Path,
        help='번역할 파일 경로 (Input file path)'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='출력 파일 경로 (Output file path)'
    )

    parser.add_argument(
        '-s', '--source',
        type=str,
        default='en',
        choices=['en', 'ko'],
        help='원본 언어 (Source language, default: auto-detect)'
    )

    parser.add_argument(
        '-d', '--destination',
        type=str,
        default='ko',
        choices=['en', 'ko'],
        help='목적 언어 (Target language, default: auto-detect)'
    )

    parser.add_argument(
        '--auto-detect',
        action='store_true',
        default=True,
        help='언어 자동 감지 (Auto-detect language, default: True)'
    )

    parser.add_argument(
        '--no-auto-detect',
        action='store_false',
        dest='auto_detect',
        help='언어 자동 감지 비활성화 (Disable auto-detect)'
    )

    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='GPU 사용 안함 (Disable GPU)'
    )

    args = parser.parse_args()

    # Initialize translator
    try:
        logger.info("번역기 초기화 중... (Initializing translator...)")
        translator = Translator(use_gpu=not args.no_gpu)
        logger.info("번역기 준비 완료! (Translator ready!)")
        print()
    except Exception as e:
        logger.error(f"번역기 초기화 실패 (Failed to initialize translator): {e}")
        sys.exit(1)

    # Execute based on arguments
    if args.text:
        # Direct text translation
        translate_text(translator, args.text, args.source, args.destination, args.auto_detect)

    elif args.file:
        # File translation
        if not args.output:
            # Generate output filename
            output_file = args.file.parent / f"{args.file.stem}_translated{args.file.suffix}"
        else:
            output_file = args.output

        translate_file(translator, args.file, output_file, args.source, args.destination, args.auto_detect)

    else:
        # Interactive mode
        interactive_mode(translator)


if __name__ == '__main__':
    main()
