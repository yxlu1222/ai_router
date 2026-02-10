import sqlite3
import json
import time
import pathlib
from typing import List, Dict, Optional

# 动态获取数据库路径 (位于项目根目录)
src_dir = pathlib.Path(__file__).parent.resolve()
DB_PATH = src_dir.parent / "benchmark.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 创建测试结果表
    c.execute('''
        CREATE TABLE IF NOT EXISTS benchmark_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT,
            timestamp REAL,
            latency_ttft REAL,
            latency_total REAL,
            throughput REAL,
            status TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_result(result: Dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO benchmark_runs 
        (model_id, timestamp, latency_ttft, latency_total, throughput, status, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        result.get("model_id"),
        time.time(),
        result.get("latency_ttft", 0),
        result.get("latency_total", 0),
        result.get("throughput", 0),
        result.get("status"),
        result.get("error", "")
    ))
    conn.commit()
    conn.close()

def get_aggregated_stats():
    """获取每个模型的平均性能数据"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # 获取最近 50 次成功的测试取平均值
    query = '''
        SELECT 
            model_id,
            AVG(latency_ttft) as avg_ttft,
            AVG(throughput) as avg_throughput,
            COUNT(*) as success_count
        FROM benchmark_runs
        WHERE status = 'success'
        GROUP BY model_id
    '''
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    
    stats = {}
    for row in rows:
        stats[row["model_id"]] = dict(row)
    return stats
