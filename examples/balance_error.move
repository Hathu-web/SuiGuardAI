/// Ví dụ code Move có lỗi Coin & Balance Logic
/// Thiếu kiểm tra số dư trước khi split hoặc withdraw

module sui_guard_demo::balance_error {
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};
    use sui::sui::SUI;
    
    /// LỖI: Split coin mà không kiểm tra số dư
    /// Có thể gây abort nếu amount > coin value
    public fun split_coin_unsafe(coin: Coin<SUI>, amount: u64): Coin<SUI> {
        // Thiếu kiểm tra: assert!(coin::value(&coin) >= amount, E_INSUFFICIENT_BALANCE);
        coin::split(coin, amount)
    }
    
    /// LỖI: Withdraw từ balance mà không kiểm tra
    public fun withdraw_unsafe(balance: &mut Balance<SUI>, amount: u64): Coin<SUI> {
        // Thiếu kiểm tra: assert!(balance::value(balance) >= amount, E_INSUFFICIENT_BALANCE);
        balance::withdraw(balance, amount)
    }
    
    /// Code đúng: Có kiểm tra số dư
    const E_INSUFFICIENT_BALANCE: u64 = 1;
    
    public fun split_coin_safe(coin: Coin<SUI>, amount: u64): Coin<SUI> {
        assert!(coin::value(&coin) >= amount, E_INSUFFICIENT_BALANCE);
        coin::split(coin, amount)
    }
}

