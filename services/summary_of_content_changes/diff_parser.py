def parse_diff_id(body: bytes) -> int | None:
    # Parses the message body and returns a valid diff_id or None.
    try:
        decoded = body.decode().strip()
        if decoded.isdigit():
            return int(decoded)
        else:
            return None
    except Exception:
        return None
