import numpy as np

from pymanopt.manifolds.manifold import Manifold


class PoincareBall(Manifold):
    r"""The Poincare ball.

    An instance represents the Cartesian product of n (defaults to 1)
    Poincare balls of dimension k.
    Elements are represented as matrices of size k x n, or arrays of
    size k if n = 1.

    The Poincare ball is embedded in R^k and is a Riemannian manifold,
    but it is not an embedded Riemannian submanifold.
    At every point x, the tangent space at x is R^k since the manifold
    is open.

    The metric is conformal to the Euclidean one (angles are preserved),
    and it is given at every point :math:`\vmx` by
    :math:`\inner{\vmu}{\vmv}_\vmx = \lambda_\vmx \inner{\vmu}{\vmv}` where
    :math:`\lambda_\vmx = 2 / (1 - \norm{\vmx}^2)` is the conformal factor.
    This induces the following distance between two points :math:`\vmx` and
    :math:`\vmy` on the manifold:

        :math:`\dist_\manM(\vmx, \vmy) = \arccosh\parens{1 + 2 \frac{\norm{\vmx
        - \vmy}^2}{(1 - \norm{\vmx}^2) (1 - \norm{\vmy}^2)}}.`

    The norm here is understood as the Euclidean norm in the ambient space.
    """

    def __init__(self, k: int, n: int = 1):
        self._k = k
        self._n = n

        if k < 1:
            raise ValueError(f"Need k >= 1. Value given was k = {k}")
        if n < 1:
            raise ValueError(f"Need n >= 1. Value given was n = {n}")

        if n == 1:
            name = f"Poincare ball B({k})"
        elif n >= 2:
            name = f"Poincare ball B({k})^{n}"

        dimension = k * n
        super().__init__(name, dimension)

    @property
    def typical_dist(self):
        return self.dim / 8

    def inner_product(self, point, tangent_vector_a, tangent_vector_b):
        factors = self.conformal_factor(point) ** 2
        return np.sum(tangent_vector_a * tangent_vector_b * factors)

    def projection(self, point, vector):
        return vector

    def norm(self, point, tangent_vector):
        return np.sqrt(
            self.inner_product(point, tangent_vector, tangent_vector)
        )

    def random_point(self):
        if self._n == 1:
            array = np.random.normal(size=self._k)
        else:
            array = np.random.normal(size=(self._k, self._n))
        norms = np.linalg.norm(array, axis=0)
        radiuses = np.random.uniform(size=self._n) ** (1.0 / self._k)
        return radiuses * array / norms

    def random_tangent_vector(self, point):
        return np.random.normal(size=np.shape(point))

    def zero_vector(self, point):
        return np.zeros_like(point)

    def dist(self, point_a, point_b):
        norms2_point_a = np.sum(point_a * point_a, axis=0)
        norms2_point_b = np.sum(point_b * point_b, axis=0)
        difference = point_a - point_b
        norms2_difference = np.sum(difference * difference, axis=0)

        columns_dist = np.arccosh(
            1
            + 2
            * norms2_difference
            / ((1 - norms2_point_a) * (1 - norms2_point_b))
        )
        return np.sqrt(np.sum(np.square(columns_dist)))

    def euclidean_to_riemannian_gradient(self, point, euclidean_gradient):
        # The hyperbolic metric tensor is conformal to the Euclidean one, so
        # the Euclidean gradient is simply rescaled.
        factors = 1 / self.conformal_factor(point) ** 2
        return euclidean_gradient * factors

    def euclidean_to_riemannian_hessian(
        self, point, euclidean_gradient, euclidean_hessian, tangent_vector
    ):
        # This expression is derived from the Koszul formula.
        lambda_x = self.conformal_factor(point)
        return (
            np.sum(euclidean_gradient * point, axis=0) * tangent_vector
            - np.sum(point * tangent_vector, axis=0) * euclidean_gradient
            - np.sum(euclidean_gradient * tangent_vector, axis=0) * point
            + euclidean_hessian / lambda_x
        ) / lambda_x

    def exp(self, point, tangent_vector):
        norm_point = np.linalg.norm(tangent_vector, axis=0)
        # Handle the case where tangent_vector is 0.
        W = tangent_vector * np.divide(
            np.tanh(norm_point / (1 - np.sum(point * point, axis=0))),
            norm_point,
            out=np.zeros_like(tangent_vector),
            where=norm_point != 0,
        )
        return self.mobius_addition(point, W)

    retraction = exp

    def log(self, point_a, point_b):
        W = self.mobius_addition(-point_a, point_b)
        norm_W = np.linalg.norm(W, axis=0)
        return (
            (1 - np.sum(point_a * point_a, axis=0))
            * np.arctanh(norm_W)
            * W
            / norm_W
        )

    def pair_mean(self, point_a, point_b):
        return self.exp(point_a, self.log(point_a, point_b) / 2)

    def mobius_addition(self, point_a, point_b):
        """Möbius addition.

        Special non-associative and non-commutative operation which is closed
        in the Poincare ball.

        Args:
            point_a: The first point.
            point_b: The second point.

        Returns:
            The Möbius sum of ``point_a`` and ``point_b``.
        """
        scalar_product = np.sum(point_a * point_b, axis=0)
        norm_point_a = np.sum(point_a * point_a, axis=0)
        norm_point_b = np.sum(point_b * point_b, axis=0)

        return (
            point_a * (1 + 2 * scalar_product + norm_point_b)
            + point_b * (1 - norm_point_a)
        ) / (1 + 2 * scalar_product + norm_point_a * norm_point_b)

    def conformal_factor(self, point):
        return 2 / (1 - np.sum(point * point, axis=0))
