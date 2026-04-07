"""
pytest 全局配置
"""
import sys, os

# 确保 tools 目录在 Python path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
