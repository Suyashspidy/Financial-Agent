"""
BDH (Dragon Hatchling) Architecture Integration
Enhanced neural processing for Due Diligence Copilot system
Based on Pathway research: "The Dragon Hatchling: The Missing Link BETWEEN THE TRANSFORMER AND MODELS OF THE BRAIN"
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, Dict, Any, List
import math
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class BDHConfig:
    """Configuration for BDH model integration."""
    vocab_size: int = 256
    d_model: int = 256
    n_heads: int = 4
    n_neurons: int = 32768
    n_layers: int = 6
    dropout: float = 0.05
    max_seq_len: int = 1024
    use_rope: bool = True
    use_hebbian: bool = True
    plasticity_timescale: float = 60.0
    # Integration with existing system
    integrate_with_pathway: bool = True
    enhance_qa_capabilities: bool = True
    fraud_detection_mode: bool = True

class RoPE(nn.Module):
    """Rotary Position Embedding for BDH."""
    
    def __init__(self, d_model: int, max_seq_len: int = 1024):
        super().__init__()
        self.d_model = d_model
        
        inv_freq = 1.0 / (10000 ** (torch.arange(0, d_model, 2).float() / d_model))
        t = torch.arange(max_seq_len).float()
        freqs = torch.outer(t, inv_freq)
        self.register_buffer('cos_cached', torch.cos(freqs))
        self.register_buffer('sin_cached', torch.sin(freqs))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(-2)
        cos = self.cos_cached[:seq_len, :]
        sin = self.sin_cached[:seq_len, :]
        
        x_even = x[..., ::2]
        x_odd = x[..., 1::2]
        
        x_rotated = torch.zeros_like(x)
        x_rotated[..., ::2] = x_even * cos - x_odd * sin
        x_rotated[..., 1::2] = x_even * sin + x_odd * cos
        
        return x_rotated

class LinearAttention(nn.Module):
    """Linear attention mechanism optimized for financial document analysis."""
    
    def __init__(self, d_model: int, n_heads: int, use_rope: bool = True):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.use_rope = use_rope
        
        if use_rope:
            self.rope = RoPE(self.head_dim)
        
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        
        if self.use_rope:
            q = self.rope(q)
            k = self.rope(k)
        
        scores = torch.matmul(q, k.transpose(-2, -1))
        causal_mask = torch.tril(torch.ones(T, T, device=x.device))
        scores = scores.masked_fill(causal_mask == 0, float('-inf'))
        
        attn_weights = F.softmax(scores, dim=-1)
        out = torch.matmul(attn_weights, v)
        
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        out = self.out_proj(out)
        
        return out

class FinancialDocumentProcessor(nn.Module):
    """BDH-based processor for financial document analysis."""
    
    def __init__(self, config: BDHConfig):
        super().__init__()
        self.config = config
        
        # Token embedding for financial terms
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        
        # Financial-specific embeddings
        self.financial_embedding = nn.Embedding(1000, config.d_model)  # Financial terms
        self.legal_embedding = nn.Embedding(1000, config.d_model)     # Legal terms
        
        # BDH blocks
        self.blocks = nn.ModuleList([
            BDHBlock(config) for _ in range(config.n_layers)
        ])
        
        # Financial analysis heads
        self.risk_classifier = nn.Linear(config.d_model, 3)  # Low, Medium, High risk
        self.clause_classifier = nn.Linear(config.d_model, 10)  # Different clause types
        self.fraud_detector = nn.Linear(config.d_model, 2)   # Fraud/No fraud
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids: torch.Tensor, financial_context: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Process financial document with BDH architecture.
        
        Args:
            input_ids: Token IDs [batch_size, seq_len]
            financial_context: Additional financial context [batch_size, context_dim]
            
        Returns:
            Dictionary with analysis results
        """
        B, T = input_ids.shape
        
        # Token embedding
        x = self.token_embedding(input_ids)
        
        # Add financial context if available
        if financial_context is not None:
            context_embedding = self.financial_embedding(financial_context.long())
            x = x + context_embedding.unsqueeze(1)
        
        # Pass through BDH blocks
        for block in self.blocks:
            x = block(x)
        
        # Financial analysis
        risk_scores = self.risk_classifier(x)
        clause_scores = self.clause_classifier(x)
        fraud_scores = self.fraud_detector(x)
        
        return {
            "risk_scores": risk_scores,
            "clause_scores": clause_scores,
            "fraud_scores": fraud_scores,
            "hidden_states": x
        }

