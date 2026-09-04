import hashlib, json
from pathlib import Path
from urllib.parse import unquote

def safe_path(root: Path,name: str) -> Path:
    root=root.resolve(); target=(root/unquote(name).lstrip("/\\")).resolve()
    if target==root or root not in target.parents: raise ValueError("unsafe file path")
    return target

class Storage:
    def __init__(self,root: Path,max_bytes: int=10*1024*1024): self.root=root; self.max_bytes=max_bytes; root.mkdir(parents=True,exist_ok=True)
    def list(self):
        return [{"name":p.name,"size":p.stat().st_size} for p in sorted(self.root.iterdir()) if p.is_file()]
    def save(self,name: str,data: bytes):
        if len(data)>self.max_bytes: raise ValueError("file is too large")
        target=safe_path(self.root,name)
        if target.exists(): raise FileExistsError("file already exists")
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        return {"name":target.name,"size":len(data),"sha256":hashlib.sha256(data).hexdigest()}
    def read(self,name: str) -> bytes: return safe_path(self.root,name).read_bytes()

