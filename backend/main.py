"""
SuiGuard Demo - Backend API
Tính năng AI tự động phát hiện và sửa lỗi đặc thù của Sui Move
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import re

app = FastAPI(title="SuiGuard AI Security Assistant", version="1.0.0")

# CORS middleware để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeAnalysisRequest(BaseModel):
    code: str
    vulnerability_type: Optional[str] = None


class Vulnerability(BaseModel):
    type: str
    severity: str  # "High", "Medium", "Low"
    line: int
    description: str
    fixed_code: str
    explanation: str


class CodeAnalysisResponse(BaseModel):
    has_vulnerabilities: bool
    vulnerabilities: List[Vulnerability]
    fixed_code: str
    summary: str


# Knowledge Base: Các pattern lỗi đặc thù của Sui Move
VULNERABILITY_PATTERNS = {
    "capability_leak": {
        "pattern": r"public\s+fun\s+\w+.*?:\s*(\w+Cap|AdminCap|TreasuryCap)",
        "description": "Capability Leak: Hàm public có thể trả về Capability, cho phép attacker chiếm quyền admin",
        "severity": "High"
    },
    "improper_wrapping": {
        "pattern": r"struct\s+(\w+)\s+has\s+store.*?wrap\(.*?\1",
        "description": "Improper Object Wrapping: Object được wrap nhưng không có cơ chế unwrap hợp lệ",
        "severity": "High"
    },
    "object_freezing": {
        "pattern": r"transfer::share_object\(.*?\)",
        "description": "Object Freezing: Shared object có thể bị đóng băng vĩnh viễn nếu không kiểm soát",
        "severity": "Medium"
    },
    "balance_logic": {
        "pattern": r"coin::split\(.*?\)|balance::withdraw\(.*?\)",
        "description": "Coin & Balance Logic: Thiếu kiểm tra số dư trước khi split hoặc withdraw",
        "severity": "Medium"
    },
    "public_package_confusion": {
        "pattern": r"public\(package\)\s+fun",
        "description": "Public(package) Confusion: Có thể bị gọi bởi module khác trong cùng package",
        "severity": "Low"
    }
}


def detect_capability_leak(code: str) -> Optional[Vulnerability]:
    """Phát hiện lỗi Capability Leak - lỗi đặc thù nguy hiểm nhất của Sui"""
    lines = code.split('\n')
    
    # Tìm các hàm public trả về Capability
    for i, line in enumerate(lines, 1):
        # Pattern: public fun ... : AdminCap hoặc tương tự
        if re.search(r'public\s+fun\s+\w+.*?:\s*(\w+Cap|AdminCap|TreasuryCap)', line):
            # Tìm hàm tương ứng
            func_match = re.search(r'public\s+fun\s+(\w+)', line)
            if func_match:
                func_name = func_match.group(1)
                
                # Tạo code sửa lỗi
                fixed_line = line.replace('public fun', 'public(friend) fun')
                fixed_code = code.replace(line, fixed_line)
                
                return Vulnerability(
                    type="Capability Leak",
                    severity="High",
                    line=i,
                    description="Hàm public có thể trả về Capability quan trọng, cho phép attacker chiếm quyền admin",
                    fixed_code=fixed_code,
                    explanation=f"Hàm {func_name} trả về Capability nhưng được khai báo public. Nên đổi thành public(friend) để chỉ module trong cùng package mới gọi được."
                )
    
    # Tìm pattern: transfer Capability ra ngoài
    for i, line in enumerate(lines, 1):
        if 'transfer::' in line and ('Cap' in line or 'Capability' in line):
            if 'public' in lines[max(0, i-5):i]:
                return Vulnerability(
                    type="Capability Leak",
                    severity="High",
                    line=i,
                    description="Capability được transfer ra ngoài trong hàm public, có thể bị attacker lấy",
                    fixed_code=code,  # Cần sửa thủ công
                    explanation="Capability không nên được transfer trong hàm public. Nên sử dụng access control hoặc chỉ cho phép friend modules."
                )
    
    return None


def detect_improper_wrapping(code: str) -> Optional[Vulnerability]:
    """Phát hiện lỗi Improper Object Wrapping"""
    lines = code.split('\n')
    
    # Tìm struct có store và có hàm wrap
    has_wrap = False
    has_unwrap = False
    wrap_line = 0
    
    for i, line in enumerate(lines, 1):
        if 'wrap(' in line or '::wrap' in line:
            has_wrap = True
            wrap_line = i
        if 'unwrap(' in line or '::unwrap' in line:
            has_unwrap = True
    
    if has_wrap and not has_unwrap:
        # Tìm struct được wrap
        struct_match = re.search(r'struct\s+(\w+)\s+has\s+store', code)
        if struct_match:
            struct_name = struct_match.group(1)
            
            # Tạo hàm unwrap
            unwrap_function = f"""
    /// Unwrap function to safely extract the wrapped object
    public fun unwrap_{struct_name.lower()}(wrapped: {struct_name}): {struct_name} {{
        let {struct_name.lower()} = unwrap_{struct_name.lower()}_internal(wrapped);
        {struct_name.lower()}
    }}
    
    fun unwrap_{struct_name.lower()}_internal(wrapped: {struct_name}): {struct_name} {{
        let {struct_name} {{ id, .. }} = wrapped;
        {struct_name} {{ id }}
    }}"""
            
            # Chèn unwrap function vào cuối module
            fixed_code = code.rstrip() + unwrap_function
            
            return Vulnerability(
                type="Improper Object Wrapping",
                severity="High",
                line=wrap_line,
                description=f"Object {struct_name} được wrap nhưng không có cơ chế unwrap, khiến tài sản bên trong bị mất vĩnh viễn",
                fixed_code=fixed_code,
                explanation=f"Cần thêm hàm unwrap để có thể lấy lại object {struct_name} sau khi wrap. Đã tự động thêm hàm unwrap_{struct_name.lower()}."
            )
    
    return None


def detect_balance_logic_error(code: str) -> Optional[Vulnerability]:
    """Phát hiện lỗi Coin & Balance Logic"""
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Tìm coin::split hoặc balance::withdraw không có kiểm tra
        if 'coin::split' in line or 'balance::withdraw' in line:
            # Kiểm tra xem có kiểm tra số dư trước đó không
            context = '\n'.join(lines[max(0, i-10):i])
            if 'balance::value<' not in context and 'coin::value<' not in context:
                # Tạo code sửa lỗi
                if 'coin::split' in line:
                    # Thêm kiểm tra trước khi split
                    indent = len(line) - len(line.lstrip())
                    check_code = ' ' * indent + f"assert!(coin::value(&coin) >= amount, E_INSUFFICIENT_BALANCE);\n"
                    fixed_code = code[:code.find(line)] + check_code + code[code.find(line):]
                else:
                    fixed_code = code
                
                return Vulnerability(
                    type="Coin & Balance Logic Error",
                    severity="Medium",
                    line=i,
                    description="Thiếu kiểm tra số dư trước khi split hoặc withdraw, có thể gây abort không mong muốn",
                    fixed_code=fixed_code,
                    explanation="Cần thêm assert kiểm tra số dư đủ trước khi thực hiện split hoặc withdraw để tránh abort."
                )
    
    return None


def ai_analyze_code(code: str) -> CodeAnalysisResponse:
    """
    AI Engine: Phân tích code và phát hiện lỗi đặc thù của Sui Move
    Trong production sẽ dùng LLM thật, đây là demo với rule-based + pattern matching
    """
    vulnerabilities = []
    
    # Phát hiện các loại lỗi
    vuln = detect_capability_leak(code)
    if vuln:
        vulnerabilities.append(vuln)
    
    vuln = detect_improper_wrapping(code)
    if vuln:
        vulnerabilities.append(vuln)
    
    vuln = detect_balance_logic_error(code)
    if vuln:
        vulnerabilities.append(vuln)
    
    # Tạo code đã sửa (lấy từ vulnerability đầu tiên nếu có)
    fixed_code = code
    if vulnerabilities:
        # Áp dụng tất cả các sửa lỗi
        for vuln in vulnerabilities:
            if vuln.fixed_code and vuln.fixed_code != code:
                fixed_code = vuln.fixed_code
                break
    
    # Tạo summary
    if vulnerabilities:
        summary = f"Phát hiện {len(vulnerabilities)} lỗ hổng bảo mật:\n"
        for vuln in vulnerabilities:
            summary += f"- {vuln.type} (Severity: {vuln.severity}) tại dòng {vuln.line}\n"
    else:
        summary = "Không phát hiện lỗ hổng bảo mật rõ ràng. Code có vẻ an toàn."
    
    return CodeAnalysisResponse(
        has_vulnerabilities=len(vulnerabilities) > 0,
        vulnerabilities=vulnerabilities,
        fixed_code=fixed_code,
        summary=summary
    )


@app.post("/api/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """
    API endpoint để phân tích code Sui Move và phát hiện lỗ hổng
    """
    try:
        if not request.code.strip():
            raise HTTPException(status_code=400, detail="Code không được để trống")
        
        result = ai_analyze_code(request.code)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích code: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "SuiGuard AI Security Assistant"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

