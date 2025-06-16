#!/usr/bin/env python3
"""
Document Center MCP - PowerAutomation 统一文档管理中心

负责管理整个PowerAutomation生态系统的文档，包括：
- 六大工作流文档
- 三大产品版本文档  
- 核心架构文档
- SmartUI组件文档
- 验证报告文档
"""

from flask import Flask, jsonify, request, send_from_directory
import os
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 文档中心配置
DOCUMENT_CENTER_CONFIG = {
    "name": "Document Center MCP",
    "version": "1.0.0",
    "description": "PowerAutomation 统一文档管理中心",
    "port": 8093,
    "base_path": "/opt/powerautomation/docs/document_center"
}

# 文档分类
DOCUMENT_CATEGORIES = {
    "workflows": {
        "name": "工作流文档",
        "description": "六大工作流MCP的完整文档",
        "path": "docs/workflows"
    },
    "products": {
        "name": "产品版本文档", 
        "description": "Enterprise/Personal/Opensource三大版本对比",
        "path": "docs/products"
    },
    "architecture": {
        "name": "架构设计文档",
        "description": "核心架构和设计文档",
        "path": "docs/architecture"
    },
    "smartui": {
        "name": "SmartUI文档",
        "description": "SmartUI组件完整文档集",
        "path": "docs/smartui"
    },
    "reports": {
        "name": "验证报告",
        "description": "系统验证和完成报告",
        "path": "docs/reports"
    },
    "templates": {
        "name": "文档模板",
        "description": "标准化文档模板",
        "path": "templates"
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "running",
        "name": DOCUMENT_CENTER_CONFIG["name"],
        "version": DOCUMENT_CENTER_CONFIG["version"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/info', methods=['GET'])
def get_info():
    """获取Document Center信息"""
    return jsonify({
        "name": DOCUMENT_CENTER_CONFIG["name"],
        "version": DOCUMENT_CENTER_CONFIG["version"],
        "description": DOCUMENT_CENTER_CONFIG["description"],
        "categories": DOCUMENT_CATEGORIES,
        "endpoints": [
            "/health",
            "/info", 
            "/categories",
            "/documents/<category>",
            "/document/<category>/<filename>",
            "/search"
        ]
    })

@app.route('/categories', methods=['GET'])
def get_categories():
    """获取所有文档分类"""
    categories_with_counts = {}
    
    for category_id, category_info in DOCUMENT_CATEGORIES.items():
        category_path = os.path.join(DOCUMENT_CENTER_CONFIG["base_path"], category_info["path"])
        
        # 统计文档数量
        doc_count = 0
        if os.path.exists(category_path):
            for root, dirs, files in os.walk(category_path):
                doc_count += len([f for f in files if f.endswith('.md')])
        
        categories_with_counts[category_id] = {
            **category_info,
            "document_count": doc_count
        }
    
    return jsonify({
        "categories": categories_with_counts,
        "total_categories": len(DOCUMENT_CATEGORIES)
    })

@app.route('/documents/<category>', methods=['GET'])
def get_documents_by_category(category):
    """获取指定分类的所有文档"""
    if category not in DOCUMENT_CATEGORIES:
        return jsonify({"error": f"Category '{category}' not found"}), 404
    
    category_info = DOCUMENT_CATEGORIES[category]
    category_path = os.path.join(DOCUMENT_CENTER_CONFIG["base_path"], category_info["path"])
    
    if not os.path.exists(category_path):
        return jsonify({"error": f"Category path not found: {category_path}"}), 404
    
    documents = []
    for root, dirs, files in os.walk(category_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, category_path)
                
                # 获取文件信息
                stat = os.stat(file_path)
                documents.append({
                    "filename": file,
                    "relative_path": relative_path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    return jsonify({
        "category": category,
        "category_info": category_info,
        "documents": documents,
        "total_documents": len(documents)
    })

@app.route('/document/<category>/<path:filename>', methods=['GET'])
def get_document_content(category, filename):
    """获取指定文档的内容"""
    if category not in DOCUMENT_CATEGORIES:
        return jsonify({"error": f"Category '{category}' not found"}), 404
    
    category_info = DOCUMENT_CATEGORIES[category]
    category_path = os.path.join(DOCUMENT_CENTER_CONFIG["base_path"], category_info["path"])
    file_path = os.path.join(category_path, filename)
    
    # 安全检查：确保文件在允许的目录内
    if not os.path.abspath(file_path).startswith(os.path.abspath(category_path)):
        return jsonify({"error": "Access denied"}), 403
    
    if not os.path.exists(file_path):
        return jsonify({"error": f"Document not found: {filename}"}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stat = os.stat(file_path)
        return jsonify({
            "filename": filename,
            "category": category,
            "content": content,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    except Exception as e:
        logger.error(f"Error reading document {filename}: {str(e)}")
        return jsonify({"error": f"Error reading document: {str(e)}"}), 500

@app.route('/search', methods=['GET'])
def search_documents():
    """搜索文档内容"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    results = []
    search_categories = [category] if category and category in DOCUMENT_CATEGORIES else DOCUMENT_CATEGORIES.keys()
    
    for cat in search_categories:
        category_info = DOCUMENT_CATEGORIES[cat]
        category_path = os.path.join(DOCUMENT_CENTER_CONFIG["base_path"], category_info["path"])
        
        if not os.path.exists(category_path):
            continue
        
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 简单的文本搜索
                        if query.lower() in content.lower() or query.lower() in file.lower():
                            relative_path = os.path.relpath(file_path, category_path)
                            results.append({
                                "filename": file,
                                "category": cat,
                                "relative_path": relative_path,
                                "matches": content.lower().count(query.lower())
                            })
                    except Exception as e:
                        logger.warning(f"Error searching in {file_path}: {str(e)}")
    
    # 按匹配数量排序
    results.sort(key=lambda x: x["matches"], reverse=True)
    
    return jsonify({
        "query": query,
        "results": results,
        "total_results": len(results)
    })

@app.route('/stats', methods=['GET'])
def get_statistics():
    """获取文档中心统计信息"""
    stats = {
        "categories": len(DOCUMENT_CATEGORIES),
        "total_documents": 0,
        "total_size": 0,
        "category_stats": {}
    }
    
    for category_id, category_info in DOCUMENT_CATEGORIES.items():
        category_path = os.path.join(DOCUMENT_CENTER_CONFIG["base_path"], category_info["path"])
        
        category_stats = {
            "documents": 0,
            "size": 0
        }
        
        if os.path.exists(category_path):
            for root, dirs, files in os.walk(category_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        category_stats["documents"] += 1
                        category_stats["size"] += file_size
        
        stats["category_stats"][category_id] = category_stats
        stats["total_documents"] += category_stats["documents"]
        stats["total_size"] += category_stats["size"]
    
    return jsonify(stats)

if __name__ == '__main__':
    logger.info(f"Starting {DOCUMENT_CENTER_CONFIG['name']} v{DOCUMENT_CENTER_CONFIG['version']}")
    logger.info(f"Document base path: {DOCUMENT_CENTER_CONFIG['base_path']}")
    
    app.run(
        host='0.0.0.0',
        port=DOCUMENT_CENTER_CONFIG['port'],
        debug=False
    )

