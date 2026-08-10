# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị token vào đây.**
> Repo này công khai — dán token vào là mất token.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Hoàng Văn Quang |
| Mã học viên | 2A202601334 |
| Repo | https://github.com/kaiosz02/K4-Day12-2A202601334-HoangVanQuang.git |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-chat-app.onrender.com/ |
| Platform | Render |
| Ngày deploy | 10/8/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán |
| `API_TOKEN` | ✅ | đặt trong dashboard, không nằm trong repo |
| `REDIS_URL` | ✅ | redis://red-d9sq0f2fngtc73fqs2rg:6379 |
| `BUCKET_CAPACITY` | ✅ | 10 |
| `REFILL_PER_MINUTE` | ✅ | 10 |
| `DAILY_BUDGET_USD` | ✅ | 1.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

Thay `<URL>` bằng Public URL ở trên:

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i <URL>/healthz

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i <URL>/readyz

# 3. Không có token — mong đợi 401 kèm header WWW-Authenticate
curl -i -X POST <URL>/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'

# 4. Có token — mong đợi 200 kèm câu trả lời
curl -i -X POST <URL>/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "X-Client-Id: sv-test" \
  -d '{"message":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST <URL>/chat \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "X-Client-Id: sv-test" \
    -d '{"message":"test"}'
done; echo
```

## Kết Quả Chạy Thật

Dán output của các lệnh trên vào đây:


# 1. Liveness — mong đợi 200 {"status":"ok"}
HTTP/1.1 200 OK
Date: Mon, 10 Aug 2026 10:14:53 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
rndr-id: 0599124c-1350-4644
Server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
CF-RAY: a28e3c7afd9aff47-SIN
alt-svc: h3=":443"; ma=86400
{"status":"ok","service":"day12-chat-service","version":"1.0.0"}

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
HTTP/1.1 200 OK
Date: Mon, 10 Aug 2026 10:16:31 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
rndr-id: 98f47326-ec49-4ec6
Server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
CF-RAY: a28e3edbb847e2fb-HKG
alt-svc: h3=":443"; ma=86400
{"status":"ready","redis":true}

# 3. Không có token — mong đợi 401 kèm header WWW-Authenticate
HTTP/1.1 422 Unprocessable Entity
Date: Mon, 10 Aug 2026 10:19:13 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
rndr-id: be19f706-9e5f-43a1
Server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
CF-RAY: a28e42d1fd7c3d7d-SIN
alt-svc: h3=":443"; ma=86400

{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}

# 4. Có token — mong đợi 200 kèm câu trả lời
PS D:\thuc_hanh_vinAI\K4-Day12-Cloud-Services-And-Deployment> curl.exe -i -X POST https://day12-chat-app.onrender.com/chat -H "Content-Type: application/json" -H "Authorization: Bearer <API_TOKEN_CỦA_BẠN>" -H "X-Client-Id: sv-test" -d "{`"message`":`"Deploy là gì?`"}"
HTTP/1.1 422 Unprocessable Entity
Date: Mon, 10 Aug 2026 10:20:50 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
rndr-id: 5e47d734-3572-409e
Server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
CF-RAY: a28e452f5a7580f7-SIN
alt-svc: h3=":443"; ma=86400

{"detail":[{"type":"json_invalid","loc":["body",1],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform
- `screenshots/healthz.png` — kết quả gọi `/healthz` từ trình duyệt hoặc curl

---

## Nếu Dùng Phương Án Dự Phòng

Không đăng ký được tài khoản cloud? Vẫn nộp được bài, nhưng CP5 tối đa 60% điểm:

1. Đặt `LOCAL_FALLBACK=true` trong `.env`
2. Chạy `docker compose up -d` rồi kiểm tra `docker compose ps`
3. Chụp màn hình vào `screenshots/`
4. Chạy `pytest tests/test_cp5.py -v` — bộ test sẽ tự chuyển sang kiểm tra
   `http://localhost:8000`
5. Ghi rõ lý do không deploy được vào phần dưới đây:

```
(điền lý do nếu dùng phương án dự phòng, ngược lại xóa mục này)
```
