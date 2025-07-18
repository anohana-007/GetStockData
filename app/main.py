"""
DataQuark Stock Analysis API
FastAPI应用实例和API路由定义
"""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.config import settings
from app.models.stock_models import StockReport, ErrorResponse
from app.services.stock_service import stock_service, StockNotFoundError, StockDataError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """处理数据验证异常"""
    logger.error(f"数据验证错误: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"请求数据格式错误: {str(exc)}"}
    )


@app.exception_handler(StockNotFoundError)
async def stock_not_found_exception_handler(request, exc):
    """处理股票未找到异常"""
    logger.warning(f"股票未找到: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(StockDataError)
async def stock_data_exception_handler(request, exc):
    """处理股票数据获取异常"""
    logger.error(f"股票数据获取错误: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"股票数据获取失败: {str(exc)}"}
    )


@app.get("/", tags=["根路径"])
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用 DataQuark Stock Analysis API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "current_time": datetime.now().isoformat()
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION
    }


@app.get(
    f"{settings.API_V1_PREFIX}/stock/full-report",
    response_model=StockReport,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        404: {"model": ErrorResponse, "description": "股票未找到"},
        500: {"model": ErrorResponse, "description": "内部服务器错误"},
    },
    tags=["股票分析"],
    summary="获取股票完整分析报告",
    description="根据股票代码获取包含基本面、估值、技术面和消息面四大维度的完整分析数据"
)
async def get_stock_full_report(
    code: str = Query(
        ...,
        regex=r"^\d{6}$",
        description="6位A股股票代码，例如：600519（贵州茅台）",
        example="600519"
    )
):
    """
    获取股票完整分析报告
    
    **参数说明:**
    - **code**: 6位数字的A股股票代码（必填）
    
    **返回数据包含:**
    - 基本面分析：市值、盈利能力、财务健康度等指标
    - 估值分析：PE、PB、PS等估值指标
    - 技术面分析：价格、成交量、技术指标等
    - 消息面分析：资金流向、概念标签等
    
    **使用示例:**
    ```
    GET /api/v1/stock/full-report?code=600519
    ```
    """
    try:
        # 验证股票代码格式
        if not code or len(code) != 6 or not code.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="股票代码格式错误，必须为6位数字"
            )
        
        logger.info(f"接收到股票分析请求: {code}")
        
        # 获取股票完整报告
        report = await stock_service.get_full_stock_report(code)
        
        logger.info(f"成功返回股票分析报告: {code} - {report.name}")
        return report
        
    except StockNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except StockDataError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请求数据验证失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务暂时不可用，请稍后重试"
        )


@app.get(f"{settings.API_V1_PREFIX}/stock/info", tags=["股票信息"])
async def get_stock_basic_info(
    code: str = Query(
        ...,
        regex=r"^\d{6}$",
        description="6位A股股票代码",
        example="600519"
    )
):
    """获取股票基本信息（简化版）"""
    try:
        if not code or len(code) != 6 or not code.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="股票代码格式错误，必须为6位数字"
            )
        
        # 这里可以实现简化版的股票信息获取
        # 为了演示，我们返回一个简单的信息
        return {
            "code": code,
            "message": "股票基本信息功能暂未实现，请使用 /full-report 获取完整信息",
            "full_report_url": f"{settings.API_V1_PREFIX}/stock/full-report?code={code}"
        }
        
    except Exception as e:
        logger.error(f"获取股票基本信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取股票基本信息失败"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 