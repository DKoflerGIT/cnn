"""Normalization layers module"""

from walnut import tensor_utils as tu
from walnut.tensor import Tensor, ArrayLike, ShapeLike
from walnut.nn.module import Module


__all__ = ["Batchnorm", "Layernorm"]


class Batchnorm(Module):
    """Batch Normalization."""

    def __init__(self, in_channels: int, eps: float = 1e-5, m: float = 0.1) -> None:
        """Implements Batch Normalization.

        Parameters
        ----------
        in_channels : int
            Number of input channels of the layer.
        eps : float, optional
            Constant for numerical stability, by default 1e-5.
        m : float, optional
            Momentum used for running mean and variance computation, by default 0.1.
        """
        super().__init__()
        self.in_channels = in_channels
        self.eps = eps
        self.m = m

        self.w = tu.ones((in_channels,))
        self.b = tu.zeros((in_channels,))
        self.parameters = [self.w, self.b]

        self.rmean = tu.zeros((in_channels,), device=self.device)
        self.rvar = tu.ones((in_channels,), device=self.device)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        in_channels = self.in_channels
        eps = self.eps
        m = self.m
        return f"{name}({in_channels=}, {eps=}, {m=})"

    def __call__(self, x: Tensor) -> Tensor:
        axis = (0,) + tuple(tu.arange(x.ndim).data[2:])
        if self.training:
            mean = x.mean(axis=axis, keepdims=True)
            var = x.var(axis=axis, keepdims=True)
            var_h = (var + self.eps) ** -0.5
            x_h = (x - mean) * var_h

            # keep running stats
            self.rmean = self.rmean * (1.0 - self.m) + mean.squeeze() * self.m
            _var = x.var(axis=axis, keepdims=True, ddof=1)  # torch uses ddof=1 here??
            self.rvar = self.rvar * (1.0 - self.m) + _var.squeeze() * self.m
        else:
            _rvar = tu.match_dims(self.rvar, x.ndim - 1)
            _rmean = tu.match_dims(self.rmean, x.ndim - 1)
            var_h = (_rvar + self.eps) ** -0.5
            x_h = (x - _rmean) * var_h

        weights = tu.match_dims(self.w, dims=x.ndim - 1)
        bias = tu.match_dims(self.b, dims=x.ndim - 1)
        y = weights * x_h + bias

        if self.training:

            def backward(dy: ArrayLike) -> ArrayLike:
                self.set_dy(dy)

                # input grads
                n = float(tu.prod(x.shape) / x.shape[1])  # cupy ?
                tmp1 = n * dy
                tmp2 = dy.sum(axis=axis, keepdims=True)
                tmp3 = (dy * x_h.data).sum(axis=axis, keepdims=True)
                x_grad = weights.data * var_h.data / n * (tmp1 - tmp2 - x_h.data * tmp3)

                # gamma grads
                self.w.grad = (x_h.data * dy).sum(axis=axis)

                # beta grads
                self.b.grad = dy.sum(axis=axis)

                return x_grad

            self.backward = backward

        self.set_y(y)
        return y


class Layernorm(Module):
    """Normalizes values per sample."""

    def __init__(self, normalized_shape: ShapeLike, eps: float = 1e-5) -> None:
        """Implements layer normalization.

        Parameters
        ----------
        normalized_shape : ShapeLike
            Shape of the normalized tensor ignoring the batch dimension.
        eps : float, optional
            Constant for numerical stability, by default 1e-5.
        """
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.w = tu.ones(normalized_shape)
        self.b = tu.zeros(normalized_shape)
        self.parameters = [self.w, self.b]

    def __repr__(self) -> str:
        name = self.__class__.__name__
        normalized_shape = self.normalized_shape
        eps = self.eps
        return f"{name}({normalized_shape=}, {eps=})"

    def __call__(self, x: Tensor) -> Tensor:
        axis = tuple(tu.arange(x.ndim).data[1:])
        mean = x.mean(axis=axis, keepdims=True)
        var = x.var(axis=axis, keepdims=True)
        var_h = (var + self.eps) ** -0.5
        x_h = (x - mean) * var_h
        y = self.w * x_h + self.b

        if self.training:

            def backward(dy: ArrayLike) -> ArrayLike:
                self.set_dy(dy)

                # input grads
                n = x.data[0].size
                tmp1 = n * dy
                tmp2 = dy.sum(axis, keepdims=True)
                tmp3 = (dy * x_h.data).sum(axis, keepdims=True)
                x_grad = self.w.data * var_h.data / n * (tmp1 - tmp2 - x_h.data * tmp3)

                # gamma grads
                self.w.grad = (x_h.data * dy).sum(axis=0)

                # beta grads
                self.b.grad = dy.sum(axis=0)

                return x_grad

            self.backward = backward

        self.set_y(y)
        return y
