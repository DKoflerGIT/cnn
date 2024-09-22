"""Neural network normalization functions."""

from ...tensor_ops.reshape_ops import insert_dim, squeeze
from ...tensor_ops.unary_ops import sqrt
from ...tensors import Tensor
from .functions import Function, FunctionCache, PseudoCache

__all__ = ["batchnorm1d", "batchnorm2d", "layernorm", "rmsnorm"]


class BatchNorm1DFn(Function):
    """Performs 1D batch normalization on a tensor."""

    @staticmethod
    def forward(
        cache: FunctionCache,
        x: Tensor,
        rmean: Tensor,
        rvar: Tensor,
        w: Tensor,
        b: Tensor,
        m: float,
        eps: float,
        training: bool,
    ) -> tuple[Tensor, Tensor, Tensor]:
        x_is_2d = x.n_axes == 2
        batch_axes: tuple[int, ...] = (0,) if x.n_axes == 2 else (0, 2)

        if training:
            # compute mean and variance from x
            mean = x.mean(batch_axes, keepdims=True)
            std = sqrt(x.var(batch_axes, keepdims=True) + eps)
            x_norm = (x - mean) / std

            # keep running stats
            rmean = rmean * (1 - m) + squeeze(mean) * m
            rvar = rvar * (1 - m) + x.var(batch_axes, ddof=1) * m
        else:
            # use running mean and variance
            var = rvar if x_is_2d else insert_dim(rvar, -1)
            mean = rmean if x_is_2d else insert_dim(rmean, -1)
            std = sqrt(var + eps)
            x_norm = (x - mean) / std

        w = w if x_is_2d else insert_dim(w, -1)
        b = b if x_is_2d else insert_dim(b, -1)
        y = w * x_norm + b

        cache.push(w, batch_axes, std, x_norm)
        return y, rmean, rvar

    @staticmethod
    def backward(cache: FunctionCache, dy: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        w, batch_axes, std, x_norm = cache.pop()
        n = float(dy.size / dy.shape[1])

        # input grads
        dy_sum = dy.sum(batch_axes, keepdims=True)
        dy_x_norm_sum = (dy * x_norm).sum(batch_axes, keepdims=True)
        dx = w / (std * n) * (n * dy - dy_sum - x_norm * dy_x_norm_sum)

        # gamma grads
        dw = squeeze(dy_x_norm_sum)

        # beta grads
        db = squeeze(dy_sum)

        return dx, dw, db


def batchnorm1d(
    x: Tensor,
    rmean: Tensor,
    rvar: Tensor,
    w: Tensor,
    b: Tensor,
    m: float = 0.1,
    eps: float = 1e-5,
    training: bool = False,
) -> tuple[Tensor, Tensor, Tensor]:
    """Performs 1D batch normalization on a tensor.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    rmean : Tensor
        Running mean tensor.
    rvar : Tensor
        Running variance tensor.
    w : Tensor
        Weight tensor for scaling the distribution.
    b : Tensor
        Bias tensor for shifting the distribution.
    m : float, optional
        Momentum used for running mean and variance computation. Defaults to ``0.1``.
    eps : float, optional
        Constant for numerical stability. Defaults to ``1e-5``.
    training : bool, optional
        Whether to perform calculations in training mode. Defaults to ``False``.

    Returns
    -------
    Tensor
        Output tensor.
    Tensor
        New running mean.
    Tensor
        New running variance.

    See Also
    ----------
    :class:`compyute.nn.BatchNorm1D`
    """
    return BatchNorm1DFn.forward(PseudoCache(), x, rmean, rvar, w, b, m, eps, training)


class BatchNorm2DFn(Function):
    """Performs 2D batch normalization on a tensor."""

    @staticmethod
    def forward(
        cache: FunctionCache,
        x: Tensor,
        rmean: Tensor,
        rvar: Tensor,
        w: Tensor,
        b: Tensor,
        m: float,
        eps: float,
        training: bool,
    ) -> tuple[Tensor, Tensor, Tensor]:
        batch_axes = (0, 2, 3)

        if training:
            # compute mean and variance from x
            mean = x.mean(batch_axes, keepdims=True)
            std = sqrt(x.var(batch_axes, keepdims=True) + eps)
            x_norm = (x - mean) / std

            # keep running stats
            rmean = rmean * (1 - m) + squeeze(mean) * m
            rvar = rvar * (1 - m) + x.var(batch_axes, ddof=1) * m
        else:
            # use running mean and variance
            mean = rmean.to_shape((*rmean.shape, 1, 1))
            std = sqrt(rvar.to_shape((*rvar.shape, 1, 1)) + eps)
            x_norm = (x - mean) / std

        w = w.to_shape((*w.shape, 1, 1))
        b = b.to_shape((*b.shape, 1, 1))
        y = w * x_norm + b

        cache.push(w, batch_axes, std, x_norm)
        return y, rmean, rvar

    @staticmethod
    def backward(cache: FunctionCache, dy: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        w, batch_axes, std, x_norm = cache.pop()
        n = float(dy.size / dy.shape[1])

        # input grads
        dy_sum = dy.sum(batch_axes, keepdims=True)
        dy_x_norm_sum = (dy * x_norm).sum(batch_axes, keepdims=True)
        dx = w / (std * n) * (n * dy - dy_sum - x_norm * dy_x_norm_sum)

        # gamma grads
        dw = squeeze(dy_x_norm_sum)

        # beta grads
        db = squeeze(dy_sum)

        return dx, dw, db


def batchnorm2d(
    x: Tensor,
    rmean: Tensor,
    rvar: Tensor,
    w: Tensor,
    b: Tensor,
    m: float = 0.1,
    eps: float = 1e-5,
    training: bool = False,
) -> tuple[Tensor, Tensor, Tensor]:
    """Performs 2D batch normalization on a tensor.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    rmean : Tensor
        Running mean values.
    rvar : Tensor
        Running variance values.
    w : Tensor
        Weight tensor for scaling the distribution.
    b : Tensor
        Bias tensor for shifting the distribution.
    m : float, optional
        Momentum used for running mean and variance computation. Defaults to ``0.1``.
    eps : float, optional
        Constant for numerical stability. Defaults to ``1e-5``.
    training : bool, optional
        Whether to perform calculations in training mode. Defaults to ``False``.

    Returns
    -------
    Tensor
        Output tensor.
    Tensor
        New running mean.
    Tensor
        New running variance.

    See Also
    ----------
    :class:`compyute.nn.BatchNorm2D`
    """
    return BatchNorm2DFn.forward(PseudoCache(), x, rmean, rvar, w, b, m, eps, training)


class LayerNormFn(Function):
    """Performs layer normalization on a tensor."""

    @staticmethod
    def forward(
        cache: FunctionCache, x: Tensor, w: Tensor, b: Tensor, eps: float
    ) -> Tensor:
        feat_axes = tuple(-i - 1 for i in range(w.n_axes))

        mean = x.mean(feat_axes, keepdims=True)
        std = sqrt(x.var(feat_axes, keepdims=True) + eps)
        x_norm = (x - mean) / std
        y = w * x_norm + b

        cache.push(w, feat_axes, std, x_norm)
        return y

    @staticmethod
    def backward(cache: FunctionCache, dy: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        w, feat_axes, std, x_norm = cache.pop()
        batch_axes = tuple(range(dy.n_axes - w.n_axes))

        # input grads
        dy_sum = dy.sum(feat_axes, keepdims=True)
        dy_x_norm = dy * x_norm
        dy_x_norm_sum = dy_x_norm.sum(feat_axes, keepdims=True)
        dx = w / (std * w.size) * (w.size * dy - dy_sum - x_norm * dy_x_norm_sum)

        # gamma grads
        dw = dy_x_norm.sum(batch_axes)

        # beta grads
        db = dy.sum(batch_axes)

        return dx, dw, db


def layernorm(x: Tensor, w: Tensor, b: Tensor, eps: float = 1e-5) -> Tensor:
    """Performs layer normalization on a tensor.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    w : Tensor
        Weight tensor for scaling the distribution.
    b : Tensor
        Bias tensor for shifting the distribution.
    eps : float, optional
        Constant for numerical stability. Defaults to ``1e-5``.

    Returns
    -------
    Tensor
        Output tensor.

    See Also
    ----------
    :class:`compyute.nn.LayerNorm`
    """
    return LayerNormFn.forward(PseudoCache(), x, w, b, eps)


class RMSNormFn(Function):
    """Performs RMS normalization on a tensor."""

    @staticmethod
    def forward(cache: FunctionCache, x: Tensor, w: Tensor, eps: float) -> Tensor:
        feat_axes = tuple(-i - 1 for i in range(w.n_axes))

        rms = sqrt((x * x).mean(feat_axes, keepdims=True) + eps)
        x_norm = x / rms
        y = w * x_norm

        cache.push(x, w, feat_axes, rms, x_norm)
        return y

    @staticmethod
    def backward(cache: FunctionCache, dy: Tensor) -> tuple[Tensor, Tensor]:
        x, w, feat_axes, rms, x_norm = cache.pop()
        sum_axes = tuple(range(x.n_axes - w.n_axes))

        # input grads
        dy_x_sum = (dy * x).sum(feat_axes, keepdims=True)
        dx = w / rms * (dy - x_norm * dy_x_sum / (w.size * rms))

        # gamma grads
        dw = (dy * x_norm).sum(sum_axes)

        return dx, dw


def rmsnorm(x: Tensor, w: Tensor, eps: float = 1e-5) -> Tensor:
    """Performs RMS normalization on a tensor.

    Parameters
    ----------
    x : Tensor
        Input tensor.
    w : Tensor
        Weight tensor for scaling the distribution.
    eps : float, optional
        Constant for numerical stability. Defaults to ``1e-5``.

    Returns
    -------
    Tensor
        Output tensor.

    See Also
    ----------
    :class:`compyute.nn.RMSNorm`
    """
    return RMSNormFn.forward(PseudoCache(), x, w, eps)
