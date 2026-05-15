"""
JLCPCB Fabrication Toolkit CLI wrapper
- BOM, CPL, Gerber ZIP 을 production/ 폴더에 자동 생성
- 사용: python fabricate.py
- 또는: 프로젝트 루트에서 더블클릭 (fabricate.bat 사용)

요구사항:
  - KiCad 10 설치 (python.exe 포함)
  - Fabrication Toolkit 플러그인 설치 (KiCad Plugin Manager)
"""

import sys
import os
import shutil
import time
import types
import importlib.util

# ── 1. 경로 설정 ──────────────────────────────────────────────────
KICAD_BIN   = r"C:\Program Files\KiCad\10.0\bin"
PLUGIN_ROOT = r"C:\Users\SEOP\Documents\KiCad\10.0\3rdparty\plugins"
PLUGIN_DIR  = os.path.join(PLUGIN_ROOT, "com_github_bennymeg_JLC-Plugin-for-KiCad")
BOARD_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usbc_charger.kicad_pcb")
OUT_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "production")
ARCHIVE_NAME = "usbc_charger_jlc"

# KiCad bin을 PATH 앞에 삽입 (pcbnew DLL 로드)
os.environ["PATH"] = KICAD_BIN + os.pathsep + os.environ.get("PATH", "")
sys.path.insert(0, KICAD_BIN + r"\Lib\site-packages")

# ── 2. pcbnew 로드 ────────────────────────────────────────────────
import pcbnew  # type: ignore

# CLI 모드에서 pcbnew.GetBoard()가 None을 반환하는 버그 우회:
# 보드를 미리 로드하고 GetBoard를 monkey-patch
board = pcbnew.LoadBoard(BOARD_FILE)
_original_GetBoard = pcbnew.GetBoard
pcbnew.GetBoard = lambda: board

# ── 3. Fabrication Toolkit 패키지를 alias로 로드 ─────────────────
# 폴더명에 하이픈이 있어 일반 import 불가 → importlib 수동 로드
ALIAS = "ft_plugin"
pkg = types.ModuleType(ALIAS)
pkg.__path__ = [PLUGIN_DIR]
pkg.__package__ = ALIAS
sys.modules[ALIAS] = pkg

for mod_name in ["config", "options", "utils", "events", "process", "thread"]:
    fp = os.path.join(PLUGIN_DIR, mod_name + ".py")
    spec = importlib.util.spec_from_file_location(f"{ALIAS}.{mod_name}", fp)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = ALIAS
    sys.modules[f"{ALIAS}.{mod_name}"] = mod
    spec.loader.exec_module(mod)

from ft_plugin.thread import ProcessThread
from ft_plugin.options import (
    AUTO_TRANSLATE_OPT, AUTO_FILL_OPT, EXCLUDE_DNP_OPT,
    EXTEND_EDGE_CUT_OPT, ALTERNATIVE_EDGE_CUT_OPT, ALL_ACTIVE_LAYERS_OPT,
    ARCHIVE_NAME as ARCHIVE_NAME_OPT, EXTRA_LAYERS, NO_BACKUP_OPT,
)

# ── 4. Fabrication Toolkit 실행 ───────────────────────────────────
options = {
    AUTO_TRANSLATE_OPT:         True,   # 회전 자동 보정
    AUTO_FILL_OPT:              True,   # 존 자동 채우기
    EXCLUDE_DNP_OPT:            True,   # DNP 부품 BOM 제외
    EXTEND_EDGE_CUT_OPT:        False,
    ALTERNATIVE_EDGE_CUT_OPT:   False,
    ALL_ACTIVE_LAYERS_OPT:      False,
    ARCHIVE_NAME_OPT:           ARCHIVE_NAME,
    EXTRA_LAYERS:               None,
    NO_BACKUP_OPT:              True,   # 백업 ZIP 생성 안 함
}

print(f"[FT] 보드: {BOARD_FILE}")
print(f"[FT] 아카이브 이름: {ARCHIVE_NAME}")

t = ProcessThread(
    wx=None,
    cli=BOARD_FILE,
    options=options,
    openBrowser=False,
    nonInteractive=True,
)
t.join()  # 완료 대기

# ── 5. 생성 파일을 production/ 폴더로 이동 ───────────────────────
project_dir = os.path.dirname(BOARD_FILE)
os.makedirs(OUT_DIR, exist_ok=True)

moved = []
patterns = [
    f"{ARCHIVE_NAME}.zip",
    f"{ARCHIVE_NAME}-gerbers.zip",
    f"{ARCHIVE_NAME}_bom.csv",
    f"{ARCHIVE_NAME}_positions.csv",
    f"{ARCHIVE_NAME}_designators.csv",
    "netlist.ipc",
]
# 프로젝트 폴더에서 생성된 파일 탐색 (archive_name 기준으로 매칭)
for fname in os.listdir(project_dir):
    src = os.path.join(project_dir, fname)
    if not os.path.isfile(src):
        continue
    name_lower = fname.lower()
    archive_lower = ARCHIVE_NAME.lower()
    if (name_lower == "netlist.ipc") or \
       (archive_lower in name_lower and (name_lower.endswith(".zip") or name_lower.endswith(".csv"))):
        dst = os.path.join(OUT_DIR, fname)
        shutil.move(src, dst)
        moved.append(fname)

if moved:
    print(f"\n[FT] production/ 으로 이동한 파일:")
    for f in moved:
        print(f"  → {f}")
else:
    print("\n[FT] 이동할 파일 없음 (이미 production/에 있거나 생성 실패)")

print(f"\n[FT] 완료. 출력 폴더: {OUT_DIR}")
