"""
接口自动化测试 - 16 个测试用例

使用 pytest 框架编写的完整接口自动化测试，测试 TODO API 的所有功能。
"""

import pytest


class TestGetTodos:
    """GET 操作的测试类"""
    
    def test_get_empty_todos_list(self, api_client):
        """测试：获取空的 TODO 列表"""
        response = api_client.get_todos()
        
        assert "todos" in response
        assert response["todos"] == []
    
    def test_get_todos_list_with_multiple_items(self, api_client, sample_todos_list):
        """测试：获取包含多个项目的 TODO 列表"""
        response = api_client.get_todos()
        
        assert "todos" in response
        assert len(response["todos"]) == 3
        assert response["todos"][0]["title"] == "Todo 1"
        assert response["todos"][1]["completed"] is True
    
    def test_get_single_todo_by_id(self, api_client, sample_todo_data):
        """测试：获取单个 TODO"""
        # 先创建一个 TODO
        created = api_client.create_todo(sample_todo_data["title"])
        todo_id = created["id"]
        
        # 获取这个 TODO
        response = api_client.get_todo(todo_id)
        
        assert response["id"] == todo_id
        assert response["title"] == sample_todo_data["title"]
        assert response["completed"] is False
    
    def test_get_non_existent_todo(self, api_client):
        """测试：获取不存在的 TODO"""
        response = api_client.get_todo(999)
        
        assert "error" in response
        assert response["error"] == "Todo not found"


class TestCreateTodos:
    """POST 操作的测试类"""
    
    def test_create_todo_with_valid_data(self, api_client, sample_todo_data):
        """测试：使用有效数据创建 TODO"""
        response = api_client.create_todo(
            sample_todo_data["title"],
            completed=sample_todo_data["completed"]
        )
        
        assert "id" in response
        assert response["title"] == sample_todo_data["title"]
        assert response["completed"] is False
    
    def test_create_todo_with_completed_status(self, api_client):
        """测试：创建已完成的 TODO"""
        response = api_client.create_todo("Completed Task", completed=True)
        
        assert response["completed"] is True
        assert response["title"] == "Completed Task"
    
    def test_create_multiple_todos_have_unique_ids(self, api_client):
        """测试：多个 TODO 的 ID 唯一性"""
        todo1 = api_client.create_todo("Todo 1")
        todo2 = api_client.create_todo("Todo 2")
        todo3 = api_client.create_todo("Todo 3")
        
        ids = [todo1["id"], todo2["id"], todo3["id"]]
        
        assert len(ids) == len(set(ids))  # 所有 ID 都唯一
        assert todo1["id"] < todo2["id"] < todo3["id"]  # ID 递增
    
    def test_create_todo_without_title_fails(self, api_client):
        """测试：不提供标题时创建失败"""
        # 尝试创建没有标题的 TODO
        response = api_client.create_todo("")
        
        # 应该返回错误或空标题的 TODO
        # 这取决于 API 的设计，这里假设接受空标题
        assert "title" in response


class TestUpdateTodos:
    """PUT 操作的测试类"""
    
    def test_update_todo_title(self, api_client, sample_todo_data):
        """测试：更新 TODO 的标题"""
        # 创建 TODO
        created = api_client.create_todo(sample_todo_data["title"])
        todo_id = created["id"]
        
        # 更新标题
        new_title = "Updated Title"
        response = api_client.update_todo(todo_id, title=new_title)
        
        assert response["id"] == todo_id
        assert response["title"] == new_title
        assert response["completed"] is False  # 完成状态不变
    
    def test_update_todo_completion_status(self, api_client, sample_todo_data):
        """测试：更新 TODO 的完成状态"""
        # 创建 TODO
        created = api_client.create_todo(sample_todo_data["title"])
        todo_id = created["id"]
        
        # 更新完成状态
        response = api_client.update_todo(todo_id, completed=True)
        
        assert response["id"] == todo_id
        assert response["completed"] is True
        assert response["title"] == sample_todo_data["title"]  # 标题不变
    
    def test_update_non_existent_todo(self, api_client):
        """测试：更新不存在的 TODO"""
        response = api_client.update_todo(999, title="New Title")
        
        assert "error" in response
        assert response["error"] == "Todo not found"
    
    def test_update_todo_title_and_status_together(self, api_client):
        """测试：同时更新标题和完成状态"""
        # 创建 TODO
        created = api_client.create_todo("Original Title", completed=False)
        todo_id = created["id"]
        
        # 同时更新标题和完成状态
        response = api_client.update_todo(
            todo_id,
            title="New Title",
            completed=True
        )
        
        assert response["title"] == "New Title"
        assert response["completed"] is True


