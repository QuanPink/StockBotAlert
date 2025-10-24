# 💡 VÍ DỤ SỬ DỤNG BOT

## 📱 Kịch bản thực tế

### Tình huống 1: Theo dõi giá HPG
```
Bạn: /alert HPG 25.5

Bot: ✅ Đã đặt cảnh báo!
     📊 Mã: HPG
     🎯 Giá mục tiêu: 25.500 VNĐ
     💰 Giá hiện tại: 24.800 VNĐ
     
     Bot sẽ thông báo khi HPG đạt ≥ 25.500

[10 phút sau, khi HPG đạt 25.500]

Bot: 🎯 CẢNH BÁO GIÁ!
     📊 HPG đã đạt mục tiêu!
     
     🎯 Giá mục tiêu: 25.500 VNĐ
     💰 Giá hiện tại: 25.500 VNĐ
     
     Cảnh báo đã được tự động xóa
```

### Tình huống 2: Theo dõi nhiều mã cùng lúc
```
Bạn: /alert HPG 25.500
Bot: ✅ Đã đặt cảnh báo!

Bạn: /alert VNM 80.000
Bot: ✅ Đã đặt cảnh báo!

Bạn: /alert FPT 120.000
Bot: ✅ Đã đặt cảnh báo!

Bạn: /list
Bot: 📋 Danh sách cảnh báo:
     
     • HPG: 25.500 (hiện tại: 24.800)
     • VNM: 80.000 (hiện tại: 78.500)
     • FPT: 120.000 (hiện tại: 119.200)
     
     Tổng: 3 cảnh báo
```

### Tình huống 3: Kiểm tra giá trước khi đặt alert
```
Bạn: /price HPG
Bot: 🟢 HPG
     
     💰 Giá: 24.800 VNĐ
     📈 Thay đổi: +200 (+0.82%)
     📊 Cao: 25.100 | Thấp: 24.500
     📦 KL: 12,450,000

Bạn: /alert HPG 25.500
Bot: ✅ Đã đặt cảnh báo!
```

### Tình huống 4: Xóa alert không cần thiết
```
Bạn: /list
Bot: 📋 Danh sách cảnh báo:
     
     • HPG: 25.500 (hiện tại: 24.800)
     • VNM: 80.000 (hiện tại: 78.500)
     • FPT: 120.000 (hiện tại: 119.200)

Bạn: /remove VNM
Bot: ✅ Đã xóa cảnh báo cho mã VNM

Bạn: /list
Bot: 📋 Danh sách cảnh báo:
     
     • HPG: 25.500 (hiện tại: 24.800)
     • FPT: 120.000 (hiện tại: 119.200)
     
     Tổng: 2 cảnh báo
```

### Tình huống 5: Xử lý lỗi
```
Bạn: /alert INVALID 100
Bot: ⏳ Đang kiểm tra mã INVALID...
Bot: ❌ Không tìm thấy mã INVALID!
     Vui lòng kiểm tra lại mã cổ phiếu.

Bạn: /alert HPG abc
Bot: ❌ Giá không hợp lệ! Vui lòng nhập số.

Bạn: /alert HPG -10
Bot: ❌ Giá phải lớn hơn 0!
```

---

## 🎯 Tips sử dụng

1. **Đặt alert trước giờ giao dịch**
   - Bot check mỗi 10 giây nên không bỏ lỡ cơ hội
   
2. **Dùng /price để kiểm tra giá hiện tại trước**
   - Biết được giá hiện tại để đặt target hợp lý

3. **Dùng /list thường xuyên**
   - Xem có bao nhiêu alerts đang active
   - Theo dõi khoảng cách giá hiện tại vs target

4. **Xóa alerts không cần thiết**
   - Dùng /remove để cleanup
   - Giữ danh sách alerts gọn gàng


---

## ⚡ Use Cases phổ biến

### Day Trading
```
/alert HPG 25.500    # Take profit point
/alert VNM 78.000    # Entry point
/alert FPT 115.000   # Stop loss
```

### Swing Trading
```
/alert VIC 40.000    # Target giá tuần này
/alert VCB 95.000    # Đợi breakout
```

### Long-term Accumulation
```
/alert HPG 22.000    # Giá tích lũy tốt
/alert VNM 75.000   # Điểm vào thêm
```

---

Chúc bạn trading thành công! 🚀📈
