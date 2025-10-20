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
    QStatusBar, QMessageBox, QGroupBox
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
                if detected_lang == 'ko':
                    self.src_lang, self.tgt_lang = 'ko', 'en'
                else:
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
        """Simple language detection"""
        korean_chars = sum(1 for char in text if '\uac00' <= char <= '\ud7a3')
        total_chars = len([char for char in text if char.strip()])

        if total_chars == 0:
            return 'en'

        korean_ratio = korean_chars / total_chars
        return 'ko' if korean_ratio > 0.3 else 'en'


class TranslatorApp(QMainWindow):
    """Main application window"""

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
        header = QLabel('🌐 로컬 번역기 - Korean ↔ English Translator')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont('Arial', 18, QFont.Weight.Bold))
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

        # Language label
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

        # Language label
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
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #667eea;
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
            QMessageBox.critical(self, 'Error', f'Failed to load translator:\n{e}')

    def translate(self):
        """Perform translation"""
        text = self.source_text.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, 'Warning', 'Please enter text to translate.')
            return

        if not self.translator:
            QMessageBox.warning(self, 'Warning', 'Translator is not ready yet.')
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

        # Update language labels
        src_name = '한국어 (Korean)' if src_lang == 'ko' else 'English'
        tgt_name = '한국어 (Korean)' if tgt_lang == 'ko' else 'English'

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
        QMessageBox.critical(self, 'Translation Error', f'Translation failed:\n{error_msg}')
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
            QMessageBox.information(self, 'Info', 'No translation to copy.')

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

    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            'Exit',
            'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

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
