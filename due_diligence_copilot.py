"""
Main Due Diligence Copilot Application
Interactive CLI for document analysis and Q&A
"""
import sys
from pathlib import Path
from typing import Optional
import json

from config import Config
from document_ingestion import DocumentIngestionPipeline
from qa_workflow import DueDiligenceQA
from audit_logger import AuditLogger


class DueDiligenceCopilot:
    """Main application class for Due Diligence Copilot"""
    
    def __init__(self):
        """Initialize the copilot application"""
        print("Initializing Due Diligence Copilot...")
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            print(f"\n❌ Configuration Error:\n{str(e)}")
            sys.exit(1)
        
        # Initialize components
        self.pipeline = DocumentIngestionPipeline()
        self.qa_system = DueDiligenceQA(self.pipeline)
        self.audit_logger = AuditLogger()
        
        print(f"✓ Configuration validated")
        print(f"✓ Documents folder: {Config.DOCS_FOLDER}")
        print(f"✓ Logs folder: {Config.AUDIT_LOG_FOLDER}")
        print(f"✓ Index folder: {Config.INDEX_FOLDER}")
    
    def index_documents(self, refresh: bool = False):
        """
        Index or refresh document index
        
        Args:
            refresh: Whether to force refresh of the index
        """
        print("\n" + "="*60)
        print("INDEXING DOCUMENTS")
        print("="*60)
        
        if refresh:
            records_count = self.qa_system.refresh_index()
        else:
            records_count = self.qa_system.load_index()
        
        if records_count == 0:
            print("\n⚠️  No documents found or indexed.")
            print(f"   Add PDF or DOCX files to: {Config.DOCS_FOLDER}")
        else:
            print(f"\n✓ Successfully indexed {records_count} chunks")
            
            # Get overview
            overview = self.qa_system.get_document_overview()
            print(f"✓ Total documents: {overview['total_documents']}")
            
            if overview['documents']:
                print("\nIndexed Documents:")
                for doc in overview['documents']:
                    print(f"  - {doc['doc_name']} ({doc['chunk_count']} chunks)")
    
    def ask_question(self, question: str, doc_filter: Optional[str] = None):
        """
        Ask a question and get an answer with citations
        
        Args:
            question: The question to ask
            doc_filter: Optional document name to filter
        """
        print("\n" + "="*60)
        print("Q&A SESSION")
        print("="*60)
        print(f"Question: {question}")
        if doc_filter:
            print(f"Document Filter: {doc_filter}")
        print("-"*60)
        
        # Get answer
        response = self.qa_system.ask_with_evidence(question)
        
        # Display answer
        print(f"\nAnswer:\n{response['answer']}")
        
        # Display citations
        if response.get('citations'):
            print(f"\n📚 Citations ({len(response['citations'])}):")
            for i, cite in enumerate(response['citations'], 1):
                doc_name = cite.get('doc_name', 'Unknown')
                page = cite.get('page', 'N/A')
                print(f"\n  [{i}] {doc_name} - Page {page}")
                if cite.get('text'):
                    print(f"      \"{cite['text'][:150]}...\"")
        
        if response.get('evidence_summary'):
            print(f"\n📎 Evidence Summary:")
            for evidence in response['evidence_summary']:
                print(f"  - {evidence}")
        
        # Log the query
        self.audit_logger.log_query(
            query=question,
            response=response,
            query_type="general"
        )
        
        print("\n✓ Query logged for audit")
    
    def find_clauses(self, clause_type: str, date_filter: Optional[str] = None):
        """
        Find contracts with specific clause types
        
        Args:
            clause_type: Type of clause (e.g., "indemnity", "termination")
            date_filter: Optional date filter
        """
        print("\n" + "="*60)
        print(f"SEARCHING FOR {clause_type.upper()} CLAUSES")
        print("="*60)
        
        results = self.qa_system.find_contracts_with_clause(clause_type, date_filter)
        
        if not results:
            print(f"\n⚠️  No contracts found with {clause_type} clauses")
            return
        
        print(f"\n✓ Found {len(results)} document(s) with {clause_type} clauses:\n")
        
        for doc_result in results:
            print(f"📄 {doc_result['doc_name']}")
            print(f"   Uploaded: {doc_result['upload_timestamp'][:10]}")
            print(f"   Matches: {len(doc_result['matches'])}")
            
            for match in doc_result['matches'][:3]:  # Show top 3 matches
                print(f"   - Page {match['page']}: {match['text'][:100]}...")
            
            if len(doc_result['matches']) > 3:
                print(f"   ... and {len(doc_result['matches']) - 3} more matches")
            print()
        
        # Log the search
        response = {"results": results, "clause_type": clause_type}
        self.audit_logger.log_query(
            query=f"Find {clause_type} clauses" + (f" from {date_filter}" if date_filter else ""),
            response=response,
            query_type="clause_search"
        )
    
    def scan_risks(self, doc_filter: Optional[str] = None, risk_keywords: Optional[list] = None):
        """
        Scan documents for potential risks
        
        Args:
            doc_filter: Optional document name filter
            risk_keywords: Optional custom risk keywords
        """
        print("\n" + "="*60)
        print("RISK SCANNING")
        print("="*60)
        
        if risk_keywords:
            print(f"Using custom keywords: {', '.join(risk_keywords)}")
        
        results = self.qa_system.flag_risks_in_documents(doc_filter, risk_keywords)
        
        print(f"\n✓ Scanned {results['total_documents_scanned']} document(s)")
        print(f"✓ Found risks in {results['documents_with_risks']} document(s)")
        
        if results['flagged_risks']:
            print("\n🚨 FLAGGED RISKS:\n")
            
            for doc_name, risks in results['flagged_risks'].items():
                print(f"📄 {doc_name}")
                print(f"   {len(risks)} risk(s) identified:\n")
                
                for risk in risks:
                    print(f"   🔴 {risk['risk_type'].upper()}")
                    print(f"      {risk['answer'][:200]}...")
                    if risk['citations']:
                        cite = risk['citations'][0]
                        page = cite.get('page', 'N/A')
                        print(f"      📍 Page {page}")
                    print()
        else:
            print("\n✓ No significant risks flagged")
        
        # Log the risk scan
        self.audit_logger.log_risk_scan(results)
        print("✓ Risk scan logged for audit")
    
    def show_statistics(self):
        """Display usage statistics"""
        print("\n" + "="*60)
        print("SYSTEM STATISTICS")
        print("="*60)
        
        # Document overview
        overview = self.qa_system.get_document_overview()
        print(f"\n📊 Documents:")
        print(f"   Total: {overview['total_documents']}")
        print(f"   Total Chunks: {overview['total_chunks']}")
        
        # Query statistics
        stats = self.audit_logger.get_query_statistics()
        print(f"\n📊 Query Statistics:")
        print(f"   Total Queries: {stats['total_queries']}")
        
        if stats['query_types']:
            print(f"\n   Query Types:")
            for qtype, count in stats['query_types'].items():
                print(f"      - {qtype}: {count}")
        
        if stats['documents_accessed']:
            print(f"\n   Most Accessed Documents:")
            sorted_docs = sorted(stats['documents_accessed'].items(), key=lambda x: x[1], reverse=True)
            for doc, count in sorted_docs[:5]:
                print(f"      - {doc}: {count} times")
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        print("\n" + "="*60)
        print("INTERACTIVE MODE")
        print("="*60)
        print("\nCommands:")
        print("  ask <question>          - Ask a question")
        print("  clause <type>           - Find clauses (e.g., 'clause indemnity')")
        print("  risk                    - Scan for risks")
        print("  refresh                 - Refresh document index")
        print("  stats                   - Show statistics")
        print("  help                    - Show this help")
        print("  quit                    - Exit")
        print("\n" + "="*60)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                elif user_input.lower() == 'help':
                    self.interactive_mode.__doc__
                    print("\nCommands listed above ☝️")
                
                elif user_input.lower() == 'refresh':
                    self.index_documents(refresh=True)
                
                elif user_input.lower() == 'stats':
                    self.show_statistics()
                
                elif user_input.lower() == 'risk':
                    self.scan_risks()
                
                elif user_input.lower().startswith('clause '):
                    clause_type = user_input[7:].strip()
                    self.find_clauses(clause_type)
                
                elif user_input.lower().startswith('ask '):
                    question = user_input[4:].strip()
                    self.ask_question(question)
                
                else:
                    # Assume it's a question
                    self.ask_question(user_input)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Type 'help' for available commands.")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("      Due Diligence Copilot - Financial Document Analysis")
    print("="*60)
    
    # Initialize the copilot
    copilot = DueDiligenceCopilot()
    
    # Index documents
    copilot.index_documents()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'ask' and len(sys.argv) > 2:
            question = ' '.join(sys.argv[2:])
            copilot.ask_question(question)
        
        elif command == 'clause' and len(sys.argv) > 2:
            clause_type = sys.argv[2]
            date_filter = sys.argv[3] if len(sys.argv) > 3 else None
            copilot.find_clauses(clause_type, date_filter)
        
        elif command == 'risk':
            copilot.scan_risks()
        
        elif command == 'stats':
            copilot.show_statistics()
        
        elif command == 'interactive':
            copilot.interactive_mode()
        
        else:
            print(f"\n❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python due_diligence_copilot.py interactive")
            print("  python due_diligence_copilot.py ask <question>")
            print("  python due_diligence_copilot.py clause <type> [date]")
            print("  python due_diligence_copilot.py risk")
            print("  python due_diligence_copilot.py stats")
    else:
        # Default to interactive mode
        copilot.interactive_mode()


if __name__ == "__main__":
    main()
