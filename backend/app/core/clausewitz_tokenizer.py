"""
流式 Clausewitz 文本格式分词器。

Stellaris 存档使用 Paradox 的 Clausewitz 引擎文本格式：
  key=value
  key="string"
  key={<nested block>}
  key=yes / key=no
  key=@reference_id

设计目标：
- 逐字符读取，O(n) 时间复杂度
- 支持 skip_block() 快进跳过不需要的段落
- 支持 find_and_parse() 定位并解析指定 key
- 内存占用仅为当前解析段落的大小（最大 <5MB）
"""

from __future__ import annotations

import re
from typing import Any


class ClausewitzTokenizer:
    """逐字符 Clausewitz 文本分词器/解析器。"""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    # ── 基础操作 ──────────────────────────────────

    def at_end(self) -> bool:
        return self.pos >= self.length

    def peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.text[idx] if idx < self.length else ""

    def advance(self, n: int = 1):
        self.pos += n

    # ── 空白与注释 ────────────────────────────────

    def skip_whitespace(self):
        while not self.at_end() and self.peek() in " \t\r\n":
            self.advance()

    def skip_comment(self):
        while not self.at_end() and self.peek() != "\n":
            self.advance()

    def skip_blank(self):
        """跳过空白和注释行。"""
        while not self.at_end():
            ch = self.peek()
            if ch in " \t\r\n":
                self.advance()
            elif ch == "#":
                self.skip_comment()
            else:
                break

    # ── 读取器 ────────────────────────────────────

    def read_quoted_string(self) -> str:
        """读取双引号字符串（处理转义引号）。返回不含引号的字符串。"""
        self.advance()  # 跳过开引号
        start = self.pos
        while not self.at_end():
            ch = self.peek()
            if ch == '"':
                # 检查是否为转义引号
                if self.pos > start and self.text[self.pos - 1] == "\\":
                    self.advance()
                    continue
                result = self.text[start : self.pos]
                self.advance()  # 跳过闭引号
                return result
            self.advance()
        result = self.text[start : self.pos]
        return result

    def read_bare_word(self) -> str:
        """读取一个未加引号的标识符/数字/布尔值。"""
        start = self.pos
        while not self.at_end() and self.peek() not in " \t\r\n={}":
            self.advance()
        return self.text[start : self.pos]

    # ── 块操作 ────────────────────────────────────

    def skip_block(self):
        """从当前位置（应为 '{'）快进到匹配的 '}'。
        正确处理嵌套块、字符串中的花括号、注释。
        调用后，pos 指向匹配 '}' 的下一个字符。"""
        if self.peek() != "{":
            return
        depth = 1
        self.advance()
        while not self.at_end() and depth > 0:
            ch = self.peek()
            if ch == '"':
                self.read_quoted_string()
            elif ch == "{":
                depth += 1
                self.advance()
            elif ch == "}":
                depth -= 1
                self.advance()
            elif ch == "#":
                self.skip_comment()
            else:
                self.advance()

    def parse_value(self) -> Any:
        """解析当前位置的值。

        返回: Python 原生类型 — str, int, float, bool, dict, list
        """
        ch = self.peek()
        if ch == '"':
            return self.read_quoted_string()
        elif ch == "{":
            return self.parse_block()
        elif ch == "@":
            self.advance()
            word = self.read_bare_word()
            try:
                return int(word)
            except (ValueError, TypeError):
                return f"@{word}"
        elif ch in "0123456789+-.":
            word = self.read_bare_word()
            return _coerce_number(word)
        else:
            word = self.read_bare_word()
            if word == "yes":
                return True
            if word == "no":
                return False
            return _coerce_number(word)

    def parse_block(self) -> dict:
        """解析 {...} 块为 Python dict。调用后 pos 指向 '}' 的下一个字符。"""
        if self.peek() != "{":
            return {}
        self.advance()  # 跳过 '{'

        result: dict = {}
        while not self.at_end():
            self.skip_blank()
            if self.at_end():
                break
            if self.peek() == "}":
                self.advance()
                return result

            key = self.read_bare_word()
            self.skip_blank()

            # 处理 value
            if self.peek() == "=":
                self.advance()
                self.skip_blank()
                result[key] = self.parse_value()
            elif self.peek() == "{":
                result[key] = self.parse_value()
            elif self.peek() == '"':
                result[key] = self.parse_value()
            elif self.peek() in "0123456789+-.":
                result[key] = self.parse_value()
            else:
                # key without obvious value — treat next token as value
                val = self.read_bare_word()
                result[key] = _coerce_number(val)

        return result

    # ── 查找操作 ──────────────────────────────────

    def find_and_parse(self, target_key: str) -> tuple[Any, bool]:
        """在当前嵌套层级中查找 target_key 并解析其值。

        返回 (value, found)。若未找到，pos 停留在当前块末尾。
        """
        while not self.at_end():
            self.skip_blank()
            if self.at_end():
                break
            if self.peek() == "}":
                break  # 当前作用域结束

            key = self.read_bare_word()
            self.skip_blank()

            # 跳过 '='
            if self.peek() == "=":
                self.advance()
                self.skip_blank()

            if key == target_key:
                return self.parse_value(), True
            else:
                # 跳过该值
                ch = self.peek()
                if ch == '"':
                    self.read_quoted_string()
                elif ch == "{":
                    self.skip_block()
                elif ch == "@":
                    self.advance()
                    self.read_bare_word()
                else:
                    self.read_bare_word()

        return None, False

    def find_all_keys(self) -> list[str]:
        """返回当前嵌套层级所有 key 名称（用于探索存档结构）。"""
        keys: list[str] = []
        saved_pos = self.pos
        while not self.at_end():
            self.skip_blank()
            if self.at_end():
                break
            if self.peek() == "}":
                break
            key = self.read_bare_word()
            keys.append(key)
            self.skip_blank()
            if self.peek() == "=":
                self.advance()
                self.skip_blank()
            ch = self.peek()
            if ch == '"':
                self.read_quoted_string()
            elif ch == "{":
                self.skip_block()
            elif ch == "@":
                self.advance()
                self.read_bare_word()
            else:
                self.read_bare_word()
        self.pos = saved_pos
        return keys


def _coerce_number(word: str) -> Any:
    """尝试将字符串转为数字，失败则返回原字符串。"""
    if not word:
        return word
    try:
        return int(word)
    except (ValueError, TypeError):
        pass
    try:
        return float(word)
    except (ValueError, TypeError):
        pass
    return word
