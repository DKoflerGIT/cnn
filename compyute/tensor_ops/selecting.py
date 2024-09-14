"""Tensor selection and filter operations."""

from typing import Optional

from ..tensors import AxisLike, ShapeError, Tensor, to_arraylike
from ..typing import ScalarLike

__all__ = [
    "argmax",
    "get_diagonal",
    "max",
    "maximum",
    "min",
    "minimum",
    "topk",
    "tril",
    "triu",
    "unique",
]


def argmax(
    x: Tensor, axis: Optional[AxisLike] = None, *, keepdims: bool = False
) -> Tensor:
    """Returns the indices of maximum values along a given axis.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    axis : AxisLike, optional
        Axes, along which the maximum value is located. Defaults to ``None``.
        If ``None`` it is computed over the flattened tensor.
    keepdims : bool, optional
        Whether to keep the tensors dimensions. Defaults to ``False``.
        If false the tensor is collapsed along the given axis.

    Returns
    -------
    Tensor
        Tensor containing indices.
    """
    return x.argmax(axis, keepdims=keepdims)


def get_diagonal(x: Tensor, d: int = 0) -> Tensor:
    """Extract a diagonal or construct a diagonal tensor.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    d : int, optional
        | Index of the diagonal. Defaults to ``0``.
        | ``0``: main diagonal
        | ``> 0``: above main diagonal
        | ``< 0``: below main diagonal

    Returns
    -------
    Tensor
        The extracted diagonal or constructed diagonal tensor.
    """
    if x.n_axes < 2:
        raise ShapeError("Input tensor must have at least 2 dimensions.")
    return Tensor(x.device.module.diag(x.data, d))


def max(
    x: Tensor, axis: Optional[AxisLike] = None, *, keepdims: bool = False
) -> Tensor:
    """Computes the maximum of tensor elements over a given axis.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    axis : AxisLike, optional
        Axis over which the maximum is computed. Defaults to ``None``.
        If none it is computed over the flattened tensor.
    keepdims : bool, optional
        Whether to keep the tensors dimensions. Defaults to ``False``.
        if ``False`` the tensor is collapsed along the given axis.

    Returns
    -------
    Tensor
        Tensor containing the maximum of elements.
    """
    return x.max(axis, keepdims=keepdims)


def maximum(x1: Tensor, x2: Tensor | ScalarLike) -> Tensor:
    """Computes the element-wise maximum of two tensors or a tensor and a scalar.

    Parameters
    ----------
    x1 : Tensor
        First tensor.
    x2 : Tensor | ScalarLike
        Second tensor or scalar.

    Returns
    -------
    Tensor
        Tensor containing the element-wise maximum.
    """
    return Tensor(x1.device.module.maximum(x1.data, to_arraylike(x2)))


def min(
    x: Tensor, axis: Optional[AxisLike] = None, *, keepdims: bool = False
) -> Tensor:
    """Computes the minimum of tensor elements over a given axis.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    axis : AxisLike, optional
        Axis over which the minimum is computed. Defaults to ``None``.
        If ``None`` it is computed over the flattened tensor.
    keepdims : bool, optional
        Whether to keep the tensors dimensions. Defaults to ``False``.
        if ``False`` the tensor is collapsed along the given axis.

    Returns
    -------
    Tensor
        Tensor containing the minimum of elements.
    """
    return x.min(axis, keepdims=keepdims)


def minimum(x1: Tensor, x2: Tensor | ScalarLike) -> Tensor:
    """Computes the element-wise minimum of two tensors or a tensor and a scalar.

    Parameters
    ----------
    x1 : Tensor
        First tensor.
    x2 : Tensor | ScalarLike
        Second tensor or scalar.

    Returns
    -------
    Tensor
        Tensor containing the element-wise minimum.
    """
    return Tensor(x1.device.module.minimum(x1.data, to_arraylike(x2)))


def topk(x: Tensor, k: int, axis: AxisLike = -1) -> tuple[Tensor, Tensor]:
    """Returns the k largest elements along a given axis.
    Implementation by https://hippocampus-garden.com/numpy_topk/.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    k : int
        Number of top elements to select.
    axis : AxisLike
        Axis, along which the top elements are selected. Defaults to ``-1``.

    Returns
    -------
    tuple[Tensor, Tensor]
        Tuple containing the top k elements and their indices.
    """
    ind = x.device.module.argpartition(-x.data, k, axis=axis)
    ind = x.device.module.take(ind, x.device.module.arange(k), axis=axis)
    data = x.device.module.take_along_axis(-x.data, ind, axis=axis)

    # sort within k elements
    ind_part = x.device.module.argsort(data, axis=axis)
    ind = x.device.module.take_along_axis(ind, ind_part, axis=axis)

    val = x.device.module.take_along_axis(-data, ind_part, axis=axis)
    return Tensor(val), Tensor(ind)


def tril(x: Tensor, diag_index: int = 0) -> Tensor:
    """Returns the lower triangle of a tensor below the
    diagonal of the last two dimensions.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    diag_index : int, optional
        | Index of the diagonal. Defaults to ``0``.
        | ``0``: main diagonal
        | ``> 0``: above main diagonal
        | ``< 0``: below main diagonal

    Returns
    -------
    Tensor
        Lower triangle tensor.
    """
    if x.n_axes < 2:
        raise ShapeError("Input tensor must have at least 2 dimensions.")
    return Tensor(x.device.module.tril(x.data, diag_index))


def triu(x: Tensor, diag_index: int = 0) -> Tensor:
    """Returns the upper triangle of a tensor above the
    diagonal of the last two dimensions.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    diag_index : int, optional
        | Index of the diagonal. Defaults to ``0``.
        | ``0``: main diagonal
        | ``> 0``: above main diagonal
        | ``< 0``: below main diagonal

    Returns
    -------
    Tensor
        Upper triangle tensor.
    """
    if x.n_axes < 2:
        raise ShapeError("Input tensor must have at least 2 dimensions.")
    return Tensor(x.device.module.triu(x.data, diag_index))


def unique(x: Tensor) -> Tensor:
    """Returns the unique ordered values of the tensor.

    Parameters
    ----------
    x : Tensor
        Input tensor.

    Returns
    -------
    Tensor
        Tensor containing unique values.
    """
    return Tensor(x.device.module.unique(x.data))
