import logging
import re
from typing import List, Optional

# 设置日志记录器
logger = logging.getLogger(__name__)


class PasswordValidator:
    """密码复杂度验证器"""

    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        min_unique_chars: int = 4,
        max_length: Optional[int] = 64,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.min_unique_chars = min_unique_chars
        self.max_length = max_length

    def validate(self, password: str) -> tuple[bool, List[str]]:
        """验证密码复杂度"""
        errors = []

        # 检查长度
        if len(password) < self.min_length:
            errors.append(f"密码长度不能少于{self.min_length}个字符")

        if self.max_length and len(password) > self.max_length:
            errors.append(f"密码长度不能超过{self.max_length}个字符")

        # 检查大写字母
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("密码必须包含至少一个大写字母")

        # 检查小写字母
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("密码必须包含至少一个小写字母")

        # 检查数字
        if self.require_digit and not re.search(r"\d", password):
            errors.append("密码必须包含至少一个数字")

        # 检查特殊字符
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密码必须包含至少一个特殊字符")

        # 检查唯一字符数
        unique_chars = len(set(password))
        if unique_chars < self.min_unique_chars:
            errors.append(f"密码必须包含至少{self.min_unique_chars}个不同字符")

        is_valid = len(errors) == 0

        return is_valid, errors


# 创建默认验证器实例
default_password_validator = PasswordValidator()


def validate_password(password: str) -> tuple[bool, List[str]]:
    """使用默认验证器验证密码"""
    return default_password_validator.validate(password)
