# SuiGuard Demo - AI Security Assistant cho Sui Move

Demo tính năng AI tự động phát hiện và sửa lỗ hổng bảo mật đặc thù của Sui Move.

## 🎯 Tính năng

- ✅ Phát hiện tự động các lỗ hổng đặc thù của Sui Move:
  - **Capability Leak** (Rò rỉ quyền) - Severity: High
  - **Improper Object Wrapping** - Severity: High  
  - **Coin & Balance Logic Error** - Severity: Medium
  - **Object Freezing** - Severity: Medium
  - **Public(package) Confusion** - Severity: Low

- ✅ Tự động sửa lỗi và đề xuất code an toàn
- ✅ Giao diện web trực quan, dễ sử dụng
- ✅ Hỗ trợ nhiều ví dụ code có lỗi để test

## 🚀 Cài đặt và Chạy

### 1. Cài đặt dependencies

```bash
cd suiguard_demo
pip install -r requirements.txt
```

### 2. Chạy Backend API

```bash
cd backend
python main.py
```

Backend sẽ chạy tại: `http://localhost:8000`

### 3. Mở Frontend

Mở file `frontend/index.html` trong trình duyệt, hoặc dùng local server:

```bash
# Python 3
cd frontend
python -m http.server 8080

# Hoặc Node.js
npx http-server -p 8080
```

Truy cập: `http://localhost:8080`

## 📝 Cách sử dụng

1. **Nhập code**: Paste code Sui Move vào ô input, hoặc chọn một trong các ví dụ có sẵn:
   - 🔴 Capability Leak
   - ⚠️ Object Wrapping  
   - 💰 Balance Logic

2. **Phân tích**: Nhấn nút "🔍 Phân tích với AI"

3. **Xem kết quả**: 
   - Danh sách lỗ hổng được phát hiện với mức độ nghiêm trọng
   - Code đã được sửa tự động
   - Giải thích chi tiết về lỗ hổng và cách sửa

## 🔍 Ví dụ Lỗ hổng

### Capability Leak (Rò rỉ Quyền)

```move
// LỖI: Hàm public trả về AdminCap
public fun get_admin_cap(ctx: &mut TxContext): AdminCap {
    AdminCap { id: object::new(ctx), admin_address: tx_context::sender(ctx) }
}
```

**Sửa lỗi:**
```move
// Đổi thành public(friend) để chỉ module trong package mới gọi được
public(friend) fun get_admin_cap(ctx: &mut TxContext): AdminCap {
    AdminCap { id: object::new(ctx), admin_address: tx_context::sender(ctx) }
}
```

### Improper Object Wrapping

```move
// LỖI: Có wrap nhưng không có unwrap
public fun wrap_token(token: Token, ctx: &mut TxContext): WrappedToken {
    WrappedToken { id: object::new(ctx), token }
}
```

**Sửa lỗi:** Thêm hàm `unwrap_token()` để có thể lấy lại Token.

### Coin & Balance Logic Error

```move
// LỖI: Split coin mà không kiểm tra số dư
public fun split_coin_unsafe(coin: Coin<SUI>, amount: u64): Coin<SUI> {
    coin::split(coin, amount)  // Có thể abort nếu amount > coin value
}
```

**Sửa lỗi:**
```move
public fun split_coin_safe(coin: Coin<SUI>, amount: u64): Coin<SUI> {
    assert!(coin::value(&coin) >= amount, E_INSUFFICIENT_BALANCE);
    coin::split(coin, amount)
}
```

## 🏗️ Kiến trúc

- **Backend**: FastAPI (Python) - Xử lý logic phát hiện lỗ hổng
- **Frontend**: HTML/CSS/JavaScript - Giao diện người dùng
- **AI Engine**: Rule-based + Pattern Matching (Demo)
  - Production sẽ dùng Fine-tuned LLM (DeepSeek-Coder-V2)

## 📂 Cấu trúc Project

```
suiguard_demo/
├── backend/
│   └── main.py              # FastAPI backend
├── frontend/
│   └── index.html           # Web interface
├── examples/
│   ├── vulnerable_code.move  # Ví dụ Capability Leak
│   ├── wrapping_error.move   # Ví dụ Object Wrapping
│   └── balance_error.move    # Ví dụ Balance Logic
├── requirements.txt
└── README.md
```

## 🔮 Roadmap

- [ ] Tích hợp LLM thật (DeepSeek-Coder API)
- [ ] Thêm nhiều pattern lỗ hổng
- [ ] Tích hợp Move Prover để verify code
- [ ] VS Code Extension
- [ ] CI/CD Pipeline integration

## 📄 License

MIT License

## 👥 Team

SuiGuard Team - Sui Hackathon 2024

