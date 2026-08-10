from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_CLIENT = "anonymous"
SCHEME = "Bearer"


def verify_bearer_token(
    authorization: str | None = Header(default=None),
    x_client_id: str | None = Header(default=None),
) -> str:
    """Kiểm tra header Authorization; trả về client_id nếu hợp lệ."""
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or missing bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Thiếu header Authorization -> 401
    if not authorization:
        raise unauthorized_exc

    # 2. Tách scheme và token
    scheme, _, token = authorization.partition(" ")

    # 3. Kiểm tra scheme (không phân biệt hoa thường) và token rỗng -> 401
    if scheme.lower() != SCHEME.lower() or not token:
        raise unauthorized_exc

    # 4. So sánh token bằng compare_digest (chống Timing Attack)
    expected_token = get_settings().api_token
    if not secrets.compare_digest(token, expected_token):
        raise unauthorized_exc

    # 5. Hợp lệ: Trả về x_client_id hoặc ANONYMOUS_CLIENT
    return x_client_id if x_client_id else ANONYMOUS_CLIENT
