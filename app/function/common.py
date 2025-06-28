import json
from typing import Any, Dict, Optional


def parse_multiline_config(command: Optional[str]) -> Dict[str, Any]:
    """
    解析多行配置，兼容Go端格式，字段缺失/空值时给默认或忽略。
    支持headers, env, args, arg, result, cookies等。
    """
    if not command:
        return {}

    result: Dict[str, Any] = {}
    lines = command.splitlines()
    for line in lines:
        line = line.strip()
        if not line or not line.startswith("【") or "】" not in line:
            continue
        key, value = line.split("】", 1)
        key = key.strip("【").strip().lower()
        value = value.strip()
        if not value:
            continue
        if key in ("headers", "env"):
            items = value.split("|||")
            d: Dict[str, str] = {}
            for item in items:
                if ":" in item:
                    k, v = item.split(":", 1)
                    d[k.strip()] = v.strip()
            result[key] = d
        elif key in ("args", "arg"):
            # 支持JSON或逗号分隔
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    result["args"] = parsed
                else:
                    result["args"] = [parsed]
            except Exception:
                # 逗号分隔
                result["args"] = [v.strip() for v in value.split(",") if v.strip()]
        elif key == "timeout":
            # 确保timeout是整数
            try:
                result[key] = int(value)
            except ValueError:
                result[key] = 60
        else:
            result[key] = value

    # 默认值处理
    if "mode" not in result or not result["mode"]:
        result["mode"] = "GET"
    if "timeout" not in result or not result["timeout"]:
        result["timeout"] = 60
    return result
