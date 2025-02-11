"""Neural network block modules."""

from typing import Optional

from ..utils.initializers import InitializerLike, get_initializer
from .activations import ActivationLike, get_activation
from .containers import Sequential
from .convolutions import Conv1D, Conv2D, PaddingLike
from .linear import Linear
from .normalizations import BatchNorm1D, BatchNorm2D

__all__ = ["Conv1DBlock", "Conv2DBlock", "DenseBlock"]


class DenseBlock(Sequential):
    """Dense neural network block containing a linear transformation layer
    and an activation function.

    Shapes:
        - Input :math:`(B_1, ... , B_n, C_{in})`
        - Output :math:`(B_1, ... , B_n, C_{out})`
    where
        - :math:`B_1, ... , B_n` ... batch dimensions
        - :math:`C_{in}` ... input channels
        - :math:`C_{out}` ... output channels

    Parameters
    ----------
    in_channels : int
        Number of input features.
    out_channels : int
        Number of output channels (neurons) of the dense block.
    activation : ActivationLike
        Activation function to use in the block.
        See :ref:`activations` for more details.
    weight_init : InitializerLike, optional
        What method to use for initializing weight parameters. Defaults to ``xavier_uniform``.
        See :ref:`initializers` for more details.
    bias : bool, optional
        Whether to use bias values. Defaults to ``True``.
    bias_init : InitializerLike, optional
        What method to use for initializing bias parameters. Defaults to ``zeros``.
        See :ref:`initializers` for more details.
    label : str, optional
        Module label. Defaults to ``None``. If ``None``, the class name is used.


    See Also
    --------
    :class:`compyute.nn.Linear`
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        activation: ActivationLike,
        weight_init: InitializerLike = "xavier_uniform",
        bias: bool = True,
        bias_init: InitializerLike = "zeros",
        label: Optional[str] = None,
    ) -> None:
        linear = Linear(in_channels, out_channels, bias)
        w_init = get_initializer(weight_init, activation)
        w_init(linear.w)
        if linear.b:
            b_init = get_initializer(bias_init, activation)
            b_init(linear.b)

        act = get_activation(activation)

        super().__init__(linear, act, label=label)


class Conv1DBlock(Sequential):
    """Convolution block containing a 1D convolutional layer, followed by an
    optional batch normalization and an activation function.

    Shapes:
        - Input :math:`(B, C_{in}, S_{in})`
        - Output :math:`(B, C_{out}, S_{out})`
    where
        - :math:`B` ... batch dimension
        - :math:`C_{in}` ... input channels
        - :math:`S_{in}` ... input sequence
        - :math:`C_{out}` ... output channels
        - :math:`S_{out}` ... output sequence

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels (filters).
    kernel_size : int
        Size of each kernel.
    activation : ActivationLike
        Activation function to use in the block.
        See :ref:`activations` for more details.
    padding : PaddingLike, optional
        Padding applied before convolution. Defaults to ``valid``.
    stride : int, optional
        Stride used for the convolution operation. Defaults to ``1``.
    dilation : int, optional
        Dilation used for each dimension of the filter. Defaults to ``1``.
    weight_init : InitializerLike, optional
        What method to use for initializing weight parameters. Defaults to ``xavier_uniform``.
        See :ref:`initializers` for more details.
    bias : bool, optional
        Whether to use bias values. Defaults to ``True``.
    bias_init : _InitializerLike, optional
        What method to use for initializing bias parameters. Defaults to ``zeros``.
        See :ref:`initializers` for more details.
    batchnorm : bool, optional
        Whether to use batch normalization. Defaults to ``False``.
    batchnorm_eps : float, optional
        Constant for numerical stability used in batch normalization. Defaults to ``1e-5``.
    batchnorm_m : float, optional
        Momentum used in batch normalization. Defaults to ``0.1``.
    label : str, optional
        Module label. Defaults to ``None``. If ``None``, the class name is used.


    See Also
    --------
    :class:`compyute.nn.Convolution1D`
    :class:`compyute.nn.BatchNorm1D`
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        activation: ActivationLike,
        padding: PaddingLike = "valid",
        stride: int = 1,
        dilation: int = 1,
        weight_init: InitializerLike = "xavier_uniform",
        bias: bool = True,
        bias_init: InitializerLike = "zeros",
        batchnorm: bool = False,
        batchnorm_eps: float = 1e-5,
        batchnorm_m: float = 0.1,
        label: Optional[str] = None,
    ) -> None:
        conv = Conv1D(
            in_channels,
            out_channels,
            kernel_size,
            padding,
            stride,
            dilation,
            bias,
        )
        w_init = get_initializer(weight_init, activation)
        w_init(conv.w)
        if conv.b:
            b_init = get_initializer(bias_init, activation)
            b_init(conv.b)

        act = get_activation(activation)

        if batchnorm:
            bn = BatchNorm1D(out_channels, batchnorm_eps, batchnorm_m)
            super().__init__(conv, bn, act, label=label)
        else:
            super().__init__(conv, act, label=label)


