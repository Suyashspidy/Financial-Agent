"""
BDH (Dragon Hatchling) Architecture Implementation
Based on the research paper: "The Dragon Hatchling: The Missing Link BETWEEN THE TRANSFORMER AND MODELS OF THE BRAIN"

This implementation provides a biologically-inspired neural network architecture that combines
Transformer-like performance with brain-like local graph dynamics and interpretability.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, Dict, Any
import math
from dataclasses import dataclass

@dataclass
class BDHConfig:
    """Configuration for BDH model."""
    vocab_size: int = 256
    d_model: int = 256  # internal dimension
    n_heads: int = 4   # number of attention heads
    n_neurons: int = 32768  # number of neurons
    n_layers: int = 6  # number of layers
    dropout: float = 0.05
    max_seq_len: int = 1024
    activation: str = "relu"
    use_rope: bool = True
    use_hebbian: bool = True  # Enable Hebbian learning
    plasticity_timescale: float = 60.0  # minutes

class RoPE(nn.Module):
    """Rotary Position Embedding implementation."""
    
    def __init__(self, d_model: int, max_seq_len: int = 1024):
        super().__init__()
        self.d_model = d_model
        
        # Precompute rotation matrices
        inv_freq = 1.0 / (10000 ** (torch.arange(0, d_model, 2).float() / d_model))
        t = torch.arange(max_seq_len).float()
        freqs = torch.outer(t, inv_freq)
        self.register_buffer('cos_cached', torch.cos(freqs))
        self.register_buffer('sin_cached', torch.sin(freqs))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(-2)
        cos = self.cos_cached[:seq_len, :]
        sin = self.sin_cached[:seq_len, :]
        
        # Apply rotation
        x_even = x[..., ::2]
        x_odd = x[..., 1::2]
        
        x_rotated = torch.zeros_like(x)
        x_rotated[..., ::2] = x_even * cos - x_odd * sin
        x_rotated[..., 1::2] = x_even * sin + x_odd * cos
        
        return x_rotated

class LinearAttention(nn.Module):
    """Linear attention mechanism for BDH."""
    
    def __init__(self, d_model: int, n_heads: int, use_rope: bool = True):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.use_rope = use_rope
        
        if use_rope:
            self.rope = RoPE(self.head_dim)
        
        # Linear projections
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        
        # Project to Q, K, V
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        
        # Apply RoPE if enabled
        if self.use_rope:
            q = self.rope(q)
            k = self.rope(k)
        
        # Linear attention computation
        # Q @ K^T with causal masking
        scores = torch.matmul(q, k.transpose(-2, -1))
        causal_mask = torch.tril(torch.ones(T, T, device=x.device))
        scores = scores.masked_fill(causal_mask == 0, float('-inf'))
        
        # Apply softmax
        attn_weights = F.softmax(scores, dim=-1)
        
        # Apply attention to values
        out = torch.matmul(attn_weights, v)
        
        # Reshape and project output
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        out = self.out_proj(out)
        
        return out

class HebbianLearning(nn.Module):
    """Hebbian learning mechanism for synaptic plasticity."""
    
    def __init__(self, n_neurons: int, plasticity_timescale: float = 60.0):
        super().__init__()
        self.n_neurons = n_neurons
        self.plasticity_timescale = plasticity_timescale
        
        # Synaptic weights (excitatory and inhibitory)
        self.excitatory_weights = nn.Parameter(torch.randn(n_neurons, n_neurons) * 0.1)
        self.inhibitory_weights = nn.Parameter(torch.randn(n_neurons, n_neurons) * 0.1)
        
        # Learning rates
        self.lr_excitatory = 0.01
        self.lr_inhibitory = 0.01
        
        # Threshold for spike generation
        self.spike_threshold = 1.0
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply Hebbian learning and return updated weights and spikes.
        
        Args:
            x: Input activations [batch_size, n_neurons]
            
        Returns:
            Tuple of (updated_weights, spikes)
        """
        batch_size = x.size(0)
        
        # Generate spikes based on threshold
        spikes = (x > self.spike_threshold).float()
        
        # Hebbian learning rule: Δw = η * pre * post
        if batch_size > 1:
            # Compute correlation matrix
            correlation = torch.matmul(spikes.T, spikes) / batch_size
            
            # Update excitatory weights
            excitatory_update = self.lr_excitatory * correlation
            self.excitatory_weights.data += excitatory_update
            
            # Update inhibitory weights (negative correlation)
            inhibitory_update = -self.lr_inhibitory * correlation
            self.inhibitory_weights.data += inhibitory_update
            
            # Apply weight decay
            self.excitatory_weights.data *= 0.99
            self.inhibitory_weights.data *= 0.99
        
        return self.excitatory_weights, spikes

