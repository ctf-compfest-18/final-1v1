import base64
import zlib
from pathlib import Path


source = Path("original.py").read_bytes()
payload = base64.b64encode(zlib.compress(source)).decode()
Path("chall.py").write_text(
    "import base64,zlib\n"
    f'eval(compile(zlib.decompress(base64.b64decode("{payload}")),"<chall>","exec"))\n'
)
