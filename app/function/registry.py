import importlib.util
import os
import sys
from typing import Any, Callable, Dict, Optional, cast

# 全局函数注册表
FUNC_REGISTRY: Dict[str, Callable[..., Any]] = {}


def load_function_from_file(file_path: str) -> Optional[Callable[..., Any]]:
    """从文件加载函数"""
    try:
        spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
        if spec is None:
            return None
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            return None
        spec.loader.exec_module(module)

        # 查找模块中的函数
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and not attr_name.startswith("_"):
                return cast(Callable[..., Any], attr)
        return None
    except Exception:
        return None


def hot_reload(func_dir: str) -> None:
    """热重载函数目录，注册所有函数名"""
    if not os.path.exists(func_dir):
        return

    for filename in os.listdir(func_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            file_path = os.path.join(func_dir, filename)
            spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and not attr_name.startswith("_"):
                    FUNC_REGISTRY[attr_name] = attr


# 注册单个函数
def register_func(name: str, func: Callable[..., Any]) -> None:
    FUNC_REGISTRY[name] = func


# 获取注册的函数
def get_function(name: str) -> Optional[Callable[..., Any]]:
    """获取注册的函数"""
    return FUNC_REGISTRY.get(name)


# 获取所有注册的函数名称
def get_all_functions() -> list[str]:
    """获取所有注册的函数名称"""
    return list(FUNC_REGISTRY.keys())


# 动态加载指定目录下所有.py文件的函数
def load_functions_from_dir(directory: str) -> None:
    if not os.path.exists(directory):
        return
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]
            file_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                if spec.loader is not None:
                    spec.loader.exec_module(module)
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if callable(obj) and not attr.startswith("_"):
                            register_func(attr, obj)
            except Exception as e:
                print(f"加载函数{filename}失败: {e}")
