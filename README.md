# LAN Drop

A small HTTP file-sharing service for trusted local networks. It supports JSON listings, downloads, and size-limited uploads without external packages.

```powershell
$env:PYTHONPATH = "src"
python -m lan_drop.server --folder shared --port 8080
Invoke-RestMethod "http://127.0.0.1:8080/files"
Invoke-WebRequest -Method Put -Uri "http://127.0.0.1:8080/files/hello.txt" -Body "hello"
Invoke-WebRequest "http://127.0.0.1:8080/files/hello.txt" -OutFile hello.txt
```

Uploads are limited to 10 MB, existing files are not replaced, and paths outside the shared folder are blocked. Bind to `0.0.0.0` only on a trusted network. This is a learning project, not a public internet server.

