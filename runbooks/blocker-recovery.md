# Runbook: Recovery from Common Blockers

## 1. Dependency Blocker

**Symptom**: Task chờ upstream task hoàn tất
**Action**:

- Kiểm tra trạng thái upstream
- Nếu upstream bị lỗi → chuyển sang escalation
- Nếu upstream chậm → điều chỉnh ETA
- Ghi nhận dependency vào task tracker

## 2. Access Blocker

**Symptom**: Missing permissions/resources
**Action**:

- Log thiếu permissions cụ thể
- Escalate đến owner cấp quyền
- Tạm chuyển task sang queue chờ
- Gửi notification đến người có thể xử lý

## 3. Policy Blocker

**Symptom**: Vi phạm governance rules
**Action**:

- Xác định policy bị vi phạm
- Yêu cầu exception approval nếu cần
- Chuyển đến người có thẩm quyền phê duyệt
- Ghi nhận lý do exception nếu được chấp thuận

## 4. Capacity Blocker

**Symptom**: Resource/concurrency limits
**Action**:

- Kiểm tra resource availability
- Chờ đến khi có slot trống
- Điều chỉnh priority nếu cần thiết
- Gửi notification khi resource khả dụng

## 5. Quality Gate Blocker

**Symptom**: Test/security/compliance fail
**Action**:

- Ghi rõ lỗi cụ thể
- Chuyển cho chuyên gia domain
- Tạo exception nếu cần bypass tạm thời
- Theo dõi để đảm bảo không tái diễn