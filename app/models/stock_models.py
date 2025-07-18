"""
股票数据模型定义
定义API请求和响应的数据结构
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")


class FundamentalAnalysis(BaseModel):
    """基本面分析数据模型"""
    # 基本信息
    market_cap: Optional[float] = Field(None, description="总市值（亿元）")
    circulating_market_cap: Optional[float] = Field(None, description="流通市值（亿元）")
    total_shares: Optional[float] = Field(None, description="总股本（万股）")
    circulating_shares: Optional[float] = Field(None, description="流通股本（万股）")
    
    # 盈利能力指标
    revenue_ttm: Optional[float] = Field(None, description="营业收入TTM（亿元）")
    net_profit_ttm: Optional[float] = Field(None, description="净利润TTM（亿元）")
    gross_profit_margin: Optional[float] = Field(None, description="毛利率（%）")
    net_profit_margin: Optional[float] = Field(None, description="净利率（%）")
    roe: Optional[float] = Field(None, description="净资产收益率ROE（%）")
    roa: Optional[float] = Field(None, description="总资产收益率ROA（%）")
    
    # 财务健康指标
    debt_to_equity_ratio: Optional[float] = Field(None, description="资产负债率（%）")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    quick_ratio: Optional[float] = Field(None, description="速动比率")
    cash_ratio: Optional[float] = Field(None, description="现金比率")
    
    # 成长性指标
    revenue_growth_yoy: Optional[float] = Field(None, description="营业收入同比增长率（%）")
    net_profit_growth_yoy: Optional[float] = Field(None, description="净利润同比增长率（%）")
    
    # 营运能力指标
    inventory_turnover: Optional[float] = Field(None, description="存货周转率")
    accounts_receivable_turnover: Optional[float] = Field(None, description="应收账款周转率")
    total_asset_turnover: Optional[float] = Field(None, description="总资产周转率")


class ValuationAnalysis(BaseModel):
    """估值分析数据模型"""
    # 市盈率指标
    pe_ratio_static: Optional[float] = Field(None, description="静态市盈率PE")
    pe_ratio_dynamic: Optional[float] = Field(None, description="动态市盈率PE")
    pe_ratio_ttm: Optional[float] = Field(None, description="滚动市盈率PE_TTM")
    
    # 市净率指标
    pb_ratio: Optional[float] = Field(None, description="市净率PB")
    
    # 市销率指标
    ps_ratio: Optional[float] = Field(None, description="市销率PS")
    
    # 企业价值倍数
    ev_ebitda: Optional[float] = Field(None, description="企业价值倍数EV/EBITDA")
    
    # PEG指标
    peg_ratio: Optional[float] = Field(None, description="PEG比率")
    
    # 股息收益率
    dividend_yield: Optional[float] = Field(None, description="股息收益率（%）")
    
    # 行业对比
    industry_pe_median: Optional[float] = Field(None, description="行业PE中位数")
    industry_pb_median: Optional[float] = Field(None, description="行业PB中位数")
    
    # 估值分位数
    pe_percentile_1y: Optional[float] = Field(None, description="PE一年分位数（%）")
    pb_percentile_1y: Optional[float] = Field(None, description="PB一年分位数（%）")


class TechnicalAnalysis(BaseModel):
    """技术面分析数据模型"""
    # 当前价格信息
    current_price: Optional[float] = Field(None, description="当前价格（元）")
    price_change: Optional[float] = Field(None, description="涨跌额（元）")
    price_change_percent: Optional[float] = Field(None, description="涨跌幅（%）")
    
    # 成交量信息
    volume: Optional[float] = Field(None, description="成交量（股）")
    turnover: Optional[float] = Field(None, description="成交额（元）")
    turnover_rate: Optional[float] = Field(None, description="换手率（%）")
    
    # 价格区间
    day_high: Optional[float] = Field(None, description="今日最高价（元）")
    day_low: Optional[float] = Field(None, description="今日最低价（元）")
    week_52_high: Optional[float] = Field(None, description="52周最高价（元）")
    week_52_low: Optional[float] = Field(None, description="52周最低价（元）")
    
    # 技术指标
    ma_5: Optional[float] = Field(None, description="5日均线（元）")
    ma_10: Optional[float] = Field(None, description="10日均线（元）")
    ma_20: Optional[float] = Field(None, description="20日均线（元）")
    ma_60: Optional[float] = Field(None, description="60日均线（元）")
    
    # 相对强弱指标
    rsi_6: Optional[float] = Field(None, description="6日RSI")
    rsi_12: Optional[float] = Field(None, description="12日RSI")
    rsi_24: Optional[float] = Field(None, description="24日RSI")
    
    # MACD指标
    macd_dif: Optional[float] = Field(None, description="MACD DIF")
    macd_dea: Optional[float] = Field(None, description="MACD DEA")
    macd_histogram: Optional[float] = Field(None, description="MACD柱状图")
    
    # 布林带指标
    boll_upper: Optional[float] = Field(None, description="布林带上轨")
    boll_middle: Optional[float] = Field(None, description="布林带中轨")
    boll_lower: Optional[float] = Field(None, description="布林带下轨")


class SentimentAnalysis(BaseModel):
    """消息面分析数据模型"""
    # 资金流向
    main_net_inflow: Optional[float] = Field(None, description="主力净流入（万元）")
    super_large_net_inflow: Optional[float] = Field(None, description="超大单净流入（万元）")
    large_net_inflow: Optional[float] = Field(None, description="大单净流入（万元）")
    medium_net_inflow: Optional[float] = Field(None, description="中单净流入（万元）")
    small_net_inflow: Optional[float] = Field(None, description="小单净流入（万元）")
    
    # 北向资金
    northbound_net_inflow: Optional[float] = Field(None, description="北向资金净流入（万元）")
    
    # 融资融券
    margin_trading_balance: Optional[float] = Field(None, description="融资余额（万元）")
    short_selling_balance: Optional[float] = Field(None, description="融券余额（万元）")
    
    # 机构持仓
    institutional_holdings_ratio: Optional[float] = Field(None, description="机构持股比例（%）")
    
    # 分析师评级
    analyst_rating_avg: Optional[float] = Field(None, description="分析师平均评级")
    analyst_target_price: Optional[float] = Field(None, description="分析师目标价（元）")
    analyst_coverage_count: Optional[int] = Field(None, description="分析师覆盖数量")
    
    # 新闻舆情指标
    news_sentiment_score: Optional[float] = Field(None, description="新闻情感得分")
    news_count_7d: Optional[int] = Field(None, description="7日新闻数量")
    
    # 概念标签
    concept_labels: Optional[List[str]] = Field(None, description="概念标签列表")
    industry_label: Optional[str] = Field(None, description="行业标签")


class StockReport(BaseModel):
    """股票完整报告数据模型"""
    # 基本信息
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    update_time: datetime = Field(..., description="数据更新时间")
    
    # 四大维度分析
    fundamental_analysis: FundamentalAnalysis = Field(..., description="基本面分析")
    valuation_analysis: ValuationAnalysis = Field(..., description="估值分析")
    technical_analysis: TechnicalAnalysis = Field(..., description="技术面分析")
    sentiment_analysis: SentimentAnalysis = Field(..., description="消息面分析")
    
    @validator('code')
    def validate_stock_code(cls, v):
        """验证股票代码格式"""
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('股票代码必须为6位数字')
        return v


class StockCodeRequest(BaseModel):
    """股票代码请求模型"""
    code: str = Field(..., description="股票代码", regex=r"^\d{6}$")
    
    @validator('code')
    def validate_stock_code(cls, v):
        """验证股票代码格式"""
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('股票代码必须为6位数字')
        return v 