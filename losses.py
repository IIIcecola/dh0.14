
import torch
import torch.nn as nn
import torch.nn.functional as F


class BaseLoss(nn.Module):
  def __init__(self, **kwargs):
    super().__init__()
    self.params = kwargs

  def forward(self, output, target):
    raise NotImplementedError("Subclass must implement forward method")


class RankLoss01Range(BaseLoss):
  """
  Rank Loss（排序损失）
  约束最后一个维度（dim）上的相对高低关系，使模型输出在时间维度上的排序与标签一致
  适用于 0-1 区间的输出，对每个时间步的 136 个特征之间的相对高低关系进行约束
  """
   def __init__(self, **kwargs):
     super().__init__(**kwargs)
     self.gamma_min = kwargs.get('gamma_min', 0.05)
     self.gamma_max = kwargs.get('gamma_max', 0.3)

  def forward(self, scores, y_ture):
    """
    :param scores: 模型输出值, shape = [batch, seq_len, dim]
    :param y_ture: 标签值, shape = [batch, seq_len, dim]
    :return: Rank Loss（constant）
    """
    batch, seq_len, dim = scores.shape
    device = scores.device

    gamma = torch.std(y_ture, dim=-1, keepdim=True)
    gamma = torch.clamp(gamma, self.gamma_min, self.gamma_max)

    # 对每个（batch, seq_len）在dim维度随机采样成对索引
    idx_i = torch.randint(0, dim, (batch, seq_len), device=device)
    idx_j = torch.randint(0, dim, (batch, seq_len), device=device)

    # 根据索引提取对应的值
    batch_idx = torch.arange(batch, device=device).view(-1, 1).expend(-1, seq_len)
    seq_idx = torch.arange(seq_len, device=device).view(-1, 1).expend(batch, -1)

    # 提取对应的值[batch, seq_len]
    s_i = scores[batch_idx, seq_idx, idx_i]
    s_j = scores[batch_idx, seq_idx, idx_j]
    y_i = y_ture[batch_idx, seq_idx, idx_i]
    y_j = y_ture[batch_idx, seq_idx, idx_j]

    y_ij = torch.where(
      y_i >= y_j,
      torch.tensor(1.0, device=device),
      torch.tensor(-1.0, device=device)
    )

    delta = (s_i - s_j) * y_ij
    loss_terms = F.softplus(gamma.squeeze(-1) * delta)

    rank_loss = loss_terms.mean()

    return rank_loss
    


