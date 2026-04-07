> Bản dịch từ [English version](#context-files)

# Context Files

> Bundle `references/` trong repo team-setup **không** còn phát hành template `goclaw-template-user.md`, `goclaw-template-bootstrap.md`, hay `goclaw-template-team.md`. Skill generate role pack không tạo `USER.md` / `BOOTSTRAP.md` từ `references/`. Runtime GoClaw vẫn có thể dùng các file đó nếu bạn tự thêm ngoài pipeline này.

> Các file markdown sau định nghĩa personality, kiến thức và hành vi của agent (theo mô hình GoClaw; subset có template trong bundle này xem bảng dưới).

**Canonical template path (skill v12+):** `agent-settings/templates/` — `goclaw-template-agents.md`, `goclaw-template-soul.md`, `goclaw-template-identity.md`, `goclaw-template-user-predefined.md`.

**Legacy mirror trong `references/`:** cùng bốn file trên; có thể dùng làm fallback đọc-only khi migrate. Pipeline render phải ghi output vào `agent-settings/roles/<role-slug>/`.

## Tổng quan

Mỗi agent load các context file xác định cách nó suy nghĩ và hành động. Các file này được lưu ở hai cấp độ: **cấp agent** (dùng chung giữa các user trên predefined agent) và **theo từng user** (tuỳ chỉnh cho từng user trên open agent). File được load theo thứ tự và inject vào system prompt trước mỗi request.

## Tổng quan các file

| File | Mục đích | Phạm vi | Open | Predefined | Có thể xoá |
|------|---------|-------|------|-----------|-----------|
| **AGENTS.md** | Hướng dẫn vận hành & phong cách trò chuyện | Dùng chung | Theo user | Cấp agent | Không |
| **SOUL.md** | Personality, giọng điệu, ranh giới, chuyên môn | Theo user | Theo user | Cấp agent | Không |
| **IDENTITY.md** | Tên, loại sinh vật, emoji, vibe | Theo user | Theo user | Cấp agent | Không |
| **USER_PREDEFINED.md** | Quy tắc xử lý user cơ bản | Cấp agent | Không có | Cấp agent | Không |
| **MEMORY.md** | Bộ nhớ dài hạn được chắt lọc | Theo user | Theo user | Theo user | Không |

## Chi tiết từng file

### AGENTS.md

**Mục đích:** Cách bạn vận hành. Phong cách trò chuyện, hệ thống bộ nhớ, quy tắc group chat, định dạng theo nền tảng.

**Ai viết:** Bạn trong quá trình setup, hoặc hệ thống từ template.

**Nội dung ví dụ:**
```markdown
# AGENTS.md - How You Operate

## Conversational Style

Talk like a person, not a bot.
- Don't parrot the question back
- Answer first, explain after
- Match the user's energy

## Memory

Use tools to persist information:
- Recall: Use `memory_search` before answering about prior decisions
- Save: Use `write_file` to MEMORY.md for long-term storage
- No mental notes — write it down NOW

## Group Chats

Respond when:
- Directly mentioned or asked a question
- You can add genuine value

Stay silent when:
- Casual banter between humans
- Someone already answered
- The conversation flows fine without you
```

**Open agent:** Theo user (user có thể tuỳ chỉnh phong cách vận hành)
**Predefined agent:** Cấp agent (khoá, dùng chung cho tất cả user)

### SOUL.md

**Mục đích:** Bạn là ai. Personality, giọng điệu, ranh giới, chuyên môn, vibe.

**Ai viết:** LLM trong quá trình summoning (predefined) hoặc user trong bootstrap (open).

**Nội dung ví dụ thực tế:**
```markdown
# SOUL.md - Who You Are

## Core Truths

Be genuinely helpful, not performative.
Have opinions. Be resourceful before asking.
Earn trust through competence.
Remember you're a guest.

## Boundaries

Private things stay private.
Never send half-baked replies.
You're not the user's voice.

## Vibe

Concise when needed, thorough when it matters.
Not a corporate drone. Not a sycophant. Just good.

## Style

- **Tone:** Casual and warm — like texting a knowledgeable friend
- **Humor:** Use it naturally when it fits
- **Emoji:** Sparingly — to add warmth, not decorate
- **Opinions:** Express perspectives. Neutral is boring.
- **Length:** Default short. Go deep when it matters.

## Expertise

_(Kiến thức chuyên môn đặt ở đây: coding standards, image generation techniques, writing styles, specialized keywords, v.v.)_
```

**Open agent:** Theo user (tạo ra khi chat lần đầu, có thể tuỳ chỉnh)
**Predefined agent:** Cấp agent (tuỳ chọn tạo qua LLM summoning)

### IDENTITY.md

**Mục đích:** Tôi là ai? Tên, loại sinh vật, mục đích, vibe, emoji.

**Ai viết:** LLM trong quá trình summoning (predefined) hoặc user trong bootstrap (open).

**Nội dung ví dụ thực tế:**
```markdown
# IDENTITY.md - Who Am I?

- **Name:** Claude
- **Creature:** AI assistant, language model, curious mind
- **Purpose:** Help research, write, code, think through problems. Navigate information chaos. Be trustworthy.
- **Vibe:** Thoughtful, direct, a bit sarcastic. Warm but not saccharine.
- **Emoji:** 🧠
- **Avatar:** _blank (or workspace-relative path like `avatars/claude.png`)_
```

**Open agent:** Theo user (tạo ra khi chat lần đầu)
**Predefined agent:** Cấp agent (tuỳ chọn tạo qua LLM summoning)

### USER.md và BOOTSTRAP.md (không còn template trong bundle này)

GoClaw runtime vẫn có thể dùng `USER.md` (mô tả người dùng) và `BOOTSTRAP.md` (nghi lễ lần đầu) nếu bạn tự tạo file trong workspace. Repo team-setup **không** cung cấp `goclaw-template-user.md` / `goclaw-template-bootstrap.md` và skill không generate hai file này trong role pack.

### MEMORY.md

**Mục đích:** Bộ nhớ dài hạn được chắt lọc. Quyết định quan trọng, bài học, sự kiện đáng nhớ.

**Ai viết:** Bạn, dùng `write_file()` trong các cuộc trò chuyện.

**Nội dung ví dụ thực tế:**
```markdown
# MEMORY.md - Long-Term Memory

## Key Decisions

- Chose Anthropic Claude as primary LLM (Nov 2025) — best instruction-following, good context window
- Switched to pgvector for embeddings (Jan 2026) — faster than external service

## Learnings

- Users want agent personality to be customizable per-user (not fixed)
- Memory search is most-used tool — index aggressively
- WebSocket connections drop on long operations — need heartbeats

## Important Contacts

- Engineering lead: @alex, alex@company.com
- Product: @jordan
- Legal: @sam (always approves new features)

## Active Projects

- Building open agent architecture (target: March 2026)
- Memory compaction for large MEMORY.md files
```

**Open agent:** Theo user (duy trì qua các session)
**Predefined agent:** Theo user (nếu user điền vào)

> **Lưu ý:** Hệ thống tìm `MEMORY.md` trước, sau đó fallback sang `memory.md` (chữ thường). Cả hai tên file đều hoạt động.

> **Đã lỗi thời:** `MEMORY.json` được dùng trong các phiên bản cũ như metadata bộ nhớ đã được index. Nó đã deprecated và thay thế bằng `MEMORY.md`. Nếu bạn có file `MEMORY.json` cũ, hãy chuyển nội dung sang `MEMORY.md`.

## Virtual Context File

Ngoài các context file có thể chỉnh sửa (xem bảng trên), GoClaw inject thêm một số **virtual context file** lúc runtime. Các file này được tạo động từ trạng thái hệ thống — không được lưu trên đĩa và không thể chỉnh sửa thủ công:

| File | Mục đích | Khi nào được inject |
|------|---------|--------------|
| **DELEGATION.md** | Context delegation task được truyền từ parent agent sang subagent được spawn | Khi agent được spawn với delegated task |
| **TEAM.md** | Hướng dẫn team orchestration — lead nhận hướng dẫn đầy đủ; member nhận phiên bản đơn giản hóa về vai trò + workspace | Khi agent thuộc về một team |
| **AVAILABILITY.md** | Trạng thái và mức độ sẵn sàng của thành viên để phối hợp trong team | Khi team context đang active |

Các file này xuất hiện trong system prompt cùng với context file thông thường nhưng bắt nguồn từ trạng thái runtime, không phải filesystem.

## Thứ tự load file

Các file được load theo thứ tự này và ghép nối vào system prompt:

1. **AGENTS.md** — cách vận hành
2. **SOUL.md** — bạn là ai
3. **IDENTITY.md** — tên, emoji
4. **USER_PREDEFINED.md** — quy tắc user mặc định (predefined)
5. **MEMORY.md** — bộ nhớ dài hạn (tuỳ chọn)

Tuỳ cấu hình runtime, GoClaw có thể load thêm **USER.md** / **BOOTSTRAP.md** nếu tồn tại trên đĩa; bundle team-setup này không sinh chúng từ `references/`.

Subagent và cron session chỉ load: AGENTS.md (context tối thiểu).

> **Inject persona:** SOUL.md và IDENTITY.md được inject **hai lần** trong system prompt — một lần ở đầu (primacy zone) để thiết lập danh tính, và một lần ở cuối (recency zone) như một lời nhắc ngắn để tránh persona drift trong các cuộc trò chuyện dài.

## Ví dụ

### Luồng Open Agent (rút gọn)

User mới chat với open agent: thường seed `AGENTS.md` / `SOUL.md` / `IDENTITY.md` (tuỳ triển khai). Phần `USER.md` / `BOOTSTRAP.md` nếu có do runtime hoặc bạn tự thêm — **không** phát sinh từ template đã gỡ trong repo team-setup này.

### Predefined Agent: FAQ Bot

Tạo FAQ bot với summoning:

1. Tạo predefined agent với mô tả:
   ```bash
   curl -X POST /v1/agents \
     -d '{
       "agent_key": "faq-bot",
       "agent_type": "predefined",
       "other_config": {
         "description": "Friendly FAQ bot that answers product questions. Patient, helpful, multilingual."
       }
     }'
   ```

2. LLM tạo file cấp agent:
   ```
   SOUL.md → "Patient, friendly, helpful tone. Multilingual support."
   IDENTITY.md → "FAQ Assistant, 🤖"
   ```

3. Khi user mới bắt đầu chat: load các file cấp agent (`SOUL.md`, `IDENTITY.md`, `AGENTS.md`, …) theo cấu hình. Tuỳ chỉnh theo user có thể thêm file khác ngoài bundle template của repo này.

4. Agent duy trì personality nhất quán theo context đã load.

## Các vấn đề thường gặp

| Vấn đề | Giải pháp |
|---------|----------|
| Context file không xuất hiện trong system prompt | Kiểm tra tên file có trong allowlist `standardFiles`. Chỉ file được nhận dạng mới được load |
| Cần USER.md / BOOTSTRAP.md | Tự tạo trong workspace hoặc dùng luồng runtime của GoClaw; bundle team-setup không cung cấp template cho hai file này |
| Thay đổi SOUL.md không có hiệu lực | Trong predefined mode, SOUL.md là cấp agent. Kiểm tra đúng scope file và cách deploy |
| System prompt quá dài | Giảm nội dung trong context file. Pipeline truncation cắt từ ít đến quan trọng nhất |

## Tiếp theo

- [Open vs. Predefined](#open-vs-predefined) — hiểu khi nào file là theo user hay cấp agent
- [Summoning & Bootstrap](#summoning-bootstrap) — cách SOUL.md và IDENTITY.md được LLM tạo ra
- [Creating Agents](#creating-agents) — hướng dẫn tạo agent từng bước

<!-- goclaw-source: 57754a5 | cập nhật: 2026-03-23 -->
