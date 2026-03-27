# USER_PREDEFINED.md - Ngữ Cảnh Người Dùng Mặc Định

_Ngữ cảnh do chủ agent cấu hình về những người dùng mà agent này phục vụ. Áp dụng cho TẤT CẢ người dùng._

- **Đối tượng phục vụ:**
  _(Agent này được tạo ra để phục vụ ai? Ví dụ: người dùng phổ thông, khách hàng nội bộ, đội kỹ thuật, founder, nhân viên vận hành...)_

- **Ngôn ngữ mặc định:**
  _(Ngôn ngữ mặc định khi user chưa thể hiện preference rõ ràng. Ví dụ: Tiếng Việt. Chỉ chuyển sang tiếng Anh khi user dùng tiếng Anh.)_

- **Quy tắc giao tiếp:**
  _(Các nguyên tắc giao tiếp áp dụng cho tất cả user. Ví dụ: ưu tiên ngắn gọn, rõ ràng, không dùng giọng quá formal, không viết dài khi không cần.)_

- **Ngữ cảnh chung:**
  _(Những điều đúng với mọi user của agent này. Ví dụ: tất cả đều dùng cùng một hệ thống nội bộ, cùng một sản phẩm, hoặc cùng một môi trường làm việc.)_

---

Đây là một phần cấu hình cốt lõi của agent.

Mỗi user có thể có `USER.md` riêng để bổ sung:
- tên
- timezone
- preference cá nhân
- ngữ cảnh riêng

Nhưng `USER.md` KHÔNG được ghi đè:
- quy tắc
- ranh giới
- baseline xử lý user
được đặt trong file này.
