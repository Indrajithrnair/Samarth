import logging
import json
import time
from datetime import datetime
from typing import Dict, Any
import os

class SamarthLogger:
    """
    Comprehensive logging system for Project Samarth
    Tracks data sources, query processing, and system health
    """
    
    def __init__(self):
        self.setup_logging()
        self.query_log = []
        self.data_source_log = []
        
    def setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('samarth.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Samarth')
        
    def log_query(self, question: str, entities: Dict, data_sources: list, response_time: float, success: bool):
        """Log user query with full traceability"""
        query_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "entities_extracted": entities,
            "data_sources_used": data_sources,
            "response_time_ms": response_time * 1000,
            "success": success,
            "session_id": self._get_session_id()
        }
        
        self.query_log.append(query_entry)
        self.logger.info(f"Query processed: {question[:50]}... | Sources: {len(data_sources)} | Time: {response_time:.2f}s")
        
    def log_data_source_access(self, source_type: str, url: str, success: bool, record_count: int, cache_hit: bool):
        """Log data source access for audit trail"""
        source_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_type": source_type,
            "url": url,
            "success": success,
            "record_count": record_count,
            "cache_hit": cache_hit,
            "response_time": time.time()
        }
        
        self.data_source_log.append(source_entry)
        status = "SUCCESS" if success else "FAILED"
        cache_status = "CACHE" if cache_hit else "API"
        self.logger.info(f"Data access [{status}] {source_type} via {cache_status}: {record_count} records")
        
    def log_error(self, error_type: str, message: str, context: Dict = None):
        """Log errors with context for debugging"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message,
            "context": context or {}
        }
        
        self.logger.error(f"Error [{error_type}]: {message}")
        if context:
            self.logger.error(f"Context: {json.dumps(context, indent=2)}")
            
    def get_system_health(self) -> Dict[str, Any]:
        """Generate system health report"""
        recent_queries = [q for q in self.query_log if 
                         (datetime.now() - datetime.fromisoformat(q["timestamp"])).seconds < 3600]
        
        recent_sources = [s for s in self.data_source_log if 
                         (datetime.now() - datetime.fromisoformat(s["timestamp"])).seconds < 3600]
        
        return {
            "queries_last_hour": len(recent_queries),
            "success_rate": sum(1 for q in recent_queries if q["success"]) / max(len(recent_queries), 1),
            "avg_response_time": sum(q["response_time_ms"] for q in recent_queries) / max(len(recent_queries), 1),
            "data_sources_accessed": len(set(s["source_type"] for s in recent_sources)),
            "cache_hit_rate": sum(1 for s in recent_sources if s["cache_hit"]) / max(len(recent_sources), 1),
            "total_records_processed": sum(s["record_count"] for s in recent_sources)
        }
        
    def _get_session_id(self) -> str:
        """Generate session ID for tracking"""
        return f"session_{int(time.time())}"
        
    def export_audit_log(self, filepath: str):
        """Export complete audit log for compliance"""
        audit_data = {
            "export_timestamp": datetime.now().isoformat(),
            "system_info": {
                "version": "1.0.0",
                "deployment": "development"
            },
            "queries": self.query_log,
            "data_sources": self.data_source_log,
            "health_metrics": self.get_system_health()
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)
            
        self.logger.info(f"Audit log exported to {filepath}")

# Global logger instance
samarth_logger = SamarthLogger()