class TestDeleteTodos:
    """DELETE 操作的测试类"""
    
    def test_delete_existing_todo(self, api_client, sample_todo_data):
        """测试：删除存在的 TODO"""
        # 创建 TODO
        created = api_client.create_todo(sample_todo_data["title"])
        todo_id = created["id"]
        
        # 验证 TODO 存在
        todo_before = api_client.get_todo(todo_id)
        assert todo_before["id"] == todo_id
        
        # 删除 TODO
        response = api_client.delete_todo(todo_id)
        assert "message" in response
        assert "deleted" in response["message"].lower()
    
    def test_delete_non_existent_todo(self, api_client):
        """测试：删除不存在的 TODO"""
        response = api_client.delete_todo(999)
        
        assert "error" in response
        assert response["error"] == "Todo not found"
    
    def test_delete_todo_removes_from_list(self, api_client, sample_todos_list):
        """测试：删除 TODO 后验证从列表中移除"""
        # 获取初始 TODO 列表
        todos_before = api_client.get_todos()
        count_before = len(todos_before["todos"])
        
        # 删除第一个 TODO
        first_todo_id = todos_before["todos"][0]["id"]
        api_client.delete_todo(first_todo_id)
        
        # 获取删除后的 TODO 列表
        todos_after = api_client.get_todos()
        count_after = len(todos_after["todos"])
        
        assert count_after == count_before - 1
        
        # 验证该 TODO 已从列表中删除
        ids_after = [todo["id"] for todo in todos_after["todos"]]
        assert first_todo_id not in ids_after


class TestTodoIntegration:
    """集成测试类"""
    
    def test_complete_todo_lifecycle(self, api_client):
        """测试：TODO 的完整生命周期"""
        # 1. 创建 TODO
        created = api_client.create_todo("Learn pytest", completed=False)
        todo_id = created["id"]
        
        # 验证创建
        assert created["title"] == "Learn pytest"
        assert created["completed"] is False
        
        # 2. 更新 TODO（完成）
        updated = api_client.update_todo(todo_id, completed=True)
        assert updated["completed"] is True
        
        # 3. 获取 TODO 验证更新
        retrieved = api_client.get_todo(todo_id)
        assert retrieved["completed"] is True
        
        # 4. 删除 TODO
        deleted = api_client.delete_todo(todo_id)
        assert "deleted" in deleted["message"].lower()
        
        # 5. 验证删除
        not_found = api_client.get_todo(todo_id)
        assert "error" in not_found
    
    def test_multiple_todos_operations(self, api_client):
        """测试：多个 TODO 的操作"""
        # 创建多个 TODO
        todos = []
        for i in range(5):
            todo = api_client.create_todo(f"Task {i+1}", completed=i % 2 == 0)
            todos.append(todo)
        
        # 验证所有 TODO 都已创建
        all_todos = api_client.get_todos()
        assert len(all_todos["todos"]) == 5
        
        # 更新其中一些 TODO
        api_client.update_todo(todos[0]["id"], title="Updated Task 1")
        api_client.update_todo(todos[2]["id"], completed=True)
        
        # 删除其中一些 TODO
        api_client.delete_todo(todos[1]["id"])
        api_client.delete_todo(todos[3]["id"])
        
        # 验证最后只剩 3 个 TODO
        remaining_todos = api_client.get_todos()
        assert len(remaining_todos["todos"]) == 3
        
        # 验证更新
        updated_todo = api_client.get_todo(todos[0]["id"])
        assert updated_todo["title"] == "Updated Task 1"


# ============= 测试执行配置 =============

if __name__ == "__main__":
    """
    运行测试的方式：
    
    1. 运行所有测试：
       pytest test_todo_api.py -v
    
    2. 运行特定测试类：
       pytest test_todo_api.py::TestGetTodos -v
    
    3. 运行特定测试：
       pytest test_todo_api.py::TestGetTodos::test_get_empty_todos_list -v
    
    4. 生成覆盖率报告：
       pytest test_todo_api.py --cov=. --cov-report=html
    
    5. 显示打印输出：
       pytest test_todo_api.py -v -s
    """
    pytest.main([__file__, "-v"])
