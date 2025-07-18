"""
股票服务模块
封装所有与akshare交互和数据处理的函数
"""
import asyncio
import logging
import traceback
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, Any
import pandas as pd
import akshare as ak
from app.models.stock_models import (
    StockReport, FundamentalAnalysis, ValuationAnalysis, 
    TechnicalAnalysis, SentimentAnalysis
)
from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataError(Exception):
    """股票数据获取异常"""
    pass


class StockNotFoundError(Exception):
    """股票未找到异常"""
    pass


class StockService:
    """股票服务类"""
    
    def __init__(self):
        self._cache = {}
        self._last_clear_cache = datetime.now()
    
    def _get_cache_key(self, stock_code: str) -> str:
        """生成缓存键"""
        return f"stock_{stock_code}"
    
    def _is_cache_expired(self, cache_time: datetime) -> bool:
        """检查缓存是否过期"""
        return (datetime.now() - cache_time).seconds > settings.CACHE_TTL
    
    def _clear_expired_cache(self):
        """清理过期缓存"""
        current_time = datetime.now()
        if (current_time - self._last_clear_cache).seconds > settings.CACHE_TTL:
            expired_keys = []
            for key, (data, cache_time) in self._cache.items():
                if self._is_cache_expired(cache_time):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            self._last_clear_cache = current_time
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    @lru_cache(maxsize=settings.MAX_CACHE_SIZE)
    def _get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if stock_info.empty:
                raise StockNotFoundError(f"股票代码 {stock_code} 不存在")
            
            # 转换为字典格式
            info_dict = {}
            for _, row in stock_info.iterrows():
                info_dict[row['item']] = row['value']
            
            return info_dict
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {stock_code}, 错误: {str(e)}")
            raise StockDataError(f"获取股票基本信息失败: {str(e)}")
    
    def _safe_get_float(self, value: Any, default: Optional[float] = None) -> Optional[float]:
        """安全获取浮点数值"""
        try:
            if value is None or value == '' or str(value).strip() == '-':
                return default
            return float(str(value).replace(',', '').replace('%', ''))
        except (ValueError, TypeError):
            return default
    
    def _safe_get_int(self, value: Any, default: Optional[int] = None) -> Optional[int]:
        """安全获取整数值"""
        try:
            if value is None or value == '' or str(value).strip() == '-':
                return default
            return int(float(str(value).replace(',', '')))
        except (ValueError, TypeError):
            return default
    
    async def _get_fundamental_data(self, stock_code: str) -> FundamentalAnalysis:
        """获取基本面数据"""
        try:
            # 获取股票基本信息
            stock_info = self._get_stock_info(stock_code)
            
            # 获取财务指标
            financial_analysis = ak.stock_financial_analysis_indicator(symbol=stock_code)
            
            # 初始化返回数据
            fundamental_data = {}
            
            # 从基本信息中提取数据
            fundamental_data['market_cap'] = self._safe_get_float(stock_info.get('总市值'))
            fundamental_data['circulating_market_cap'] = self._safe_get_float(stock_info.get('流通市值'))
            fundamental_data['total_shares'] = self._safe_get_float(stock_info.get('总股本'))
            fundamental_data['circulating_shares'] = self._safe_get_float(stock_info.get('流通股'))
            
            # 从财务分析中提取数据（取最新一期数据）
            if not financial_analysis.empty:
                latest_data = financial_analysis.iloc[-1]
                fundamental_data['revenue_ttm'] = self._safe_get_float(latest_data.get('营业收入'))
                fundamental_data['net_profit_ttm'] = self._safe_get_float(latest_data.get('净利润'))
                fundamental_data['gross_profit_margin'] = self._safe_get_float(latest_data.get('毛利率'))
                fundamental_data['net_profit_margin'] = self._safe_get_float(latest_data.get('净利率'))
                fundamental_data['roe'] = self._safe_get_float(latest_data.get('净资产收益率'))
                fundamental_data['roa'] = self._safe_get_float(latest_data.get('总资产收益率'))
                fundamental_data['debt_to_equity_ratio'] = self._safe_get_float(latest_data.get('资产负债比率'))
                fundamental_data['current_ratio'] = self._safe_get_float(latest_data.get('流动比率'))
                fundamental_data['quick_ratio'] = self._safe_get_float(latest_data.get('速动比率'))
            
            return FundamentalAnalysis(**fundamental_data)
        
        except Exception as e:
            logger.error(f"获取基本面数据失败: {stock_code}, 错误: {str(e)}")
            return FundamentalAnalysis()
    
    async def _get_valuation_data(self, stock_code: str) -> ValuationAnalysis:
        """获取估值数据"""
        try:
            # 获取估值指标
            stock_info = self._get_stock_info(stock_code)
            
            valuation_data = {
                'pe_ratio_static': self._safe_get_float(stock_info.get('市盈率-静态')),
                'pe_ratio_dynamic': self._safe_get_float(stock_info.get('市盈率-动态')),
                'pe_ratio_ttm': self._safe_get_float(stock_info.get('市盈率TTM')),
                'pb_ratio': self._safe_get_float(stock_info.get('市净率')),
                'ps_ratio': self._safe_get_float(stock_info.get('市销率')),
                'dividend_yield': self._safe_get_float(stock_info.get('股息率')),
            }
            
            return ValuationAnalysis(**valuation_data)
        
        except Exception as e:
            logger.error(f"获取估值数据失败: {stock_code}, 错误: {str(e)}")
            return ValuationAnalysis()
    
    async def _get_technical_data(self, stock_code: str) -> TechnicalAnalysis:
        """获取技术面数据"""
        try:
            # 获取实时行情数据
            current_data = ak.stock_zh_a_spot_em()
            stock_current = current_data[current_data['代码'] == stock_code]
            
            # 获取历史行情数据用于计算技术指标
            hist_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                          start_date="20240101", end_date="20241231", adjust="")
            
            technical_data = {}
            
            if not stock_current.empty:
                current_row = stock_current.iloc[0]
                technical_data['current_price'] = self._safe_get_float(current_row.get('最新价'))
                technical_data['price_change'] = self._safe_get_float(current_row.get('涨跌额'))
                technical_data['price_change_percent'] = self._safe_get_float(current_row.get('涨跌幅'))
                technical_data['volume'] = self._safe_get_float(current_row.get('成交量'))
                technical_data['turnover'] = self._safe_get_float(current_row.get('成交额'))
                technical_data['turnover_rate'] = self._safe_get_float(current_row.get('换手率'))
                technical_data['day_high'] = self._safe_get_float(current_row.get('最高'))
                technical_data['day_low'] = self._safe_get_float(current_row.get('最低'))
            
            # 计算移动平均线
            if not hist_data.empty and len(hist_data) >= 60:
                hist_data['收盘'] = pd.to_numeric(hist_data['收盘'], errors='coerce')
                technical_data['ma_5'] = hist_data['收盘'].rolling(window=5).mean().iloc[-1]
                technical_data['ma_10'] = hist_data['收盘'].rolling(window=10).mean().iloc[-1]
                technical_data['ma_20'] = hist_data['收盘'].rolling(window=20).mean().iloc[-1]
                technical_data['ma_60'] = hist_data['收盘'].rolling(window=60).mean().iloc[-1]
                
                # 计算52周高低点
                technical_data['week_52_high'] = hist_data['收盘'].max()
                technical_data['week_52_low'] = hist_data['收盘'].min()
            
            return TechnicalAnalysis(**technical_data)
        
        except Exception as e:
            logger.error(f"获取技术面数据失败: {stock_code}, 错误: {str(e)}")
            return TechnicalAnalysis()
    
    async def _get_sentiment_data(self, stock_code: str) -> SentimentAnalysis:
        """获取消息面数据"""
        try:
            sentiment_data = {}
            
            # 获取资金流向数据
            try:
                flow_data = ak.stock_individual_fund_flow(stock=stock_code, market="sh" if stock_code.startswith('6') else "sz")
                if not flow_data.empty:
                    latest_flow = flow_data.iloc[-1]
                    sentiment_data['main_net_inflow'] = self._safe_get_float(latest_flow.get('主力净流入-净额'))
                    sentiment_data['super_large_net_inflow'] = self._safe_get_float(latest_flow.get('超大单净流入-净额'))
                    sentiment_data['large_net_inflow'] = self._safe_get_float(latest_flow.get('大单净流入-净额'))
                    sentiment_data['medium_net_inflow'] = self._safe_get_float(latest_flow.get('中单净流入-净额'))
                    sentiment_data['small_net_inflow'] = self._safe_get_float(latest_flow.get('小单净流入-净额'))
            except Exception:
                pass
            
            # 获取概念标签
            try:
                concept_data = ak.stock_board_concept_cons_em(symbol="东方财富")
                concepts = concept_data[concept_data['代码'] == stock_code]['板块名称'].tolist() if not concept_data.empty else []
                sentiment_data['concept_labels'] = concepts[:10]  # 限制数量
            except Exception:
                sentiment_data['concept_labels'] = []
            
            return SentimentAnalysis(**sentiment_data)
        
        except Exception as e:
            logger.error(f"获取消息面数据失败: {stock_code}, 错误: {str(e)}")
            return SentimentAnalysis()
    
    async def get_full_stock_report(self, stock_code: str) -> StockReport:
        """获取完整的股票报告"""
        # 检查缓存
        cache_key = self._get_cache_key(stock_code)
        if cache_key in self._cache:
            cached_data, cache_time = self._cache[cache_key]
            if not self._is_cache_expired(cache_time):
                logger.info(f"从缓存获取股票数据: {stock_code}")
                return cached_data
        
        # 清理过期缓存
        self._clear_expired_cache()
        
        try:
            # 验证股票代码是否存在
            stock_info = self._get_stock_info(stock_code)
            stock_name = stock_info.get('股票简称', '')
            
            if not stock_name:
                raise StockNotFoundError(f"未找到股票代码 {stock_code} 对应的股票")
            
            # 并发获取各维度数据
            fundamental_task = self._get_fundamental_data(stock_code)
            valuation_task = self._get_valuation_data(stock_code)
            technical_task = self._get_technical_data(stock_code)
            sentiment_task = self._get_sentiment_data(stock_code)
            
            # 等待所有任务完成
            fundamental_analysis, valuation_analysis, technical_analysis, sentiment_analysis = await asyncio.gather(
                fundamental_task, valuation_task, technical_task, sentiment_task,
                return_exceptions=True
            )
            
            # 处理异常结果
            if isinstance(fundamental_analysis, Exception):
                logger.error(f"基本面数据获取异常: {fundamental_analysis}")
                fundamental_analysis = FundamentalAnalysis()
            
            if isinstance(valuation_analysis, Exception):
                logger.error(f"估值数据获取异常: {valuation_analysis}")
                valuation_analysis = ValuationAnalysis()
            
            if isinstance(technical_analysis, Exception):
                logger.error(f"技术面数据获取异常: {technical_analysis}")
                technical_analysis = TechnicalAnalysis()
            
            if isinstance(sentiment_analysis, Exception):
                logger.error(f"消息面数据获取异常: {sentiment_analysis}")
                sentiment_analysis = SentimentAnalysis()
            
            # 构建完整报告
            report = StockReport(
                code=stock_code,
                name=stock_name,
                update_time=datetime.now(),
                fundamental_analysis=fundamental_analysis,
                valuation_analysis=valuation_analysis,
                technical_analysis=technical_analysis,
                sentiment_analysis=sentiment_analysis
            )
            
            # 缓存结果
            if len(self._cache) < settings.MAX_CACHE_SIZE:
                self._cache[cache_key] = (report, datetime.now())
            
            logger.info(f"成功获取股票完整报告: {stock_code} - {stock_name}")
            return report
        
        except StockNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取股票报告失败: {stock_code}, 错误: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            raise StockDataError(f"获取股票数据失败: {str(e)}")


# 全局股票服务实例
stock_service = StockService() 