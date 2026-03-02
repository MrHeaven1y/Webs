import torch
import math
import torch.nn.functional as F
import torch.nn as nn

class PatchEmbedding(nn.Module):
  def __init__(self, patch_size, d_model):
    super().__init__()

    self.conv = nn.Conv2d(in_channels=3, out_channels=d_model, kernel_size=patch_size, stride=patch_size)
    self.flatten = nn.Flatten(start_dim=2)

    self.cls = nn.Parameter(torch.randn(1, 1, d_model))
  def forward(self, x):

    B = x.shape[0]
    patches = self.conv(x)
    patches = self.flatten(patches)

    patches = patches.transpose(1,2)

    cls_tokens = self.cls.expand(B, -1, -1)
    patches = torch.concat((cls_tokens, patches), dim=1)

    return patches
  

class PositionalEncoding(nn.Module):
  def __init__(self, num_patches, d_model):
    super().__init__()

    pe = torch.zeros((num_patches+1, d_model))

    position = torch.arange(0,num_patches+1, dtype=torch.float).unsqueeze(1)

    div_term = torch.exp(
        -torch.arange(0, d_model, 2) * math.log(10000.0) / d_model
    )

    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)

    pe = pe.unsqueeze(0)

    self.register_buffer('pe', pe)

  def forward(self, x):
    T = x.shape[1]

    return x + self.pe[:, :T]

class MHA(nn.Module):
  # 1. Add dropout here
  def __init__(self, d_model, n_heads, dropout): 
    super().__init__()
    self.d_model = d_model
    self.n_heads = n_heads
    self.d_k = d_model // n_heads

    self.WQ = nn.Linear(d_model, d_model, bias=False)
    self.WK = nn.Linear(d_model, d_model, bias=False)
    self.WV = nn.Linear(d_model, d_model, bias=False)

    self.proj = nn.Linear(d_model, d_model, bias=False)
    self.dropout = nn.Dropout(dropout) # Now it knows what 'dropout' is

  def forward(self, x):
    B, T, _ = x.shape

    Q = self.WQ(x).view(B,T, self.n_heads, self.d_k).transpose(1,2)
    K = self.WK(x).view(B,T, self.n_heads, self.d_k).transpose(1,2)
    V = self.WV(x).view(B,T, self.n_heads, self.d_k).transpose(1,2)

    score = torch.matmul(Q, K.transpose(-2, -1)) * (self.d_k ** -0.5)
    attn = F.softmax(score, dim=-1)
    attn = self.dropout(attn)

    out = torch.matmul(attn, V)
    out = out.transpose(1, 2).contiguous().view(B, T, self.d_model)

    return self.proj(out)
  
  

class Encoder(nn.Module):
  # 2. Add dropout here
  def __init__(self, d_model, n_heads, dropout):
    super().__init__()

    # 3. Pass dropout down to MHA
    self.mha = MHA(d_model, n_heads, dropout) 
    
    self.ln1 = nn.LayerNorm(d_model)
    self.ln2 = nn.LayerNorm(d_model)
    self.mlp = nn.Sequential(*[
        nn.Linear(d_model, d_model*4),
        nn.GELU(),
        nn.Linear(d_model*4, d_model),
        nn.Dropout(dropout), # Now it knows what 'dropout' is
    ])

  def forward(self, x):

    x = x + self.mha(self.ln1(x))
    x = x + self.mlp(self.ln2(x))

    return x
  


class ViT(nn.Module):
  def __init__(self, d_model, n_heads, num_classes, size=64, patch=16, n_layers=12, dropout=0.3):
    super().__init__()
    num_patches = (size // patch) ** 2
    
    self.patched_embd = PatchEmbedding(patch, d_model)
    self.pos_encd = PositionalEncoding(num_patches, d_model)

    self.encoders = nn.ModuleList([
        Encoder(d_model, n_heads, dropout) for _ in range(n_layers)
    ])

    self.ln = nn.LayerNorm(d_model)
    self.head = nn.Linear(d_model, num_classes)

  def forward(self, x):

    x = self.patched_embd(x)
    x = self.pos_encd(x)

    for encoder in self.encoders:
      x = encoder(x)

    cls_token = x[:, 0, :]

    out = self.ln(cls_token)
    out = self.head(out)

    return out