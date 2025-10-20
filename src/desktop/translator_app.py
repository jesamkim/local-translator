#!/usr/bin/env python3
"""
PyQt6 Desktop Application for Local Translator
macOS compatible translation app with modern UI
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QCheckBox, QSplitter,
    QStatusBar, QMessageBox, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QTextCursor

from src.translator import Translator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TranslationWorker(QThread):
    """Worker thread for translation to prevent UI freezing"""
    finished = pyqtSignal(str, str, str)  # translation, src_lang, tgt_lang
    error = pyqtSignal(str)

    def __init__(self, translator, text, src_lang, tgt_lang, auto_detect):
        super().__init__()
        self.translator = translator
        self.text = text
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.auto_detect = auto_detect

    def run(self):
        try:
            # Auto-detect language if enabled
            if self.auto_detect:
                detected_lang = self.detect_language(self.text)
                # Default target language is English for all Asian languages
                # Korean ↔ English (bidirectional)
                # Japanese → English
                # Chinese → English
                # English → Korean (default)
                if detected_lang == 'ko':
                    self.src_lang, self.tgt_lang = 'ko', 'en'
                elif detected_lang in ['ja', 'zh']:
                    self.src_lang, self.tgt_lang = detected_lang, 'en'
                else:  # English or other
                    self.src_lang, self.tgt_lang = 'en', 'ko'

            # Perform translation
            result = self.translator.translate(
                self.text,
                src_lang=self.src_lang,
                tgt_lang=self.tgt_lang
            )

            self.finished.emit(result, self.src_lang, self.tgt_lang)

        except Exception as e:
            logger.error(f"Translation error: {e}", exc_info=True)
            self.error.emit(str(e))

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Enhanced language detection for Korean, Japanese, Chinese, and English
        Returns: language code ('ko', 'ja', 'zh', or 'en')
        """
        if not text or not text.strip():
            return 'en'

        # Count characters for each language
        korean_chars = sum(1 for char in text if '\uac00' <= char <= '\ud7a3')

        # Japanese: Hiragana, Katakana, and some Kanji
        hiragana = sum(1 for char in text if '\u3040' <= char <= '\u309f')
        katakana = sum(1 for char in text if '\u30a0' <= char <= '\u30ff')
        japanese_chars = hiragana + katakana

        # Chinese: CJK Unified Ideographs (common Chinese characters)
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')

        # Total non-whitespace characters
        total_chars = len([char for char in text if char.strip()])

        if total_chars == 0:
            return 'en'

        # Calculate ratios
        korean_ratio = korean_chars / total_chars
        japanese_ratio = japanese_chars / total_chars
        chinese_ratio = chinese_chars / total_chars

        # Determine language (threshold: 20%)
        if korean_ratio > 0.2:
            return 'ko'
        elif japanese_ratio > 0.2:
            return 'ja'
        elif chinese_ratio > 0.2:
            return 'zh'
        else:
            return 'en'


