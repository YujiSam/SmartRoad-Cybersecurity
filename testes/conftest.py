import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(_tmp, "teste.db")
os.environ["AUDITORIA_PATH"] = os.path.join(_tmp, "auditoria.jsonl")
os.environ["USAR_LLM"] = "false"