class BDHBlock(nn.Module):
    """Single BDH block with local graph dynamics."""
    
    def __init__(self, config: BDHConfig):
        super().__init__()
        self.config = config
        
        # Layer normalization
        self.ln1 = nn.LayerNorm(config.d_model, elementwise_affine=False, bias=False)
        self.ln2 = nn.LayerNorm(config.d_model, elementwise_affine=False, bias=False)
        
        # Linear attention
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
        
        # Hebbian learning if enabled
        if config.use_hebbian:
            self.hebbian = HebbianLearning(config.n_neurons, config.plasticity_timescale)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through BDH block.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            
        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
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

class BDHModel(nn.Module):
    """
    BDH (Dragon Hatchling) Model Implementation
    
    A biologically-inspired neural network that combines Transformer-like performance
    with brain-like local graph dynamics and interpretability.
    """
    
    def __init__(self, config: BDHConfig):
        super().__init__()
        self.config = config
        
        # Token embedding
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        
        # BDH blocks
        self.blocks = nn.ModuleList([
            BDHBlock(config) for _ in range(config.n_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Parameter(
            torch.zeros((config.d_model, config.vocab_size)).normal_(std=0.02)
        )
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        """Initialize model weights."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through BDH model.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            
        Returns:
            Logits [batch_size, seq_len, vocab_size]
        """
        B, T = input_ids.shape
        
        # Token embedding
        x = self.token_embedding(input_ids)
        
        # Pass through BDH blocks
        for block in self.blocks:
            x = block(x)
        
        # Output projection
        logits = x @ self.output_projection
        
        return logits
    
    def get_attention_patterns(self, input_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Extract attention patterns for interpretability.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            
        Returns:
            Dictionary containing attention patterns
        """
        B, T = input_ids.shape
        x = self.token_embedding(input_ids)
        
        attention_patterns = {}
        
        for i, block in enumerate(self.blocks):
            # Get attention weights from the block
            x_norm = block.ln1(x)
            attn_out = block.attention(x_norm)
            
            # Store attention pattern
            attention_patterns[f'layer_{i}'] = attn_out
        
        return attention_patterns
    
    def get_neuron_activations(self, input_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Extract neuron activations for interpretability.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            
        Returns:
            Dictionary containing neuron activations
        """
        B, T = input_ids.shape
        x = self.token_embedding(input_ids)
        
        neuron_activations = {}
        
        for i, block in enumerate(self.blocks):
            # Get neuron activations from the block
            x_norm = block.ln1(x)
            x_neurons = F.relu(x_norm @ block.decoder_x.transpose(0, 1).reshape(self.config.d_model, -1))
            
            # Store neuron activations
            neuron_activations[f'layer_{i}'] = x_neurons
        
        return neuron_activations

class BDHProcessor:
    """Processor for BDH model with financial document analysis capabilities."""
    
    def __init__(self, config: BDHConfig):
        self.config = config
        self.model = BDHModel(config)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def analyze_financial_document(self, text: str) -> Dict[str, Any]:
        """
        Analyze financial document using BDH model.
        
        Args:
            text: Financial document text
            
        Returns:
            Analysis results
        """
        # Tokenize text (simplified tokenization)
        tokens = self._tokenize_text(text)
        input_ids = torch.tensor([tokens], device=self.device)
        
        # Get model output
        with torch.no_grad():
            logits = self.model(input_ids)
            attention_patterns = self.model.get_attention_patterns(input_ids)
            neuron_activations = self.model.get_neuron_activations(input_ids)
        
        # Analyze patterns
        analysis = {
            "attention_patterns": self._analyze_attention_patterns(attention_patterns),
            "neuron_activations": self._analyze_neuron_activations(neuron_activations),
            "risk_indicators": self._extract_risk_indicators(text, attention_patterns),
            "confidence_score": self._calculate_confidence_score(logits)
        }
        
        return analysis
    
    def _tokenize_text(self, text: str) -> list:
        """Simple tokenization (in production, use proper tokenizer)."""
        # Convert text to character-level tokens
        return [ord(c) for c in text[:self.config.max_seq_len]]
    
    def _analyze_attention_patterns(self, patterns: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """Analyze attention patterns for interpretability."""
        analysis = {}
        
        for layer_name, pattern in patterns.items():
            # Calculate attention entropy
            entropy = -torch.sum(pattern * torch.log(pattern + 1e-8), dim=-1)
            analysis[layer_name] = {
                "entropy": entropy.mean().item(),
                "max_attention": pattern.max().item(),
                "attention_variance": pattern.var().item()
            }
        
        return analysis
    
    def _analyze_neuron_activations(self, activations: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """Analyze neuron activations for interpretability."""
        analysis = {}
        
        for layer_name, activation in activations.items():
            analysis[layer_name] = {
                "sparsity": (activation == 0).float().mean().item(),
                "mean_activation": activation.mean().item(),
                "max_activation": activation.max().item(),
                "active_neurons": (activation > 0.1).sum().item()
            }
        
        return analysis
    
    def _extract_risk_indicators(self, text: str, patterns: Dict[str, torch.Tensor]) -> list:
        """Extract risk indicators from text and attention patterns."""
        risk_indicators = []
        
        # Text-based risk indicators
        risk_keywords = ["fraud", "suspicious", "unusual", "irregular", "anomaly"]
        for keyword in risk_keywords:
            if keyword.lower() in text.lower():
                risk_indicators.append(f"keyword_{keyword}")
        
        # Attention-based risk indicators
        for layer_name, pattern in patterns.items():
            if pattern.max() > 0.8:  # High attention
                risk_indicators.append(f"high_attention_{layer_name}")
        
        return risk_indicators
    
    def _calculate_confidence_score(self, logits: torch.Tensor) -> float:
        """Calculate confidence score from model output."""
        probs = F.softmax(logits, dim=-1)
        max_probs = probs.max(dim=-1)[0]
        return max_probs.mean().item()

# Example usage and testing
def create_bdh_model(vocab_size: int = 256, d_model: int = 256) -> BDHModel:
    """Create a BDH model with default configuration."""
    config = BDHConfig(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=4,
        n_neurons=32768,
        n_layers=6,
        dropout=0.05
    )
    return BDHModel(config)

def test_bdh_model():
    """Test BDH model functionality."""
    model = create_bdh_model()
    
    # Test input
    input_ids = torch.randint(0, 256, (1, 10))
    
    # Forward pass
    logits = model(input_ids)
    print(f"Output shape: {logits.shape}")
    
    # Get attention patterns
    attention_patterns = model.get_attention_patterns(input_ids)
    print(f"Attention patterns keys: {list(attention_patterns.keys())}")
    
    # Get neuron activations
    neuron_activations = model.get_neuron_activations(input_ids)
    print(f"Neuron activations keys: {list(neuron_activations.keys())}")
    
    print("BDH model test completed successfully!")

if __name__ == "__main__":
    test_bdh_model()
