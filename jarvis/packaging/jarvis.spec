from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


ROOT = Path(SPECPATH).parent

# Keep package resources (the benchmark YAML files and prices.toml) alongside
# the frozen package. Mutable state is deliberately not copied from jarvis_data.
datas = collect_data_files("jarvis", include_py_files=False)
datas += collect_data_files("winrt", include_py_files=False)
datas.append((str(ROOT / "jarvis.toml"), "."))
for skill in (ROOT / "jarvis_data" / "skills").glob("*.yaml"):
    datas.append((str(skill), "jarvis_data/skills"))

hiddenimports = collect_submodules("jarvis")
hiddenimports += [
    "wave",
    "scipy",
    "sklearn",
    "winrt.windows.foundation",
    "winrt.windows.media.playback",
    "winrt.windows.media.speechsynthesis",
]

analysis = Analysis(
    [str(ROOT / "jarvis" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tests", "onnxruntime", "openwakeword", "moonshine_voice"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="jarvis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="jarvis",
)
