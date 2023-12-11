import autograd.numpy as np
import pytest
import scipy
import pymanopt
from pymanopt.optimizers import FrankWolfe
from pymanopt.manifolds import SymmetricPositiveDefinite
class TestFrankWolfe:
    n = 3
    N = 50
    matrices = [np.random.uniform(size=(n, n)) for i in range(N)]
    matricespd = np.array([
        matrix @ matrix.T for matrix in matrices
    ])
    matricesinv = np.array([
        np.linalg.inv(matrix) for matrix in matricespd
    ])
    manifold = manifold = SymmetricPositiveDefinite(n)
    @pymanopt.function.autograd(manifold)
    def cost(X):
        # print(type(X))
        X = np.array(X)
        # print(type(X))
        # evalues, evectors = np.linalg.eig()
        Xinvsqrt = np.array(np.linalg.inv(scipy.linalg.sqrtm(X)))
        # print(type(Xinvsqrt))
        return sum(
            np.linalg.norm(scipy.linalg.logm(Xinvsqrt @ matrix @ Xinvsqrt)) for matrix in matricespd
        )
    @pymanopt.function.autograd(manifold)
    def rieman_grad(X):
          Xinv = np.linalg.inv(X)
          return sum(
            Xinv @ scipy.linalg.logm(X @ matrix) for matrix in matricesinv
        )
    problem = pymanopt.Problem(manifold, cost, riemannian_gradient=rieman_grad)
    U = np.mean(matricespd, axis = 0)
    U = U
    print(matricespd)
    L = np.linalg.inv(np.sum(1/len(matrices)*matricesinv, axis = 0))
    L = L
    print(L)
    print(U)
    optimizer = FrankWolfe()
    initial_point = (L+U)/2
    print(np.linalg.cholesky(U))
    print(np.linalg.cholesky(L))
    result = optimizer.run(problem, L, U, initial_point = initial_point)
    print(result)