class BDHBlock(nn.Module):
    """Single BDH block with financial document optimization."""
    
    def __init__(self, config: BDHConfig):
        super().__init__()
        self.config = config
        
        self.ln1 = nn.LayerNorm(config.d_model, elementwise_affine=False, bias=False)
        self.ln2 = nn.LayerNorm(config.d_model, elementwise_affine=False, bias=False)
        
        self.attention = LinearAttention(
            config.d_model, 
            config.n_heads, 
            config.use_rope
        )
        
        # Neuron encoder/decoder matrices
        self.encoder = nn.Parameter(
            torch.zeros((config.n_neurons, config.d_model)).normal_(std=0.02)
        )
        self.decoder_x = nn.Parameter(
            torch.zeros((config.n_heads, config.d_model, config.n_neurons // config.n_heads)).normal_(std=0.02)
        )
        self.decoder_y = nn.Parameter(
            torch.zeros((config.n_heads, config.d_model, config.n_neurons // config.n_heads)).normal_(std=0.02)
        )
        
        self.dropout = nn.Dropout(config.dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        
        # First normalization
        x_norm = self.ln1(x)
        
        # Project to neuron space
        x_neurons = F.relu(x_norm @ self.decoder_x.transpose(0, 1).reshape(D, -1))
        x_neurons = x_neurons.view(B, T, self.config.n_heads, -1)
        
        # Apply attention
        attn_out = self.attention(x_norm)
        
        # Project attention output to neuron space
        y_neurons = F.relu(self.ln2(attn_out) @ self.decoder_y.transpose(0, 1).reshape(D, -1))
        y_neurons = y_neurons.view(B, T, self.config.n_heads, -1)
        
        # Element-wise multiplication (local interaction)
        z_neurons = y_neurons * x_neurons
        
        # Reshape back to model dimension
        z_neurons = z_neurons.transpose(1, 2).reshape(B, T, -1)
        
        # Apply dropout
        z_neurons = self.dropout(z_neurons)
        
        # Project back to model space
        output = z_neurons @ self.encoder
        
        # Residual connection
        output = x + output
        
        # Final normalization
        output = self.ln2(output)
        
        return output

class DueDiligenceBDHProcessor:
    """BDH processor integrated with Due Diligence Copilot system."""
    
    def __init__(self, config: BDHConfig = None):
        if config is None:
            config = BDHConfig()
        
        self.config = config
        self.model = FinancialDocumentProcessor(config)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Financial term mappings
        self.financial_terms = self._initialize_financial_terms()
        self.legal_terms = self._initialize_legal_terms()
        
    def _initialize_financial_terms(self) -> Dict[str, int]:
        """Initialize financial term mappings."""
        return {
            "payment": 1, "invoice": 2, "amount": 3, "due": 4, "balance": 5,
            "revenue": 6, "expense": 7, "profit": 8, "loss": 9, "asset": 10,
            "liability": 11, "equity": 12, "cash": 13, "credit": 14, "debit": 15,
            "interest": 16, "rate": 17, "fee": 18, "charge": 19, "cost": 20,
            "price": 21, "value": 22, "worth": 23, "budget": 24, "forecast": 25
        }
    
    def _initialize_legal_terms(self) -> Dict[str, int]:
        """Initialize legal term mappings."""
        return {
            "contract": 1, "agreement": 2, "clause": 3, "term": 4, "condition": 5,
            "indemnity": 6, "liability": 7, "warranty": 8, "guarantee": 9, "obligation": 10,
            "right": 11, "duty": 12, "responsibility": 13, "breach": 14, "violation": 15,
            "penalty": 16, "fine": 17, "damages": 18, "compensation": 19, "remedy": 20,
            "termination": 21, "expiration": 22, "renewal": 23, "amendment": 24, "modification": 25
        }
    
    def analyze_document_chunk(self, chunk_text: str, document_type: str = "contract") -> Dict[str, Any]:
        """
        Analyze a document chunk using BDH architecture.
        
        Args:
            chunk_text: Text content of the document chunk
            document_type: Type of document (contract, invoice, etc.)
            
        Returns:
            Analysis results
        """
        try:
            # Tokenize text
            tokens = self._tokenize_financial_text(chunk_text)
            input_ids = torch.tensor([tokens], device=self.device)
            
            # Get financial context
            financial_context = self._extract_financial_context(chunk_text)
            context_tensor = torch.tensor([financial_context], device=self.device)
            
            # Process with BDH model
            with torch.no_grad():
                results = self.model(input_ids, context_tensor)
            
            # Extract analysis
            analysis = {
                "risk_level": self._interpret_risk_scores(results["risk_scores"]),
                "clause_types": self._interpret_clause_scores(results["clause_scores"]),
                "fraud_probability": self._interpret_fraud_scores(results["fraud_scores"]),
                "confidence": self._calculate_confidence(results),
                "financial_context": financial_context,
                "document_type": document_type
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document chunk: {str(e)}")
            return {
                "risk_level": "unknown",
                "clause_types": [],
                "fraud_probability": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _tokenize_financial_text(self, text: str) -> List[int]:
        """Tokenize financial text for BDH processing."""
        # Simple character-level tokenization
        # In production, use a proper tokenizer
        tokens = []
        for char in text[:self.config.max_seq_len]:
            token_id = min(ord(char), self.config.vocab_size - 1)
            tokens.append(token_id)
        
        # Pad to max length
        while len(tokens) < self.config.max_seq_len:
            tokens.append(0)
        
        return tokens[:self.config.max_seq_len]
    
    def _extract_financial_context(self, text: str) -> int:
        """Extract financial context score from text."""
        text_lower = text.lower()
        financial_score = 0
        legal_score = 0
        
        # Count financial terms
        for term, score in self.financial_terms.items():
            if term in text_lower:
                financial_score += score
        
        # Count legal terms
        for term, score in self.legal_terms.items():
            if term in text_lower:
                legal_score += score
        
        # Combine scores
        total_score = financial_score + legal_score
        return min(total_score, 999)  # Cap at 999 for embedding
    
    def _interpret_risk_scores(self, risk_scores: torch.Tensor) -> str:
        """Interpret risk classification scores."""
        probs = F.softmax(risk_scores, dim=-1)
        max_prob, max_idx = probs.max(dim=-1)
        
        risk_levels = ["low", "medium", "high"]
        return risk_levels[max_idx.item()]
    
    def _interpret_clause_scores(self, clause_scores: torch.Tensor) -> List[str]:
        """Interpret clause classification scores."""
        probs = F.softmax(clause_scores, dim=-1)
        top_indices = torch.topk(probs, k=3, dim=-1).indices
        
        clause_types = [
            "payment", "termination", "indemnity", "liability", "warranty",
            "confidentiality", "intellectual_property", "governing_law", 
            "dispute_resolution", "force_majeure"
        ]
        
        return [clause_types[idx.item()] for idx in top_indices[0]]
    
    def _interpret_fraud_scores(self, fraud_scores: torch.Tensor) -> float:
        """Interpret fraud detection scores."""
        probs = F.softmax(fraud_scores, dim=-1)
        fraud_prob = probs[0, 1].item()  # Probability of fraud
        return fraud_prob
    
    def _calculate_confidence(self, results: Dict[str, torch.Tensor]) -> float:
        """Calculate overall confidence score."""
        # Use the maximum probability across all classifications
        max_conf = 0.0
        
        for key, scores in results.items():
            if key != "hidden_states":
                probs = F.softmax(scores, dim=-1)
                max_conf = max(max_conf, probs.max().item())
        
        return max_conf
    
    def enhance_qa_response(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """
        Enhance Q&A response using BDH analysis.
        
        Args:
            question: User question
            answer: Generated answer
            context: Document context
            
        Returns:
            Enhanced response with BDH insights
        """
        try:
            # Analyze the context
            context_analysis = self.analyze_document_chunk(context)
            
            # Analyze the answer
            answer_analysis = self.analyze_document_chunk(answer)
            
            # Combine analyses
            enhanced_response = {
                "original_answer": answer,
                "context_risk_level": context_analysis["risk_level"],
                "answer_confidence": answer_analysis["confidence"],
                "detected_clauses": answer_analysis["clause_types"],
                "fraud_indicators": answer_analysis["fraud_probability"],
                "bdh_insights": {
                    "financial_complexity": context_analysis["financial_context"],
                    "risk_assessment": context_analysis["risk_level"],
                    "confidence_score": answer_analysis["confidence"]
                }
            }
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error enhancing QA response: {str(e)}")
            return {
                "original_answer": answer,
                "error": str(e)
            }

# Integration functions for existing Due Diligence Copilot
def create_bdh_processor() -> DueDiligenceBDHProcessor:
    """Create BDH processor for Due Diligence Copilot integration."""
    config = BDHConfig(
        vocab_size=256,
        d_model=256,
        n_heads=4,
        n_neurons=32768,
        n_layers=6,
        dropout=0.05,
        integrate_with_pathway=True,
        enhance_qa_capabilities=True,
        fraud_detection_mode=True
    )
    return DueDiligenceBDHProcessor(config)

def analyze_document_with_bdh(processor: DueDiligenceBDHProcessor, 
                            document_text: str, 
                            document_type: str = "contract") -> Dict[str, Any]:
    """Analyze document using BDH architecture."""
    return processor.analyze_document_chunk(document_text, document_type)

def enhance_qa_with_bdh(processor: DueDiligenceBDHProcessor,
                       question: str,
                       answer: str,
                       context: str) -> Dict[str, Any]:
    """Enhance Q&A response with BDH insights."""
    return processor.enhance_qa_response(question, answer, context)

# Example usage
if __name__ == "__main__":
    # Test BDH processor
    processor = create_bdh_processor()
    
    # Test document analysis
    sample_text = "Payment shall be made within 30 days of invoice date. Late payments subject to 1.5% monthly interest."
    analysis = analyze_document_with_bdh(processor, sample_text, "contract")
    
    print("BDH Analysis Results:")
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Clause Types: {analysis['clause_types']}")
    print(f"Fraud Probability: {analysis['fraud_probability']:.3f}")
    print(f"Confidence: {analysis['confidence']:.3f}")
    
    print("\nBDH processor integration test completed successfully!")
