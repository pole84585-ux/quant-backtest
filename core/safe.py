def safe_run(func, default=None, *args, **kwargs):
    """
    所有函数统一安全执行
    出错不崩溃，只返回默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[SAFE ERROR] {func.__name__}: {e}")
        return default
