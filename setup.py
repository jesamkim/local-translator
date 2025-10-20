from setuptools import setup
import sys

# Increase recursion limit for py2app
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
