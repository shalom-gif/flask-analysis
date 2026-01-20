#!/usr/bin/env python
# coding: utf-8
"""
AST静态分析器 - 分析Flask代码结构
"""

import ast
import os
import json
from collections import defaultdict

class FlaskASTAnalyzer:
    def __init__(self):
        self.stats = {
            "files_analyzed": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_imports": 0,
            "function_details": [],
            "class_details": [],
            "import_details": []
        }
    
    def analyze_file(self, file_path):
        """分析单个Python文件的AST结构"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            file_stats = {
                "file": os.path.relpath(file_path),
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "lines": len(content.splitlines())
            }
            
            for node in ast.walk(tree):
                # 统计函数
                if isinstance(node, ast.FunctionDef):
                    file_stats["functions"] += 1
                    func_info = self._analyze_function(node, file_path)
                    self.stats["function_details"].append(func_info)
                
                # 统计类
                elif isinstance(node, ast.ClassDef):
                    file_stats["classes"] += 1
                    class_info = self._analyze_class(node, file_path)
                    self.stats["class_details"].append(class_info)
                
                # 统计导入
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    file_stats["imports"] += 1
                    import_info = self._analyze_import(node, file_path)
                    self.stats["import_details"].append(import_info)
            
            # 更新总体统计
            self.stats["files_analyzed"] += 1
            self.stats["total_functions"] += file_stats["functions"]
            self.stats["total_classes"] += file_stats["classes"]
            self.stats["total_imports"] += file_stats["imports"]
            
            return file_stats
            
        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None
    
    def _analyze_function(self, node, file_path):
        """分析函数节点"""
        # 计算函数长度
        func_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        
        # 统计参数数量
        args_count = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            args_count += 1
        if node.args.kwarg:
            args_count += 1
        
        # 获取装饰器
        decorators = []
        for decorator in node.decorator_list:
            try:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Attribute):
                # 处理如 @app.route 这样的属性装饰器
                    attr_name = decorator.attr
                # 尝试获取value的id，如果value是Name
                    if isinstance(decorator.value, ast.Name):
                        decorators.append(f"{decorator.value.id}.{attr_name}")
                    else:
                        decorators.append(f"?.{attr_name}")
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        decorators.append(decorator.func.id)
                    elif isinstance(decorator.func, ast.Attribute):
                        decorators.append(decorator.func.attr)
            except Exception as e:
            # 如果解析装饰器失败，记录错误并继续
                decorators.append(f"error:{type(decorator).__name__}")
        
        return {
            "file": file_path,
            "name": node.name,
            "line": node.lineno,
            "args": args_count,
            "lines": func_lines,
            "decorators": decorators,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _analyze_class(self, node, file_path):
        """分析类节点"""
        # 查找类中的方法
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        # 查找基类
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
        
        return {
            "file": file_path,
            "name": node.name,
            "line": node.lineno,
            "methods": len(methods),
            "bases": bases,
            "method_names": methods[:5]  # 只取前5个方法名
        }
    
    def _analyze_import(self, node, file_path):
        """分析导入节点"""
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "module": alias.name,
                    "alias": alias.asname,
                    "type": "import"
                })
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({
                    "module": node.module or "",
                    "name": alias.name,
                    "alias": alias.asname,
                    "level": node.level,
                    "type": "from_import"
                })
        
        return {
            "file": file_path,
            "imports": imports
        }
    
    def analyze_directory(self, directory):
        """分析整个目录的Python文件"""
        print(f"分析目录: {directory}")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)
        
        # 生成摘要统计
        summary = {
            "total_files": self.stats["files_analyzed"],
            "total_functions": self.stats["total_functions"],
            "total_classes": self.stats["total_classes"],
            "total_imports": self.stats["total_imports"],
            "avg_functions_per_file": self.stats["total_functions"] / max(self.stats["files_analyzed"], 1),
            "avg_classes_per_file": self.stats["total_classes"] / max(self.stats["files_analyzed"], 1),
        }
        
        return summary
    
    def save_results(self, output_dir):
        """保存分析结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细结果
        with open(os.path.join(output_dir, "ast_analysis_detailed.json"), 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        # 保存函数统计
        function_stats = defaultdict(int)
        for func in self.stats["function_details"]:
            function_stats[func["name"]] += 1
        
        # 保存类统计
        class_stats = defaultdict(int)
        for cls in self.stats["class_details"]:
            class_stats[cls["name"]] += 1
        
        # 保存导入统计
        import_stats = defaultdict(int)
        for imp in self.stats["import_details"]:
            for item in imp["imports"]:
                module = item.get("module") or item.get("name", "")
                if module:
                    import_stats[module] += 1
        
        summary = {
            "function_counts": dict(sorted(function_stats.items(), key=lambda x: x[1], reverse=True)[:20]),
            "class_counts": dict(sorted(class_stats.items(), key=lambda x: x[1], reverse=True)[:20]),
            "import_counts": dict(sorted(import_stats.items(), key=lambda x: x[1], reverse=True)[:20]),
        }
        
        with open(os.path.join(output_dir, "ast_analysis_summary.json"), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"AST分析结果已保存到: {output_dir}")
        return summary

def analyze_flask_version(version_dir, output_dir):
    """分析特定版本的Flask"""
    print(f"\n{'='*60}")
    print(f"分析Flask版本: {os.path.basename(version_dir)}")
    print('='*60)
    
    analyzer = FlaskASTAnalyzer()
    summary = analyzer.analyze_directory(version_dir)
    
    print(f"文件数量: {summary['total_files']}")
    print(f"函数总数: {summary['total_functions']}")
    print(f"类总数: {summary['total_classes']}")
    print(f"导入总数: {summary['total_imports']}")
    print(f"平均每文件函数数: {summary['avg_functions_per_file']:.2f}")
    print(f"平均每文件类数: {summary['avg_classes_per_file']:.2f}")
    
    # 保存结果
    version_output_dir = os.path.join(output_dir, os.path.basename(version_dir))
    analyzer.save_results(version_output_dir)
    
    return summary

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
    
    # 分析所有下载的版本
    repos_dir = os.path.join(RAW_DATA_DIR, "flask_repos")
    output_dir = os.path.join(PROCESSED_DATA_DIR, "static_analysis")
    
    if os.path.exists(repos_dir):
        results = {}
        for version_dir in os.listdir(repos_dir):
            full_path = os.path.join(repos_dir, version_dir)
            if os.path.isdir(full_path):
                try:
                    summary = analyze_flask_version(full_path, output_dir)
                    results[version_dir] = summary
                except Exception as e:
                    print(f"分析 {version_dir} 失败: {e}")
        
        # 保存所有版本的比较结果
        with open(os.path.join(output_dir, "version_comparison.json"), 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n所有版本分析完成！结果保存在: {output_dir}")
    else:
        print(f"Flask源码目录不存在: {repos_dir}")