class Conv2DBlock(Sequential):
    """Convolution block containing a 2D convolutional layer, followed by an
    optional batch normalization and an activation function.

    Shapes:
        - Input :math:`(B, C_{in}, Y_{in}, X_{in})`
        - Output :math:`(B, C_{out}, Y_{out}, X_{out})`
    where
        - :math:`B` ... batch dimension
        - :math:`C_{in}` ... input channels
        - :math:`Y_{in}` ... input height
        - :math:`X_{in}` ... input width
        - :math:`C_{out}` ... output channels
        - :math:`Y_{out}` ... output height
        - :math:`X_{out}` ... output width

    Parameters
    ----------
    in_channels : int
        Number of input channels (color channels).
    out_channels : int
        Number of output channels (filters or feature maps).
    kernel_size : int
        Size of each kernel.
    activation : ActivationLike
        Activation function to use in the block.
        See :ref:`activations` for more details.
    padding : PaddingLike, optional
        Padding applied before convolution. Defaults to ``valid``.
    stride : int , optional
        Strides used for the convolution operation. Defaults to ``1``.
    dilation : int , optional
        Dilations used for each dimension of the filter. Defaults to ``1``.
    weight_init : InitializerLike, optional
        What method to use for initializing weight parameters. Defaults to ``xavier_uniform``.
        See :ref:`initializers` for more details.
    bias : bool, optional
        Whether to use bias values. Defaults to ``True``.
    bias_init : InitializerLike, optional
        What method to use for initializing bias parameters. Defaults to ``zeros``.
        See :ref:`initializers` for more details.
    batchnorm : bool, optional
        Whether to use batch normalization. Defaults to ``False``.
    batchnorm_eps : float, optional
        Constant for numerical stability used in batch normalization. Defaults to ``1e-5``.
    batchnorm_m : float, optional
        Momentum used in batch normalization. Defaults to ``0.1``.
    label : str, optional
        Module label. Defaults to ``None``. If ``None``, the class name is used.


    See Also
    --------
    :class:`compyute.nn.Convolution2D`
    :class:`compyute.nn.BatchNorm2D`
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        activation: ActivationLike,
        padding: PaddingLike = "valid",
        stride: int = 1,
        dilation: int = 1,
        weight_init: InitializerLike = "xavier_uniform",
        bias: bool = True,
        bias_init: InitializerLike = "zeros",
        batchnorm: bool = False,
        batchnorm_eps: float = 1e-5,
        batchnorm_m: float = 0.1,
        label: Optional[str] = None,
    ) -> None:
        conv = Conv2D(
            in_channels, out_channels, kernel_size, padding, stride, dilation, bias
        )
        w_init = get_initializer(weight_init, activation)
        w_init(conv.w)
        if conv.b:
            b_init = get_initializer(bias_init, activation)
            b_init(conv.b)

        act = get_activation(activation)

        if batchnorm:
            bn = BatchNorm2D(out_channels, batchnorm_eps, batchnorm_m)
            super().__init__(conv, bn, act, label=label)
        else:
            super().__init__(conv, act, label=label)
