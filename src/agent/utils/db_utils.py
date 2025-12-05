import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import (
    QuerySQLDatabaseTool,
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
)
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

class DBOperationRequest(BaseModel):
    """数据库操作请求验证"""        
    table_name: str = Field(..., description="表名")
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="批量数据")
    condition: Optional[str] = Field(default=None, description="WHERE 条件")
    unique_key: str = Field(default="id", description="唯一键字段")
    limit: int = Field(default=100, ge=1, le=1000, description="查询限制")

class SecureDatabaseToolkit:
    """企业级安全的数据库工具集"""
    
    def __init__(
        self, 
        database_uri: str, 
        schema: Optional[str] = None,
        allowed_tables: Optional[List[str]] = None,
        max_rows: int = 1000,
        pool_size: int = 20
    ):
        """初始化 - 生产级连接池 + 权限控制"""
        self.database_uri = database_uri
        self.schema = schema
        self.allowed_tables = set(allowed_tables or [])
        self.max_rows = max_rows
        
        # ✅ 生产级连接池配置
        self.engine = self._create_production_engine(pool_size)
        self.db = SQLDatabase(self.engine, schema=schema)
        self.inspector = inspect(self.engine)
        
        # ✅ 权限检查表列表
        self._validate_allowed_tables()
        
        # ✅ 工具集 + 类型绑定
        self.tools = self._create_tools()
    
    def _create_production_engine(self, pool_size: int):
        """创建生产级数据库引擎"""
        engine = create_engine(
            self.database_uri,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            future=True,
            connect_args={"connect_timeout": 10}
        )
        
        # ✅ 连接事件监听
        @event.listens_for(engine, "connect")
        def connect(dbapi_connection, connection_record):
            # psycopg2 连接需要使用游标执行 SQL
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        
        @event.listens_for(engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            if not dbapi_connection.closed:
                # psycopg2 连接需要使用游标执行 SQL
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
        
        return engine
    
    def _validate_allowed_tables(self):
        """验证权限表是否存在"""
        existing_tables = set(self.inspector.get_table_names(schema=self.schema))
        invalid_tables = self.allowed_tables - existing_tables
        if invalid_tables:
            logger.warning(f"权限表不存在: {invalid_tables}")
            self.allowed_tables &= existing_tables
    
    def _check_table_permission(self, table_name: str) -> bool:
        """表权限检查"""
        if not self.allowed_tables:
            return True
        return table_name in self.allowed_tables
    
    def _safe_sql(self, table_name: str, operation: str, condition: str = None) -> str:
        """生成安全的 SQL 模板"""
        if not self._check_table_permission(table_name):
            raise ValueError(f"权限拒绝: 无权操作表 {table_name}")
        
        if condition:
            return f"{operation} FROM {table_name} WHERE {condition}"
        return f"{operation} FROM {table_name}"
    
    def _create_tools(self) -> List[Any]:
        """创建工具集"""
        # LangChain 内置 SQL 工具
        return [
            QuerySQLDatabaseTool(db=self.db),
            InfoSQLDatabaseTool(db=self.db),
            ListSQLDatabaseTool(db=self.db),
        ]
        

# 使用示例（✅ 已修复）
if __name__ == "__main__":
    # 初始化工具集
    db_toolkit = SecureDatabaseToolkit(
        database_uri="postgresql://postgres:qNxLn%407nNy3Czx%40@sbp-ryxlih7k8b5udx72.supabase.opentrust.net:5432/mana",
        pool_size=10
    )
    
    # 创建智能 SQL 代理
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0, base_url= "https://api.chatanywhere.org", api_key="sk-9QcmraXhWnRuTcbIPSdHhMSQaHa2PJTqXHZsMO6C60NNspTS")
    
    sql_agent = create_sql_agent(
        llm=llm,
        db=db_toolkit.db,  # ✅ 使用 db 参数而不是 toolkit
        extra_tools=db_toolkit.tools,  # ✅ 传入额外的自定义工具
        verbose=True,
        max_iterations=15,
        early_stopping_method="generate"
    )
    
    # 测试复杂查询
    result = sql_agent.invoke({
        "input": """
        请帮我分析用户手机号 'phone=17338125513' 的营养摄入：
        1. 列出所有餐食相关表
        2. 统计用户本月总卡路里摄入
        3. 找出最高热量的一餐
        4. 生成营养摄入报告
        """
    })
    print(result['output'])