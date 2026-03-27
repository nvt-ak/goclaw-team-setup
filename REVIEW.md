# REVIEW.md — GoClaw Team Setup

## 1) Lỗi cốt lõi gây build mãi không xong

1. **Gate semantic chưa đủ chặt**
   - Verify cũ thiên về cấu trúc/đủ file, chưa chặn mạnh lỗi semantic cross-domain.
   - Kết quả: pack content có thể lọt residue từ team IT.

2. **Điều kiện DONE chưa khóa cứng cặp evidence**
   - Có lúc pass trạng thái nhưng thiếu bằng chứng đóng run đầy đủ.
   - Dẫn tới mâu thuẫn “pass kỹ thuật” vs “chưa đủ artifact để close”.

3. **Watchdog/evidence timeout chưa được ràng buộc rõ thành trạng thái fail**
   - Thiếu checkpoint artifact theo chu kỳ thì cần block rõ, tránh treo.

4. **Bundle trước đó thiếu SKILL.md trong zip local**
   - Khó test độc lập vì chỉ có references.

## 2) V8 đã vá gì

- Thêm **Deterministic Completion Contract**:
  - DONE chỉ khi có đủ `VERIFY_TEAM_PACK_REPORT.md` + `DIFF_REPORT.md`.
- Thêm **team-type semantic gate**:
  - Chặn semantic drift theo `team_type`.
- Thêm **watchdog policy 5 phút**:
  - Quá hạn không checkpoint evidence => `BLOCKED_NO_EVIDENCE`.
- Bổ sung **HEARTBEAT.md** vào per-role required set.
- Bundle v8 có **SKILL.md + references + scripts** để test được end-to-end.

## 3) Kỳ vọng sau patch

- Giảm false PASS do chỉ pass cấu trúc.
- Trạng thái close minh bạch hơn (artifact-driven).
- Dễ debug hơn nhờ fail state rõ (`INCOMPLETE_SETUP` / `FAILED_SEMANTIC_DRIFT` / `BLOCKED_NO_EVIDENCE`).
