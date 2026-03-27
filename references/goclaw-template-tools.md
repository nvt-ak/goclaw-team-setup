# TOOLS.md - Ghi Chú Môi Trường

Skills định nghĩa cách tool hoạt động nói chung.  
File này ghi lại những gì riêng biệt trong môi trường của bạn.

Đây là cheat sheet để bạn làm việc nhanh và chính xác hơn.

---

## Những gì nên ghi ở đây

Các thông tin cụ thể như:

- tên thiết bị và vị trí
- SSH host và alias
- giọng TTS ưa thích
- tên phòng / loa / thiết bị
- biệt danh user hay dùng
- mapping giữa cách user nói và hệ thống thật

---

## Ví dụ

### Thiết bị

- "laptop của tôi" → MacBook Pro, hostname: user-mbp
- "điện thoại" → iPhone 15

### SSH

- home-server → 192.168.1.100, user: admin
- vps → 45.xx.xx.xx, user: ubuntu

### TTS

- giọng mặc định: "Nova"
- loa mặc định: "Phòng khách"

### Mapping

- "báo cáo hôm nay" → workflow tổng hợp task trong ngày
- "check việc" → kiểm tra task pending

---

## Nguyên tắc

- Ghi cụ thể, không mơ hồ
- Luôn cập nhật khi thay đổi
- Xóa thông tin không còn dùng

---

## Không nên ghi

- mật khẩu
- API key
- private key
- thông tin nhạy cảm

---

## Lý do tách riêng

Skills có thể chia sẻ.  
Môi trường của bạn thì không.

Tách riêng giúp:
- không lộ thông tin
- không mất config khi update skill
- agent hiểu đúng context thực tế

---

## Ghi nhớ

Subagent và cron cũng đọc file này.  
Mọi ghi chú ở đây đều dùng được cho automation.

---

Đây là cheat sheet của bạn.  
Càng rõ → agent càng ít sai.
