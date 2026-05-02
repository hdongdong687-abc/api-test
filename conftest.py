"""
pytest 配置文件 - Fixtures 和测试配置

包含所有的 pytest fixtures 和测试环境配置。
"""

import pytest
import time
from api_client import TodoAPIClient
from mock_server import get_mock_server


# ============= 会话级 Fixtures =============

@pytest.fixture(scope="session")
def mock_server():
    """
    会话级 fixture：启动和停止模拟服务器
    
    在整个测试会话的开始启动服务器，结束时停止。
    """
    server = get_mock_server(port=5000)
    server.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    yield server
    
    server.stop()


# ============= 函数级 Fixtures =============

@pytest.fixture(autouse=True)
def clear_todos(mock_server):
    """
    自动使用的 fixture：在每个测试前清空所有 TODO
    
    Args:
        mock_server: 模拟服务器 fixture
    """
    # 测试前清空
    mock_server.clear_data()
    
    yield
    
    # 测试后清空（可选）
    mock_server.clear_data()


@pytest.fixture
def api_client(mock_server):
    """
    提供 API 客户端实例
    
    Args:
        mock_server: 模拟服务器 fixture
        
    Returns:
        TodoAPIClient 实例
    """
    client = TodoAPIClient(base_url="http://localhost:5000")
    
    yield client
    
    # 清理
    client.close()


# ============= 测试数据 Fixtures =============

@pytest.fixture
def sample_todo_data():
    """
    示例 TODO 数据
    
    Returns:
        包含一个示例 TODO 的字典
    """
    return {
        "title": "Test Todo",
        "completed": False
    }


@pytest.fixture
def sample_completed_todo():
    """
    已完成的示例 TODO 数据
    
    Returns:
        包含一个已完成的示例 TODO 的字典
    """
    return {
        "title": "Completed Todo",
        "completed": True
    }


@pytest.fixture
def sample_todos_list(api_client):
    """
    创建多个示例 TODO
    
    Args:
        api_client: API 客户端 fixture
        
    Returns:
        创建的 TODO 列表
    """
    todos_data = [
        {"title": "Todo 1", "completed": False},
        {"title": "Todo 2", "completed": True},
        {"title": "Todo 3", "completed": False},
    ]
    
    created_todos = []
    for todo_data in todos_data:
        response = api_client.create_todo(
            todo_data["title"],
            completed=todo_data["completed"]
        )
        created_todos.append(response)
    
    return created_todos


# ============= pytest 配置 =============

def pytest_configure(config):
    """pytest 配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试集合"""
    # 可以在这里添加自定义的测试修改逻辑
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
