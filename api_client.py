"""
API 客户端 - 用于与 TODO API 交互的封装

提供了所有 CRUD 操作的方法，简化了测试代码的编写。
"""

import requests
from typing import Optional, Dict, List, Any


class TodoAPIClient:
    """TODO API 客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 基础 URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.api_prefix = "/api"
    
    def _get_url(self, endpoint: str) -> str:
        """构建完整 URL"""
        return f"{self.base_url}{self.api_prefix}{endpoint}"
    
    def get_todos(self) -> Dict[str, Any]:
        """
        获取所有 TODO 列表
        
        Returns:
            包含 todos 列表的字典
        """
        url = self._get_url("/todos")
        response = self.session.get(url)
        return response.json()
    
    def get_todo(self, todo_id: int) -> Dict[str, Any]:
        """
        获取单个 TODO
        
        Args:
            todo_id: TODO ID
            
        Returns:
            TODO 数据字典
        """
        url = self._get_url(f"/todos/{todo_id}")
        response = self.session.get(url)
        if response.status_code == 404:
            return {"error": "Todo not found"}
        return response.json()
    
    def create_todo(self, title: str, completed: bool = False) -> Dict[str, Any]:
        """
        创建新的 TODO
        
        Args:
            title: TODO 标题
            completed: 是否完成（默认 False）
            
        Returns:
            创建的 TODO 数据
        """
        url = self._get_url("/todos")
        data = {
            "title": title,
            "completed": completed
        }
        response = self.session.post(url, json=data)
        return response.json()
    
    def update_todo(
        self, 
        todo_id: int, 
        title: Optional[str] = None, 
        completed: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        更新 TODO
        
        Args:
            todo_id: TODO ID
            title: 新标题（可选）
            completed: 新的完成状态（可选）
            
        Returns:
            更新后的 TODO 数据
        """
        url = self._get_url(f"/todos/{todo_id}")
        data = {}
        
        if title is not None:
            data["title"] = title
        if completed is not None:
            data["completed"] = completed
        
        response = self.session.put(url, json=data)
        if response.status_code == 404:
            return {"error": "Todo not found"}
        return response.json()
    
    def delete_todo(self, todo_id: int) -> Dict[str, Any]:
        """
        删除 TODO
        
        Args:
            todo_id: TODO ID
            
        Returns:
            删除结果字典
        """
        url = self._get_url(f"/todos/{todo_id}")
        response = self.session.delete(url)
        if response.status_code == 404:
            return {"error": "Todo not found"}
        return response.json()
    
    def close(self):
        """关闭会话"""
        self.session.close()


if __name__ == "__main__":
    # 使用示例
    client = TodoAPIClient()
    
    # 创建 TODO
    new_todo = client.create_todo("Learn pytest", completed=False)
    print(f"创建的 TODO: {new_todo}")
    
    # 获取所有 TODO
    todos = client.get_todos()
    print(f"所有 TODO: {todos}")
