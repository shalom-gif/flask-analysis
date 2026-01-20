#!/usr/bin/env python
# coding: utf-8
"""
LibCST分析器 - 代码修改和模式分析
"""

import libcst as cst
import os
from typing import Dict, List
from collections import defaultdict 

class FlaskLibCSTAnalyzer:
    def __init__(self):
        self.function_calls = defaultdict(int)
        self.decorators = defaultdict(int)
        self.class_hierarchy = {}
    
    def analyze_file(self, file_path):
        """使用LibCST分析文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = cst.parse_module(code)
            
            # 访问器收集信息
            visitor = CodeVisitor()
            tree.visit(visitor)
            
            # 合并统计
            for func, count in visitor.function_calls.items():
                self.function_calls[func] += count
            
            for dec, count in visitor.decorators.items():
                self.decorators[dec] += count
            
            # 转换器示例：将所有整数加1
            transformer = IntTransformer()
            modified_tree = tree.visit(transformer)
            
            return {
                "original_lines": len(code.splitlines()),
                "modified_lines": len(modified_tree.code.splitlines()),
                "function_calls": dict(visitor.function_calls),
                "decorators": dict(visitor.decorators)
            }
            
        except Exception as e:
            print(f"LibCST分析失败 {file_path}: {e}")
            return None
    
    def find_flask_patterns(self, file_path):
        """查找Flask特定模式"""
        patterns = {
            "route_decorators": [],
            "app_creation": False,
            "blueprint_usage": False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = cst.parse_module(code)
            
            # 查找Flask路由装饰器
            class RouteFinder(cst.CSTVisitor):
                def __init__(self):
                    self.routes = []
                
                def visit_Decorator(self, node):
                    decorator_str = cst.Module([]).code_for_node(node)
                    if "@app.route" in decorator_str or "@blueprint.route" in decorator_str:
                        self.routes.append(decorator_str)
            
            finder = RouteFinder()
            tree.visit(finder)
            patterns["route_decorators"] = finder.routes
            
            # 检查是否有Flask应用创建
            if "Flask(" in code or "flask.Flask(" in code:
                patterns["app_creation"] = True
            
            # 检查是否使用蓝图
            if "Blueprint(" in code or "blueprint" in code.lower():
                patterns["blueprint_usage"] = True
            
            return patterns
            
        except Exception as e:
            print(f"模式查找失败 {file_path}: {e}")
            return patterns

class CodeVisitor(cst.CSTVisitor):
    """收集代码信息的访问器"""
    def __init__(self):
        self.function_calls = defaultdict(int)
        self.decorators = defaultdict(int)
    
    def visit_Call(self, node):
        if isinstance(node.func, cst.Name):
            self.function_calls[node.func.value] += 1
    
    def visit_Decorator(self, node):
        decorator_str = cst.Module([]).code_for_node(node.decorator)
        self.decorators[decorator_str] += 1

class IntTransformer(cst.CSTTransformer):
    """将所有整数加1的转换器（示例）"""
    def leave_Integer(self, original_node, updated_node):
        try:
            value = int(updated_node.value)
            return updated_node.with_changes(value=str(value + 1))
        except:
            return updated_node

def analyze_with_libcst(directory, output_file):
    """使用LibCST分析整个目录"""
    print(f"使用LibCST分析目录: {directory}")
    
    analyzer = FlaskLibCSTAnalyzer()
    patterns_summary = {
        "total_files": 0,
        "files_with_routes": 0,
        "files_with_app": 0,
        "files_with_blueprint": 0,
        "all_routes": []
    }
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                patterns = analyzer.find_flask_patterns(file_path)
                
                patterns_summary["total_files"] += 1
                if patterns["route_decorators"]:
                    patterns_summary["files_with_routes"] += 1
                    patterns_summary["all_routes"].extend(patterns["route_decorators"])
                if patterns["app_creation"]:
                    patterns_summary["files_with_app"] += 1
                if patterns["blueprint_usage"]:
                    patterns_summary["files_with_blueprint"] += 1
    
    # 保存结果
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(patterns_summary, f, indent=2, ensure_ascii=False)
    
    print(f"LibCST分析完成！结果保存在: {output_file}")
    return patterns_summary