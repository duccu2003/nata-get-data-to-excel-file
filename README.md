# NATA - Get Data To Excel File

API FastAPI để nhận dữ liệu JSON và xuất file Excel (`.xlsx`) dựa trên template có sẵn.

## 1) Tổng quan

Project hiện tại tập trung vào endpoint:

- `POST /excel/generate-excel/`: tạo file Excel từ payload đầu vào.
- `GET /`: health check đơn giản.

`/invoice` đã được khai báo router nhưng các endpoint bên trong đang comment (chưa sử dụng).

## 2) Công nghệ sử dụng

- Python
- FastAPI + Uvicorn
- openpyxl
- flatten-dict
- Docker / Docker Compose

## 3) Cấu trúc thư mục

```text
.
|-- app/
|   |-- main.py
|   |-- middleware.py
|   |-- routes/
|   |   |-- excel.py
|   |   `-- invoice.py
|   |-- utils/
|   |   |-- excel_utils.py
|   |   `-- mapping.py
|   `-- models/
|       `-- template_data.py
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- temp.xlsx
```

## 4) Hệ điều hành hỗ trợ

Project có thể chạy trên:

- Windows
- macOS
- Linux

Điều kiện:

- Python 3.11 khuyến nghị (để đồng nhất với Docker image `python:3.11-slim`)
- Hoặc dùng Docker/Docker Compose (khuyến nghị khi deploy)

## 5) Cài đặt và chạy local

### 5.1 Yêu cầu

- Đã cài Python 3.11+
- Có file template `temp.xlsx` ở thư mục gốc project

### 5.2 Cài đặt dependency

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5.3 Chạy ứng dụng

Từ thư mục gốc project, chạy:

```bash
python app/main.py
```

Hoặc chạy trực tiếp bằng `uvicorn` (khuyến nghị khi phát triển):

Windows (PowerShell):

```powershell
uvicorn main:app --app-dir app --host 0.0.0.0 --port 8000 --reload
```

macOS/Linux:

```bash
uvicorn main:app --app-dir app --host 0.0.0.0 --port 8000 --reload
```

Mặc định app lắng nghe tại:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## 6) Hướng dẫn API

### 6.1 Health check

- Method: `GET`
- URL: `/`

Kết quả mẫu:

```json
{
  "message": "Welcome to FastAPI!"
}
```

### 6.2 Tạo file Excel

- Method: `POST`
- URL: `/excel/generate-excel/`
- Content-Type: `application/json`

Payload mẫu (dùng map placeholder trực tiếp):

```json
{
  "replacements": {
    "1": "SUNWOOD VIETNAM",
    "2": "PC-001",
    "3": "2026-03-17",
    "20": "120",
    "21": "1000",
    "DPL": "[{\"contNo\":\"ABCD1234567\",\"sealNo\":\"SEAL001\",\"weightNet\":1000,\"weightGross\":1020}]",
    "CSHT": "[{\"bookingNumber\":\"BK001\",\"contNo\":\"ABCD1234567\",\"sealNo\":\"SEAL001\",\"weightNet\":1000,\"weightGross\":1020}]"
  }
}
```

Lưu ý quan trọng:

- `DPL` và `CSHT` phải là JSON string (không phải array thường), vì code đang dùng `json.loads(...)`.
- API trả về trực tiếp file `.xlsx` (`FileResponse`).

## 7) Thư mục output

- Khi chạy local bằng `python app/main.py`, file output được tạo trong `app/temp/`.
- Khi chạy bằng Docker Compose, thư mục host `./temp` được mount vào container `/app/temp`.

## 8) Deploy bằng Docker (khuyến nghị)

### 8.1 Chạy với Docker Compose

```bash
docker compose up -d --build
```

Service map port:

- Host `6060` -> Container `8000`

Sau khi chạy:

- API: `http://localhost:6060`
- Docs: `http://localhost:6060/docs`

### 8.2 Dùng Docker command thường

Build image:

```bash
docker build -t nata-excel-api .
```

Run container:

```bash
docker run -d \
  -p 6060:8000 \
  -v ${PWD}/temp.xlsx:/app/temp.xlsx \
  -v ${PWD}/temp:/app/temp \
  --name nata-excel-api \
  nata-excel-api
```

## 9) Checklist deploy production

- Đặt reverse proxy (Nginx/Traefik) trước app.
- Giới hạn CORS theo domain frontend (hiện tại đang `allow_origins=["*"]`).
- Đặt log rotation nếu deploy lâu dài.
- Theo dõi dung lượng thư mục output `temp`.
- Backup/quản lý file template `temp.xlsx`.

## 10) Lỗi thường gặp

1. `Template file not found`
- Kiểm tra file `temp.xlsx` có tồn tại đúng vị trí hay không.
- Nếu chạy Docker, kiểm tra volume mount `./temp.xlsx:/app/temp.xlsx`.

2. `Invalid DPL data format` hoặc `Invalid CSHT data format`
- Kiểm tra `DPL`/`CSHT` có phải JSON string hợp lệ không.

3. Port bị trùng
- Đổi port host trong `docker-compose.yml` (ví dụ `7070:8000`).

## 11) Lệnh nhanh để test

```bash
curl -X POST "http://localhost:6060/excel/generate-excel/" \
  -H "Content-Type: application/json" \
  -d "{\"replacements\":{\"1\":\"SUNWOOD VIETNAM\",\"2\":\"PC-001\",\"20\":\"120\",\"21\":\"1000\"}}" \
  --output output.xlsx
```

---

Nếu cần, có thể bổ sung thêm:

- file `.env` + cấu hình biến môi trường
- endpoint health check nâng cao (`/healthz`, `/readyz`)
- CI/CD (GitHub Actions) cho build và deploy tự động
