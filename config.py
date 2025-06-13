#!/usr/bin/env python3
"""
配置文件，存储API密钥和其他配置信息
"""

# API密钥
GEMINI_API_KEY = "AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw"
CLAUDE_API_KEY = "YOUR_CLAUDE_API_KEY_HERE"

# OCR配置
OCR_CONFIG = {
    "lang": "ch",  # 支持中英文
    "det_model_dir": None,  # 使用默认模型
    "rec_model_dir": None,  # 使用默认模型
}

# Gemini配置
GEMINI_CONFIG = {
    "model": "gemini-1.5-pro",
    "temperature": 0.2,
    "max_output_tokens": 2048,
}

# Claude配置
CLAUDE_CONFIG = {
    "model": "claude-3-opus-20240229",
    "temperature": 0.2,
    "max_tokens": 2048,
}

# 文件处理配置
FILE_CONFIG = {
    "supported_formats": ["pdf", "png", "jpg", "jpeg"],
    "output_dir": "output",
}
