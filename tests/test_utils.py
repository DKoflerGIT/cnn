"""Test utils module"""

import numpy as np
import cupy as cp
import torch

import walnut
from walnut.tensor import Tensor, ShapeLike, ArrayLike


def get_vals(
    shape: ShapeLike, torch_grad: bool = True, device: str = "cpu"
) -> tuple[Tensor, torch.Tensor]:
    """Returns a walnut tensor and a torch tensor initialized equally."""
    walnut_x = walnut.randn(shape)
    torch_x = torch.from_numpy(walnut_x.data)
    if torch_grad:
        torch_x.requires_grad = True
    walnut_x.to_device(device)
    return walnut_x, torch_x


def validate(
    x1: Tensor | ArrayLike, x2: torch.Tensor | None, tol: float = 1e-5
) -> bool:
    if isinstance(x1, Tensor):
        x1 = x1.data
    if isinstance(x1, cp.ndarray):
        x1 = walnut.cuda.cupy_to_numpy(x1)
    return np.allclose(x1, x2.detach().numpy(), tol, tol)
