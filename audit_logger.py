"""
Audit logging module for Due Diligence Copilot
Logs all queries, responses, and evidence references
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import csv

from config import Config


class AuditLogger:
    """Handles audit logging for all Q&A operations"""
    
    def __init__(self):
        """Initialize the audit logger"""
        self.log_folder = Config.AUDIT_LOG_FOLDER
        self.log_folder.mkdir(parents=True, exist_ok=True)
        
        # Create separate log files
        self.query_log_file = self.log_folder / "query_log.jsonl"
        self.risk_log_file = self.log_folder / "risk_log.jsonl"
        self.audit_csv_file = self.log_folder / "audit_summary.csv"
        
        # Initialize CSV if it doesn't exist
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize the CSV audit log with headers"""
        if not self.audit_csv_file.exists():
            with open(self.audit_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp',
                    'Query Type',
                    'Query Text',
                    'Documents Accessed',
                    'Citations Count',
                    'User'
                ])
    
    def log_query(
        self,
        query: str,
        response: Dict[str, Any],
        query_type: str = "general",
        user: str = "default_user"
    ) -> str:
        """
        Log a Q&A query and response
        
        Args:
            query: The user's query
            response: The system's response dictionary
            query_type: Type of query (general, risk_scan, clause_search, etc.)
            user: User identifier
            
        Returns:
            Log entry ID
        """
        timestamp = datetime.now().isoformat()
        
        # Extract documents accessed from citations
        docs_accessed = set()
        citations_count = 0
        
        if 'citations' in response:
            citations_count = len(response['citations'])
            for cite in response['citations']:
                if 'doc_name' in cite:
                    docs_accessed.add(cite['doc_name'])
        
        # Create log entry
        log_entry = {
            "log_id": f"{timestamp}_{user}",
            "timestamp": timestamp,
            "user": user,
            "query_type": query_type,
            "query": query,
            "response": response,
            "documents_accessed": list(docs_accessed),
            "citations_count": citations_count
        }
        
        # Write to JSONL file
        with open(self.query_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Write to CSV summary
        with open(self.audit_csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                query_type,
                query[:100],  # Truncate long queries
                '; '.join(docs_accessed),
                citations_count,
                user
            ])
        
        return log_entry["log_id"]
    
    def log_risk_scan(
        self,
        risk_results: Dict[str, Any],
        user: str = "default_user"
    ) -> str:
        """
        Log a risk scanning operation
        
        Args:
            risk_results: Results from risk scanning
            user: User identifier
            
        Returns:
            Log entry ID
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "log_id": f"risk_{timestamp}_{user}",
            "timestamp": timestamp,
            "user": user,
            "operation": "risk_scan",
            "results": risk_results
        }
        
        # Write to risk log file
        with open(self.risk_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_entry["log_id"]
    
    def log_document_processing(
        self,
        doc_name: str,
        chunks_extracted: int,
        status: str = "success",
        error_msg: Optional[str] = None
    ):
        """
        Log document processing events
        
        Args:
            doc_name: Name of the document
            chunks_extracted: Number of chunks extracted
            status: Processing status
            error_msg: Optional error message
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "operation": "document_processing",
            "doc_name": doc_name,
            "chunks_extracted": chunks_extracted,
            "status": status,
            "error": error_msg
        }
        
        # Append to query log
        with open(self.query_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_recent_queries(self, limit: int = 10) -> list:
        """
        Get recent queries from the log
        
        Args:
            limit: Number of recent queries to retrieve
            
        Returns:
            List of recent query log entries
        """
        if not self.query_log_file.exists():
            return []
        
        queries = []
        with open(self.query_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("query_type"):  # Only Q&A queries
                        queries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        # Return most recent queries
        return queries[-limit:] if len(queries) > limit else queries
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged queries
        
        Returns:
            Dictionary with query statistics
        """
        if not self.query_log_file.exists():
            return {"total_queries": 0}
        
        stats = {
            "total_queries": 0,
            "query_types": {},
            "documents_accessed": {},
            "users": {}
        }
        
        with open(self.query_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    if not entry.get("query_type"):
                        continue
                    
                    stats["total_queries"] += 1
                    
                    # Count query types
                    qtype = entry.get("query_type", "unknown")
                    stats["query_types"][qtype] = stats["query_types"].get(qtype, 0) + 1
                    
                    # Count documents accessed
                    for doc in entry.get("documents_accessed", []):
                        stats["documents_accessed"][doc] = stats["documents_accessed"].get(doc, 0) + 1
                    
                    # Count users
                    user = entry.get("user", "unknown")
                    stats["users"][user] = stats["users"].get(user, 0) + 1
                    
                except json.JSONDecodeError:
                    continue
        
        return stats
    
    def export_audit_trail(
        self,
        output_file: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Export audit trail to a file
        
        Args:
            output_file: Optional output file path
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            
        Returns:
            Path to the exported file
        """
        if output_file is None:
            output_file = str(self.log_folder / f"audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        audit_data = {
            "export_timestamp": datetime.now().isoformat(),
            "filters": {
                "start_date": start_date,
                "end_date": end_date
            },
            "entries": []
        }
        
        if not self.query_log_file.exists():
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2)
            return output_file
        
        with open(self.query_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply date filters
                    if start_date and entry.get("timestamp", "") < start_date:
                        continue
                    if end_date and entry.get("timestamp", "") > end_date:
                        continue
                    
                    audit_data["entries"].append(entry)
                    
                except json.JSONDecodeError:
                    continue
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
        
        return output_file
    
    def clear_old_logs(self, days_to_keep: int = 90):
        """
        Clear logs older than specified days
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        # This is a simplified version - in production, you'd want to
        # read, filter, and rewrite the log files
        print(f"Note: Log cleanup would remove entries before {cutoff_date}")
        print("For production, implement file rotation or database-backed logging")
