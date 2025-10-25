# 🤖 Stock Alert Bot - Telegram Bot Cảnh Báo Giá Cổ Phiếu

Bot Telegram giúp theo dõi giá cổ phiếu Việt Nam và gửi thông báo khi đạt ngưỡng giá mong muốn.

## ✨ Tính năng

- ✅ Đặt cảnh báo giá cổ phiếu (1 chiều: giá >= mục tiêu)
- ✅ Kiểm tra giá mỗi 10 giây
- ✅ Tự động xóa alert sau khi kích hoạt
- ✅ Kiểm tra giá realtime từ VietStock API
- ✅ Validate mã cổ phiếu
- ✅ Lưu trữ alerts bằng SQLite

## 📋 Yêu cầu

- Python 3.8+
- Telegram Bot Token (từ @BotFather)

## 🚀 Cài đặt

### 1. Clone/Download code

```bash
cd stock-alert-bot
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình Bot Token

Mở file `config.py` và thay thế token của bạn:

```python
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
```

Hoặc dùng biến môi trường:

```bash
export BOT_TOKEN='your_telegram_bot_token'
```

### 4. Chạy bot

```bash
python bot.py
```

## 📱 Cách sử dụng

### Các lệnh cơ bản:

1. **Đặt cảnh báo:**
   ```
   /alert HPG 25 500
   ```
   → Nhận thông báo khi HPG đạt ≥ 25,500 VNĐ

2. **Xem danh sách alerts:**
   ```
   /list
   ```

3. **Xóa cảnh báo:**
   ```
   /remove HPG
   ```

4. **Kiểm tra giá hiện tại:**
   ```
   /price HPG
   ```

5. **Xem hướng dẫn:**
   ```
   /guide
   ```
   
6. **Danh sách lệnh:**
   ```
   /help
   ```

## 🌐 Deploy lên Server/VPS

### Option 1: Deploy lên Railway.app (Free)

1. Đăng ký tài khoản tại [Railway.app](https://railway.app)
2. Tạo New Project → Deploy from GitHub
3. Thêm biến môi trường:
   - `BOT_TOKEN`: your_bot_token
4. Railway sẽ tự động deploy và chạy 24/7

### Option 2: Deploy lên Render.com (Free)

1. Đăng ký tại [Render.com](https://render.com)
2. New → Background Worker
3. Connect repository
4. Add environment variable: `BOT_TOKEN`
5. Deploy

### Option 3: VPS/Server riêng

```bash
# 1. Copy code lên server
scp -r stock-alert-bot user@your-server:/home/user/

# 2. SSH vào server
ssh user@your-server

# 3. Cài đặt dependencies
cd /home/user/stock-alert-bot
pip3 install -r requirements.txt

# 4. Tạo systemd service (chạy background)
sudo nano /etc/systemd/system/stockbot.service
```

Nội dung file service:

```ini
[Unit]
Description=Stock Alert Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/stock-alert-bot
Environment="BOT_TOKEN=your_bot_token_here"
ExecStart=/usr/bin/python3 /home/user/stock-alert-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Khởi động service:

```bash
sudo systemctl enable stockbot
sudo systemctl start stockbot
sudo systemctl status stockbot
```

### Option 4: Docker (Recommended)

Tạo file `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Chạy với Docker:

```bash
docker build -t stock-alert-bot .
docker run -d --name stock-bot -e BOT_TOKEN='your_token' stock-alert-bot
```

## 🔧 Cấu hình nâng cao

Trong file `config.py`:

```python
# Thời gian kiểm tra giá (giây)
CHECK_INTERVAL = 10  # Mặc định 10 giây

# Thay đổi nguồn API (nếu cần)
SSI_API_URL = 'https://finfo-api.vndirect.com.vn/v4/stock_prices'
```

## 📊 Nguồn dữ liệu

Bot sử dụng **VIETSTOCK API** (miễn phí, không cần authentication):
- Realtime data (delay < 1 phút)
- Hỗ trợ tất cả mã trên HOSE, HNX, UPCOM
- Stable và reliable

## ⚠️ Lưu ý

- Giá được tính theo **nghìn đồng** (VD: 25500 = 25,500 VNĐ)
- Alert tự động xóa sau khi kích hoạt (gửi 1 lần duy nhất)
- Chỉ hỗ trợ alert 1 chiều (giá >= mục tiêu)
- Bot cần chạy 24/7 để hoạt động

## 🐛 Troubleshooting

**Bot không chạy:**
- Kiểm tra BOT_TOKEN đã đúng chưa
- Chạy `python bot.py` và xem log lỗi

**Không nhận được alert:**
- Kiểm tra bot đang chạy: `ps aux | grep bot.py`
- Xem log: `tail -f bot.log` (nếu có)

**Mã cổ phiếu không hợp lệ:**
- Đảm bảo nhập đúng mã (VD: HPG, VNM, FPT)
- API chỉ hỗ trợ mã trên sàn Việt Nam

## 📝 TODO / Tính năng tương lai

- [ ] Alert 2 chiều (giá <= mục tiêu)
- [ ] Alert theo % thay đổi
- [ ] Export danh sách alerts
- [ ] Thống kê lịch sử alerts
- [ ] Multi-user support với database riêng

## 📄 License

MIT License - Free to use

---

**Chúc bạn đầu tư thành công! 🚀📈**
