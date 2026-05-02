"""
Mock Server - 模拟 TODO API 服务器

基于 Flask 的完整 TODO API 实现，用于接口自动化测试。
"""

from flask import Flask, request, jsonify
import threading
from typing import Dict, List, Any, Optional


class MockServer:
    """模拟 TODO API 服务器"""
    
    def __init__(self, port: int = 5000):
        """
        初始化模拟服务器
        
        Args:
            port: 服务器端口
        """
        self.port = port
        self.app = Flask(__name__)
        self.todos: Dict[int, Dict[str, Any]] = {}
        self.next_id = 1
        self.thread: Optional[threading.Thread] = None
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/api/todos', methods=['GET'])
        def get_todos():
            """获取所有 TODO"""
            todos_list = list(self.todos.values())
            return jsonify({"todos": todos_list}), 200
        
        @self.app.route('/api/todos/<int:todo_id>', methods=['GET'])
        def get_todo(todo_id: int):
            """获取单个 TODO"""
            if todo_id not in self.todos:
                return jsonify({"error": "Todo not found"}), 404
            return jsonify(self.todos[todo_id]), 200
        
        @self.app.route('/api/todos', methods=['POST'])
        def create_todo():
            """创建新 TODO"""
            data = request.get_json()
            
            # 验证必需字段
            if not data or 'title' not in data:
                return jsonify({"error": "Title is required"}), 400
            
            todo = {
                "id": self.next_id,
                "title": data['title'],
                "completed": data.get('completed', False)
            }
            
            self.todos[self.next_id] = todo
            self.next_id += 1
            
            return jsonify(todo), 201
        
        @self.app.route('/api/todos/<int:todo_id>', methods=['PUT'])
        def update_todo(todo_id: int):
            """更新 TODO"""
            if todo_id not in self.todos:
                return jsonify({"error": "Todo not found"}), 404
            
            data = request.get_json()
            todo = self.todos[todo_id]
            
            if 'title' in data:
                todo['title'] = data['title']
            if 'completed' in data:
                todo['completed'] = data['completed']
            
            return jsonify(todo), 200
        
        @self.app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
        def delete_todo(todo_id: int):
            """删除 TODO"""
            if todo_id not in self.todos:
                return jsonify({"error": "Todo not found"}), 404
            
            deleted = self.todos.pop(todo_id)
            return jsonify({"message": "Todo deleted", "todo": deleted}), 200
        
        @self.app.route('/api/todos', methods=['DELETE'])
        def clear_todos():
            """清空所有 TODO"""
            count = len(self.todos)
            self.todos.clear()
            self.next_id = 1
            return jsonify({"message": f"{count} todos deleted"}), 200
    
    def start(self):
        """启动服务器"""
        def run():
            self.app.run(port=self.port, debug=False, use_reloader=False)
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """停止服务器"""
        # Flask 没有直接的停止方法，线程设置为 daemon 会在主线程退出时自动停止
        pass
    
    def clear_data(self):
        """清空所有数据"""
        self.todos.clear()
        self.next_id = 1


def get_mock_server(port: int = 5000) -> MockServer:
    """
    创建和获取模拟服务器实例
    
    Args:
        port: 服务器端口
        
    Returns:
        MockServer 实例
    """
    return MockServer(port)


if __name__ == "__main__":
    import time
    
    # 启动服务器
    server = get_mock_server()
    server.start()
    print("Mock server started on http://localhost:5000")
    
    # 让服务器运行 10 秒
    time.sleep(10)
    
    # 停止服务器
    server.stop()
    print("Mock server stopped")