class TranslatorApp(QMainWindow):
    """Main application window"""

    # Available languages
    LANGUAGES = {
        'ko': '한국어 (Korean)',
        'en': 'English',
        'ja': '日本語 (Japanese)',
        'zh': '中文 (Chinese)'
    }

    def __init__(self):
        super().__init__()
        self.translator = None
        self.worker = None
        self.current_src_lang = 'en'
        self.current_tgt_lang = 'ko'

        self.init_ui()
        self.init_translator()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('로컬 번역기 (Local Translator)')
        self.setGeometry(100, 100, 1000, 700)

        # Set window icon
        icon_path = Path(__file__).parent.parent.parent / 'icons' / 'icon.png'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Translation area (splitter for resizable panels)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Source panel
        source_panel = self.create_source_panel()
        splitter.addWidget(source_panel)

        # Target panel
        target_panel = self.create_target_panel()
        splitter.addWidget(target_panel)

        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)

        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Initializing translator...')

        # Apply styling
        self.apply_styles()

    def create_header(self):
        """Create header section"""
        header = QLabel('🌐 로컬 번역기 - Multilingual Translator\n한국어 ↔ English · 日本語 · 中文')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 20px;
                border-radius: 10px;
            }
        """)
        return header

    def create_source_panel(self):
        """Create source text panel"""
        group = QGroupBox('원문 (Source)')
        layout = QVBoxLayout()

        # Language label (shown when auto-detect is on)
        self.source_lang_label = QLabel('Auto-detect')
        self.source_lang_label.setStyleSheet("""
            QLabel {
                background-color: #667eea;
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-weight: bold;
            }
        """)

        # Language selector (shown when auto-detect is off)
        self.source_lang_combo = QComboBox()
        for code, name in self.LANGUAGES.items():
            self.source_lang_combo.addItem(name, code)
        self.source_lang_combo.setCurrentText(self.LANGUAGES['en'])
        self.source_lang_combo.currentIndexChanged.connect(self.on_source_lang_changed)
        self.source_lang_combo.setVisible(False)
        self.source_lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #667eea;
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #212529;
                border: 1px solid #dee2e6;
                selection-background-color: #667eea;
                selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: #212529;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #667eea;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8ebfd;
                color: #212529;
            }
        """)

        # Text edit
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText('번역할 텍스트를 입력하세요...\nEnter text to translate...')
        self.source_text.setFont(QFont('Arial', 12))
        self.source_text.textChanged.connect(self.update_char_count)

        # Character count
        self.char_count_label = QLabel('0 characters')
        self.char_count_label.setStyleSheet('color: #6c757d;')

        # Clear button
        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self.clear_text)
        clear_btn.setMaximumWidth(100)

        # Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.source_lang_label)
        top_layout.addWidget(self.source_lang_combo)
        top_layout.addStretch()
        top_layout.addWidget(clear_btn)

        layout.addLayout(top_layout)
        layout.addWidget(self.source_text)
        layout.addWidget(self.char_count_label)

        group.setLayout(layout)
        return group

    def create_target_panel(self):
        """Create target text panel"""
        group = QGroupBox('번역 (Translation)')
        layout = QVBoxLayout()

        # Language label (shown when auto-detect is on)
        self.target_lang_label = QLabel('-')
        self.target_lang_label.setStyleSheet("""
            QLabel {
                background-color: #764ba2;
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-weight: bold;
            }
        """)

        # Language selector (shown when auto-detect is off)
        self.target_lang_combo = QComboBox()
        for code, name in self.LANGUAGES.items():
            self.target_lang_combo.addItem(name, code)
        self.target_lang_combo.setCurrentText(self.LANGUAGES['ko'])
        self.target_lang_combo.currentIndexChanged.connect(self.on_target_lang_changed)
        self.target_lang_combo.setVisible(False)
        self.target_lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #764ba2;
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #212529;
                border: 1px solid #dee2e6;
                selection-background-color: #764ba2;
                selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: #212529;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #764ba2;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8ebfd;
                color: #212529;
            }
        """)

        # Text edit
        self.target_text = QTextEdit()
        self.target_text.setPlaceholderText('번역 결과가 여기에 표시됩니다...\nTranslation will appear here...')
        self.target_text.setFont(QFont('Arial', 12))
        self.target_text.setReadOnly(True)

        # Copy button
        copy_btn = QPushButton('Copy')
        copy_btn.clicked.connect(self.copy_translation)
        copy_btn.setMaximumWidth(100)

        # Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.target_lang_label)
        top_layout.addWidget(self.target_lang_combo)
        top_layout.addStretch()
        top_layout.addWidget(copy_btn)

        layout.addLayout(top_layout)
        layout.addWidget(self.target_text)

        group.setLayout(layout)
        return group

    def create_control_panel(self):
        """Create control panel"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Auto-detect checkbox
        self.auto_detect_cb = QCheckBox('언어 자동 감지 (Auto-detect language)')
        self.auto_detect_cb.setChecked(True)
        self.auto_detect_cb.setFont(QFont('Arial', 10))
        self.auto_detect_cb.stateChanged.connect(self.on_auto_detect_changed)

        # Swap button
        swap_btn = QPushButton('⇄ Swap')
        swap_btn.clicked.connect(self.swap_text)
        swap_btn.setMaximumWidth(100)

        # Translate button
        self.translate_btn = QPushButton('번역하기 (Translate)')
        self.translate_btn.clicked.connect(self.translate)
        self.translate_btn.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.translate_btn.setMinimumHeight(50)
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        layout.addWidget(self.auto_detect_cb)
        layout.addWidget(swap_btn)
        layout.addStretch()
        layout.addWidget(self.translate_btn)

        return widget

    def apply_styles(self):
        """Apply global styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QWidget {
                color: #212529;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
                color: #212529;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #495057;
            }
            QLabel {
                color: #212529;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                color: #212529;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
            QCheckBox {
                color: #212529;
            }
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #212529;
                background-color: white;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                background-color: #667eea;
                color: white;
            }
            QMessageBox QPushButton:hover {
                background-color: #5568d3;
            }
        """)

    def init_translator(self):
        """Initialize translator in background"""
        QTimer.singleShot(100, self._load_translator)

    def _load_translator(self):
        """Load translator model"""
        try:
            self.status_bar.showMessage('Loading translation model... This may take a minute.')
            self.translator = Translator(use_gpu=False)
            self.status_bar.showMessage('Ready! 번역 준비 완료', 3000)
            self.translate_btn.setEnabled(True)
            logger.info("Translator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize translator: {e}")
            self.status_bar.showMessage(f'Error: {e}')
            self._show_message_box('Error', f'Failed to load translator:\n{e}', QMessageBox.Icon.Critical)

    def translate(self):
        """Perform translation"""
        text = self.source_text.toPlainText().strip()

        if not text:
            self._show_message_box('Warning', 'Please enter text to translate.', QMessageBox.Icon.Warning)
            return

        if not self.translator:
            self._show_message_box('Warning', 'Translator is not ready yet.', QMessageBox.Icon.Warning)
            return

        # Disable button and show progress
        self.translate_btn.setEnabled(False)
        self.translate_btn.setText('번역 중... (Translating...)')
        self.status_bar.showMessage('Translating...')

        # Start translation in worker thread
        self.worker = TranslationWorker(
            self.translator,
            text,
            self.current_src_lang,
            self.current_tgt_lang,
            self.auto_detect_cb.isChecked()
        )
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.start()

    def on_translation_finished(self, translation, src_lang, tgt_lang):
        """Handle translation completion"""
        self.target_text.setPlainText(translation)

        # Language names mapping
        lang_names = {
            'ko': '한국어 (Korean)',
            'en': 'English',
            'ja': '日本語 (Japanese)',
            'zh': '中文 (Chinese)'
        }

        # Update language labels
        src_name = lang_names.get(src_lang, src_lang.upper())
        tgt_name = lang_names.get(tgt_lang, tgt_lang.upper())

        self.source_lang_label.setText(src_name)
        self.target_lang_label.setText(tgt_name)

        # Update current languages
        self.current_src_lang = src_lang
        self.current_tgt_lang = tgt_lang

        # Re-enable button
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText('번역하기 (Translate)')
        self.status_bar.showMessage('Translation completed! 번역 완료', 3000)

    def on_translation_error(self, error_msg):
        """Handle translation error"""
        self._show_message_box('Translation Error', f'Translation failed:\n{error_msg}', QMessageBox.Icon.Critical)
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText('번역하기 (Translate)')
        self.status_bar.showMessage('Translation failed')

    def clear_text(self):
        """Clear all text"""
        self.source_text.clear()
        self.target_text.clear()
        self.source_lang_label.setText('Auto-detect')
        self.target_lang_label.setText('-')

    def copy_translation(self):
        """Copy translation to clipboard"""
        text = self.target_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_bar.showMessage('Translation copied to clipboard! 복사 완료', 2000)
        else:
            self._show_message_box('Info', 'No translation to copy.', QMessageBox.Icon.Information)

    def swap_text(self):
        """Swap source and target text"""
        source = self.source_text.toPlainText()
        target = self.target_text.toPlainText()

        self.source_text.setPlainText(target)
        self.target_text.setPlainText(source)

        # Swap languages
        self.current_src_lang, self.current_tgt_lang = self.current_tgt_lang, self.current_src_lang

    def update_char_count(self):
        """Update character count"""
        count = len(self.source_text.toPlainText())
        self.char_count_label.setText(f'{count} characters')

    def on_auto_detect_changed(self, state):
        """Handle auto-detect checkbox state change"""
        is_checked = (state == Qt.CheckState.Checked)

        # Toggle visibility of labels vs combo boxes
        self.source_lang_label.setVisible(is_checked)
        self.source_lang_combo.setVisible(not is_checked)
        self.target_lang_label.setVisible(is_checked)
        self.target_lang_combo.setVisible(not is_checked)

        if is_checked:
            # Reset to auto-detect mode
            self.source_lang_label.setText('Auto-detect')
            self.target_lang_label.setText('-')
        else:
            # Set to manual mode with current selections
            src_code = self.source_lang_combo.currentData()
            tgt_code = self.target_lang_combo.currentData()
            self.current_src_lang = src_code
            self.current_tgt_lang = tgt_code
            logger.info(f"Manual mode: {src_code} -> {tgt_code}")

    def on_source_lang_changed(self, index):
        """Handle source language selection change"""
        src_code = self.source_lang_combo.currentData()
        tgt_code = self.target_lang_combo.currentData()

        # Prevent same language selection
        if src_code == tgt_code:
            # Find a different target language
            for code in self.LANGUAGES.keys():
                if code != src_code:
                    # Set target to a different language
                    idx = self.target_lang_combo.findData(code)
                    self.target_lang_combo.setCurrentIndex(idx)
                    tgt_code = code
                    break

        self.current_src_lang = src_code
        self.current_tgt_lang = tgt_code

    def on_target_lang_changed(self, index):
        """Handle target language selection change"""
        src_code = self.source_lang_combo.currentData()
        tgt_code = self.target_lang_combo.currentData()

        # Prevent same language selection
        if src_code == tgt_code:
            # Find a different source language
            for code in self.LANGUAGES.keys():
                if code != tgt_code:
                    # Set source to a different language
                    idx = self.source_lang_combo.findData(code)
                    self.source_lang_combo.setCurrentIndex(idx)
                    src_code = code
                    break

        self.current_src_lang = src_code
        self.current_tgt_lang = tgt_code

    def _show_message_box(self, title, message, icon):
        """Helper method to show styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Force style for dialog
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #212529;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 24px;
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5568d3;
            }
        """)

        msg_box.exec()

    def closeEvent(self, event):
        """Handle window close event"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle('Exit')
        msg_box.setText('Are you sure you want to exit?')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Force style for dialog
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #212529;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 24px;
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5568d3;
            }
        """)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName('Local Translator')
    app.setOrganizationName('LocalTranslator')

    window = TranslatorApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
