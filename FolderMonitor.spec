# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['_bz2', '_lzma', '_ssl', '_socket', 'PIL', 'numpy', 'urllib', '_bz2', '_lzma', '_ssl', '_socket', 'PIL', 'numpy', 'http.client', 'pandas', 'xmlrpc', 'unittest', 'test', 'pdb', 'notebook', 'matplotlib', 'pytz', '_decimal', '_sqlite3', '_uuid', '_zoneinfo', '_ssl', '_queue', '_msi', '_ctypes', '_ctypes_test', '_elementtree', '_hashlib', '_msi', '_multiprocessing', '_overlapped', '_queue', '_ssl', '_testbuffer', '_testcapi', '_testconsole', '_testinternalcapi', '_testimportmultiple', '_testmultiphase', 'libffi', 'libssl-1_1', 'pyexpat', 'select', 'scipy', 'setuptools', 'hook', 'distutils', 'site', 'hooks', 'tornado', 'PIL', 'PyQt4', 'PyQt5', 'pydoc', 'pythoncom', 'pytz', 'pywintypes', 'sqlite3', 'pyz', 'pandas', 'sklearn', 'scapy', 'scrapy', 'sympy', 'kivy', 'pyramid', 'opencv', 'tensorflow', 'pipenv', 'pattern', 'mechanize', 'beautifulsoup4', 'requests', 'wxPython', 'pygi', 'pillow', 'pygame', 'pyglet', 'flask', 'django', 'pylint', 'pytube', 'odfpy', 'mccabe', 'pilkit', 'six', 'wrapt', 'astroid', 'isort', 'lib2to3', 'pydoc'],
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
    name='FolderMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
