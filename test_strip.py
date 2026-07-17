base_url = "https://integrate.api.nvidia.com/v1/chat/completions/"
if base_url:
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    if base_url.endswith("/chat/completions"):
        base_url = base_url[:-17]
    if base_url.endswith("/"):
        base_url = base_url[:-1]
print(f"FINAL BASE URL: {base_url}")
