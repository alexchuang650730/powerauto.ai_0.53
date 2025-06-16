"""
为SmartUI添加MCP状态检查端点
"""

# 在现有的api_server.py中添加以下端点

@app.route('/api/mcp/status')
def get_mcp_status():
    """获取MCP组件状态 - 为前端提供实时状态"""
    try:
        import requests
        
        # 从MCP状态API获取数据
        response = requests.get('http://localhost:8095/api/mcp/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # 格式化为前端需要的格式
            mcp_list = []
            for mcp_id, mcp_info in data['data']['mcps'].items():
                mcp_list.append({
                    'id': mcp_id,
                    'name': mcp_info['name'],
                    'status': mcp_info['status'],
                    'health': mcp_info.get('health', 'unknown'),
                    'version': mcp_info.get('version', 'unknown'),
                    'url': mcp_info['url'],
                    'capabilities': mcp_info.get('capabilities', [])
                })
            
            return jsonify({
                "success": True,
                "data": {
                    "mcps": mcp_list,
                    "total": len(mcp_list),
                    "coordinator_status": data['data']['coordinator_status'],
                    "timestamp": data['data']['timestamp']
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "无法获取MCP状态"
            }), 500
            
    except Exception as e:
        logger.error(f"获取MCP状态失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/mcp/coordinator')
def get_coordinator_info():
    """获取MCP协调器信息"""
    try:
        import requests
        
        response = requests.get('http://localhost:8095/api/mcp/coordinator/status', timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({
                "success": False,
                "error": "协调器不可用"
            }), 500
            
    except Exception as e:
        logger.error(f"获取协调器信息失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

