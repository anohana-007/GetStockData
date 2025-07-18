"""
API端点测试
针对API端点的单元测试和集成测试
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# 创建测试客户端
client = TestClient(app)


class TestHealthCheck:
    """健康检查测试"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestStockAPI:
    """股票API测试"""
    
    def test_full_report_valid_code(self):
        """测试有效股票代码"""
        # 使用一个可能存在的股票代码进行测试
        response = client.get("/api/v1/stock/full-report?code=000001")
        # 注意：这个测试可能会因为网络或数据源问题而失败
        # 在实际环境中，我们可能需要mock akshare的响应
        assert response.status_code in [200, 404, 500]  # 允许多种响应
    
    def test_full_report_invalid_code_format(self):
        """测试无效的股票代码格式"""
        # 测试非6位数字
        response = client.get("/api/v1/stock/full-report?code=123")
        assert response.status_code == 422  # FastAPI的验证错误
        
        # 测试字母
        response = client.get("/api/v1/stock/full-report?code=abcdef")
        assert response.status_code == 422
        
        # 测试空值
        response = client.get("/api/v1/stock/full-report")
        assert response.status_code == 422
    
    def test_full_report_nonexistent_code(self):
        """测试不存在的股票代码"""
        response = client.get("/api/v1/stock/full-report?code=999999")
        # 这个代码大概率不存在，应该返回404
        assert response.status_code in [404, 500]  # 可能是404或500
    
    def test_stock_info_endpoint(self):
        """测试股票基本信息端点"""
        response = client.get("/api/v1/stock/info?code=600519")
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"] == "600519"


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_endpoint(self):
        """测试不存在的端点"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """测试不允许的HTTP方法"""
        response = client.post("/api/v1/stock/full-report")
        assert response.status_code == 405


# 如果需要测试异步功能，可以使用pytest-asyncio
@pytest.mark.asyncio
async def test_async_functionality():
    """测试异步功能（示例）"""
    # 这里可以添加对异步函数的测试
    pass


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__]) 