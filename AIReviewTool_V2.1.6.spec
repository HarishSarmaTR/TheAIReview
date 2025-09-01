# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['AIReview\\AIReview.py'],
    pathex=[],
    binaries=[],
    datas=[('images', 'images'), ('docs', 'docs'), ('blue.json', '.'), ('version_config.json', '.'), ('AIReview\\*.json', '.')],
    hiddenimports=[
        'api_handler',
        'usage_tracker', 
        'TokenExtraction',
        'github_token_extractor',
        'update_checker',
        'simple_reviewer',
        'requests',
        'github',
        'cryptography.fernet',
        'PIL.Image',
        'PIL.ImageTk',
        'customtkinter'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AIReviewTool_V2.1.6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    icon=['ai.ico'],
)
