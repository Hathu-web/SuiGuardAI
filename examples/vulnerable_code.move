/// Ví dụ code Move có lỗi Capability Leak - LỖI NGHIÊM TRỌNG
/// Đây là lỗi đặc thù nguy hiểm nhất của Sui Move

module sui_guard_demo::vulnerable_admin {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    
    /// Admin Capability - quyền quản trị quan trọng
    struct AdminCap has key, store {
        id: UID,
        admin_address: address,
    }
    
    /// Treasury - kho bạc chứa coin
    struct Treasury has key {
        id: UID,
        balance: u64,
    }
    
    /// LỖI: Hàm public có thể trả về AdminCap
    /// Attacker có thể gọi hàm này và chiếm quyền admin
    public fun get_admin_cap(ctx: &mut TxContext): AdminCap {
        AdminCap {
            id: object::new(ctx),
            admin_address: tx_context::sender(ctx),
        }
    }
    
    /// LỖI: Transfer AdminCap ra ngoài trong hàm public
    public fun transfer_admin_cap(cap: AdminCap, recipient: address) {
        // Attacker có thể lấy AdminCap và chiếm quyền kiểm soát
        transfer::transfer(cap, recipient);
    }
    
    /// Hàm an toàn: chỉ friend modules mới gọi được
    public(friend) fun safe_get_admin_cap(ctx: &mut TxContext): AdminCap {
        AdminCap {
            id: object::new(ctx),
            admin_address: tx_context::sender(ctx),
        }
    }
}

