/// Ví dụ code Move có lỗi Improper Object Wrapping
/// Object được wrap nhưng không có cơ chế unwrap

module sui_guard_demo::wrapping_error {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    
    /// Token struct có store ability
    struct Token has key, store {
        id: UID,
        amount: u64,
        symbol: vector<u8>,
    }
    
    /// Wrapper struct
    struct WrappedToken has key, store {
        id: UID,
        token: Token,  // Token được wrap bên trong
    }
    
    /// LỖI: Có hàm wrap nhưng không có hàm unwrap
    /// Token bên trong sẽ bị mất vĩnh viễn
    public fun wrap_token(token: Token, ctx: &mut TxContext): WrappedToken {
        WrappedToken {
            id: object::new(ctx),
            token,
        }
    }
    
    /// Thiếu hàm unwrap_token() để lấy lại Token
    /// Điều này khiến Token bị mất vĩnh viễn sau khi wrap
}

