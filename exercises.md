# Phiếu Phản Ánh — K4 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay các câu hỏi bằng câu trả lời chi tiết của bạn.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Học viên  Mã học viên: K4-Day12

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `api_token` không có giá trị mặc định nên app chết ngay khi
khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà việc
"chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

* **Nếu để giá trị mặc định `"changeme"`:** Khi deploy ứng dụng lên môi trường Staging/Production mà lập trình viên hoặc DevOps quên khai báo biến môi trường `API_TOKEN`, ứng dụng vẫn khởi động thành công và các kiểm tra liveness/readiness (`/healthz`) đều báo `200 OK`. Hệ thống CI/CD đánh giá deployment thành công. Tuy nhiên, toàn bộ API của hệ thống lúc này đang mở ra với secret mặc định là `"changeme"`. Các bot tự động quét lỗ hổng hoặc kẻ tấn công có thể dễ dàng gửi request `Bearer changeme` để gọi vào service, gây thất thoát dữ liệu lịch sử chat hoặc tiêu tốn chi phí gọi LLM API. Bạn chỉ phát hiện sự cố khi hóa đơn Cloud tăng vọt hoặc dữ liệu bị rò rỉ.
* **Nếu không có giá trị mặc định (`api_token: str`):** Ngay khi ứng dụng khởi động, Pydantic Settings kiểm tra thiếu `API_TOKEN` và ném ra lỗi `ValidationError`. Ứng dụng lập tức "chết sớm" (Fail Fast) trước khi nhận bất kỳ lượt traffic nào. Tiến trình deploy trên CI/CD bị sập lập tức, container báo trạng thái `CrashLoopBackOff` hoặc `Failed`, báo hiệu ngay cho lập trình viên biết cần bổ sung secret trước khi tính năng nguy hiểm này có thể chạm tới môi trường thật.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/chat` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Dòng log JSON thu được từ service:
```json
{"timestamp": "2026-08-10T10:15:30.123456Z", "event": "chat_completed", "client_id": "alice", "prompt_tokens": 15, "completion_tokens": 32, "usd_cost": 0.00064}
```

Hai việc làm được với log JSON cấu trúc mà `print("đã trả lời xong")` không làm được:
1. **Truy vấn, lọc và gom nhóm chỉ số tự động trên các công cụ Log Management (Datadog, ELK, CloudWatch, Grafana Loki):**
   Vì log được định dạng chuẩn JSON có các trường key-value rõ ràng (`client_id`, `usd_cost`, `prompt_tokens`), các hệ thống phân tích log có thể tự động bóc tách và tạo dashboard/alert. Ví dụ: dễ dàng tính tổng chi phí `usd_cost` theo từng client trong ngày, hoặc thiết lập cảnh báo tự động gửi về Slack khi có client tiêu tốn hơn $1. Lệnh `print("đã trả lời xong")` chỉ là chuỗi văn bản không cấu trúc, bắt buộc phải viết regex phức tạp và dễ lỗi nếu chuỗi thay đổi.
2. **Theo vết phân tán (Distributed Tracing) và Kiểm toán an ninh (Security & Observability Auditing):**
   Log JSON tự động đính kèm thông tin định danh ngữ cảnh (`timestamp` chuẩn ISO 8601, ID người dùng `client_id`, tên sự kiện `event`). Điều này cho phép trace chính xác ai đã thực hiện request nào ở thời điểm nào, tiêu tốn bao nhiêu tài nguyên hệ thống. Trong khi đó, lệnh `print` thông thường hoàn toàn thiếu các thông tin định danh này, không thể dùng để đối soát hay kiểm toán an ninh.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t chat:single .
docker build -t chat:multi .
docker images | grep chat
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ~1.8 GB |
| Multi-stage | ~220 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Phần dung lượng chênh lệch khổng lồ (~1.58 GB) giữa hai bản bao gồm:
1. **Trình biên dịch và công cụ Build (Build toolchain & Compilers):** Base image chuẩn đầy đủ (`python:3.11`) chứa toàn bộ bộ công cụ biên dịch C/C++ (`gcc`, `g++`, `make`), bộ thư viện tiêu đề hệ thống (`python-dev`, `build-essential`), Git và các tiện ích dành cho quá trình biên dịch. Ở bản Multi-stage, các công cụ này chỉ nằm ở stage `builder` để cài đặt thư viện rồi bị loại bỏ hoàn toàn khỏi image final runtime.
2. **Bộ nhớ đệm (Pip cache & Build artifacts):** Trong single-stage build, toàn bộ cache tải về của `pip` và các file tạm sinh ra trong quá trình cài đặt gói python bị giữ lại trong image layers.
3. **Các thư viện hệ điều hành không cần thiết:** Bản Multi-stage sử dụng `python:3.11-slim` làm runtime base, lược bỏ hầu hết các gói Debian tiêu chuẩn không cần thiết (documentation, man pages, unused system libraries) và chỉ copy phần thư viện Python đã cài hoàn chỉnh (`/root/.local` sang `/home/appuser/.local`). Điều này giúp thu gọn kích thước image xuống dưới 400MB và giảm thiểu bề mặt tấn công an ninh (attack surface).

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

* **Với thứ tự Dockerfile chuẩn (COPY requirements.txt -> RUN pip install -> COPY . .):**
  * *Các layer được dùng lại từ Cache:* Tất cả các layer phía trên lệnh `COPY . .` bao gồm `FROM`, `WORKDIR`, `COPY requirements.txt .`, và lệnh tốn nhiều thời gian nhất là `RUN pip install ...` đều được Docker sử dụng lại từ build cache 100% vì checksum của `requirements.txt` không thay đổi.
  * *Các layer phải chạy lại:* Từ lệnh `COPY . .` (nơi Docker phát hiện file `app/main.py` bị sửa), layer này cùng tất cả các layer tiếp theo phía dưới (`RUN chown`, `ENV`, `USER`, `EXPOSE`, `HEALTHCHECK`, `CMD`) sẽ bị invalid cache và phải thực thi lại. Thời gian build lại chỉ mất 1-2 giây.
* **Nếu đặt `COPY . .` lên trước `RUN pip install`:**
  Khi sửa 1 ký tự trong `app/main.py`, checksum tại bước `COPY . .` lập tức bị thay đổi. Điều này khiến toàn bộ các layer đứng sau nó — bao gồm cả `RUN pip install` — bị mất cache và buộc phải chạy lại từ đầu. Docker sẽ phải tải và cài đặt lại toàn bộ thư viện Python trong `requirements.txt` mỗi lần bạn sửa code, làm quá trình build kéo dài lãng phí thời gian và băng thông.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

* **Chuỗi sự kiện khai thác nguy hiểm:**
  1. *Xuất phát từ lỗ hổng code:* Code Python chứa lỗ hổng thi hành lệnh từ xa (Remote Code Execution - RCE) thông qua `eval()`, `pickle.loads()`, hoặc gọi `subprocess` với tham số người dùng nhập vào.
  2. *Chiếm quyền trong Container:* Kẻ tấn công khai thác RCE để chạy lệnh shell bên trong container. Do container mặc định chạy bằng user `root` (UID 0), kẻ tấn công sở hữu đặc quyền tối cao trong container (có thể sửa đổi file hệ thống, cài mã độc, đọc dữ liệu môi trường).
  3. *Escaping khỏi Container lên máy Host:* Nếu container có cấu hình chia sẻ nguy hiểm với host (như mount ổ đĩa host, mount Docker socket `/var/run/docker.sock`, hoặc thông qua lỗ hổng Kernel Linux breakout), quyền root trong container sẽ tương đương với quyền `root` (UID 0) trên chính máy chủ Host. Kẻ tấn công lấy được quyền kiểm soát toàn bộ máy chủ vật lý/VPS host.
* **Lệnh `USER appuser` cắt đứt chuỗi ở đâu:**
  Lệnh `USER appuser` chuyển tiến trình ứng dụng sang chạy dưới một tài khoản người dùng thường không có đặc quyền (unprivileged user). Lệnh này cắt đứt chuỗi tấn công ngay tại **Bước 2**: Khi lỗ hổng RCE bị kích hoạt, lệnh shell bị thực thi chỉ có quyền hạn hạn chế của `appuser`. Kẻ tấn công không thể sửa file hệ thống container, không thể cài phần mềm độc hại yêu cầu root, và ngăn chặn triệt để khả năng leo thang quyền hạn (container breakout) lên máy Host.

---

### Câu 6 — Bearer token (CP3)

Vì sao 401 phải kèm header `WWW-Authenticate: Bearer`? Và vì sao ta trả **cùng
một** thông báo lỗi cho cả ba trường hợp (thiếu header, sai scheme, sai token)
thay vì nói rõ sai ở đâu cho người dùng dễ sửa?

1. **Vì sao 401 phải kèm `WWW-Authenticate: Bearer`:**
   Theo tiêu chuẩn HTTP RFC 7235 (Mục 4.1) và RFC 6750 (OAuth 2.0 Bearer Token Usage), khi Server trả về phản hồi `401 Unauthorized`, nó bắt buộc phải cung cấp header `WWW-Authenticate` để chỉ thị rõ cho phía Client (Browser, HTTP client, API Gateway) biết phương thức xác thực nào đang được ứng dụng yêu cầu (ở đây là `Bearer`). Giúp Client hiểu cách gửi lại request đúng chuẩn (ví dụ: kích hoạt luồng đăng nhập OAuth2).
2. **Vì sao trả CÙNG MỘT thông báo lỗi cho cả ba trường hợp:**
   Đây là nguyên tắc bảo mật tối quan trọng **Security by Design (Tránh rò rỉ thông tin - Information Disclosure / Enumeration Attacks)**.
   Nếu API trả về thông báo lỗi chi tiết như "Thiếu header Authorization", "Sai định dạng Bearer" hay "Token không tồn tại/đã hết hạn", kẻ tấn công có thể dựa vào phản hồi riêng biệt đó để:
   * Phân tích và hiểu rõ cấu trúc logic bảo mật nội bộ của hệ thống.
   * Thực hiện các cuộc tấn công dò quét (token enumeration/brute-force) để xác định token nào hợp lệ hoặc phân biệt giữa token sai định dạng và token bị hết hạn.
   Việc trả về chung một thông báo lỗi (ví dụ: `"Invalid or missing authentication token"`) giúp bảo vệ hệ thống, không để lộ bất kỳ manh mối nào cho kẻ tấn công.

---

### Câu 7 — Token bucket (CP3)

Với `capacity=10`, `refill_per_minute=10`: một client im lặng 10 phút rồi gửi
liên tiếp. Nó gửi được bao nhiêu request trước khi bị 429? Nếu bỏ đoạn
`min(capacity, ...)` trong `available()` thì con số đó thành bao nhiêu, và tại sao?

* **Với thuật toán chuẩn (có `min(capacity, ...)`):**
  Client gửi được tối đa **10 request** liên tiếp trước khi bị trả về lỗi `429 Too Many Requests`.
  *Lý do:* Cho dù client có im lặng 10 phút (theo thời gian lý thuyết có thể hồi $10 \text{ phút} \times 10 \text{ tokens/phút} = 100 \text{ tokens}$), hàm `min(capacity, ...)` khống chế số lượng token khả dụng không bao giờ được phép vượt quá dung tích tối đa của xô (`capacity = 10`).
* **Nếu bỏ đoạn `min(capacity, ...)` trong `available()`:**
  Con số request gửi được sẽ tăng vọt lên **100 request** (hoặc 101 tùy thuộc lượng fraction refill trong lúc gửi).
  *Tại sao:* Khi không có giới hạn `min(capacity, ...)`, số token sẽ bị dồn tích vô hạn theo thời gian im lặng ($0 + 10 \times 10 = 100$ tokens). Điều này làm vô hiệu hóa hoàn toàn cơ chế bảo vệ của Token Bucket, tạo ra lỗ hổng cho các đợt tấn công bùng nổ traffic (burst attack / traffic spike), gây sập hệ thống sau một khoảng thời gian client im lặng "nằm vùng".

---

### Câu 8 — Ngân sách theo ngày (CP3)

So sánh hạn mức $30/tháng với hạn mức $1/ngày cho cùng một client. Giả sử có sự
cố khiến một client gọi liên tục từ 2h sáng. Với mỗi cách, thiệt hại tối đa là
bao nhiêu và service tự hồi phục khi nào?

* **Với hạn mức $30/tháng:**
  * *Thiệt hại tối đa:* Toàn bộ ngân sách **$30** sẽ bị đốt sạch chỉ trong vòng vài phút/vài giờ đầu tiên của sự cố từ 2h sáng.
  * *Thời điểm tự hồi phục:* Service sẽ chặn hoàn toàn client đó (trả về 402 Payment Required) trong **suốt thời gian còn lại của tháng** (cho tới ngày đầu tiên của tháng sau khi ngân sách tháng được reset). Client bị gián đoạn dịch vụ kéo dài cả tháng.
* **Với hạn mức $1/ngày:**
  * *Thiệt hại tối đa:* Thiệt hại bị khống chế tối đa chỉ là **$1** cho ngày xảy ra sự cố. Ngay khi chi phí chạm mốc $1, Cost Guard sẽ lập tức chặn request.
  * *Thời điểm tự hồi phục:* Service sẽ tự động khôi phục dịch vụ cho client đó vào **00:00:00 UTC của ngày hôm sau** (khi key ngân sách ngày trong Redis hết hạn TTL 24h hoặc được reset).
* **Kết luận:** Hạn mức theo ngày tuân thủ nguyên tắc giảm thiểu bán kính thiệt hại (Blast Radius Reduction), ngăn chặn tình trạng một script lỗi đốt sạch ngân sách cả tháng trong một đêm và hỗ trợ tự khôi phục nhanh theo chu kỳ 24 giờ.

---

### Câu 9 — /healthz khác /readyz (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Thứ tự diễn biến sự cố khi gộp 2 endpoint làm một và kiểm tra Redis:

1. **Thời điểm T = 0s (Sự cố Redis):** Kết nối tới Redis bị gián đoạn hoặc Redis bị treo trong 30 giây.
2. **Thời điểm T = 5s - 10s (Liveness Probe thất bại):** Orchestrator (Docker Swarm/Kubernetes/Cloud Platform) định kỳ gọi Liveness Probe (lúc này đã gộp chung với readyz) tới 3 container. Do Redis chết, endpoint trả về lỗi HTTP 500/503 hoặc bị timeout.
3. **Thời điểm T = 15s - 20s (Tiêu diệt và khởi động lại container):** Nhận thấy Liveness Probe báo thất bại liên tiếp (quá số lần `failureThreshold`), Orchestrator kết luận cả 3 container app đã chết và ra lệnh **kill & restart (khởi động lại) đồng loạt cả 3 container**.
4. **Thời điểm T = 20s - 30s (Vòng lặp khởi động vô tận - CrashLoopBackOff):** Các container mới khởi động lại tiếp tục thực hiện Liveness check khi khởi tạo. Vì Redis vẫn chưa sống lại (đang trong 30s sự cố), các container mới lại tiếp tục báo lỗi và lại bị Orchestrator kill & restart liên tục.
5. **Thời điểm T > 30s (Thảm họa quá tải khi Redis vừa hồi phục):** Ngay cả khi Redis vừa hoạt động trở lại sau 30s, cả 3 container app vẫn đang trong trạng thái restart/down. Traffic của toàn bộ người dùng bị nghẽn và ồ ạt tràn vào cùng lúc khi container mở lại, gây sập cục bộ (Cascading Failure).

*Kết luận:* `/healthz` (Liveness) chỉ được kiểm tra nội tại tiến trình app để quyết định restart; còn `/readyz` (Readiness) mới được kiểm tra dependency (Redis) để ngắt traffic tạm thời mà KHÔNG kill container.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

* **Tên lỗi gặp phải:** App không đọc cổng từ biến môi trường `$PORT` do Cloud Platform cấp (Render / Railway / Cloud Run).
* **Thông báo lỗi trong Log:**
  `Error: Timed out waiting for container to respond on port 10000` hoặc `Application failed to respond on PORT assigned by platform`.
* **Cách tìm ra nguyên nhân:**
  1. Vào trang quản trị Dashboard của Cloud Platform, xem mục Runtime Logs.
  2. Quan sát thấy dòng log của ứng dụng: `INFO: Uvicorn running on http://0.0.0.0:8000`.
  3. Nhận ra Cloud Platform tự động cấp một cổng ngẫu nhiên thông qua biến môi trường `PORT` (ví dụ `PORT=10000`), nhưng ứng dụng lại hardcode chạy ở cổng `8000`. Router của Cloud không thể chuyển tiếp (forward) traffic vào container dẫn tới timeout healthcheck.
* **Cách khắc phục:**
  Sửa code khởi chạy Uvicorn trong `app/main.py` hoặc lệnh CMD trong `Dockerfile` để đọc linh hoạt biến môi trường `PORT`:
  ```python
  import os
  port = int(os.getenv("PORT", 8000))
  uvicorn.run(app, host="0.0.0.0", port=port)
  ```
  Và trong `Dockerfile`:
  ```dockerfile
  CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
  ```
