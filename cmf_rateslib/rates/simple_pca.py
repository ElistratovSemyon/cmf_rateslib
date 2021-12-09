
from ..rates.base_model import BaseRatesModel
from ..curves.zero_curve import ZeroCurve
import numpy as np
from sympy.solvers import solve
from sympy import Symbol
import random


class SimplePCAModel(BaseRatesModel):

    def __init__(self, maturities, maturity_loadings, factor_vols):
        super().__init__()

        maturities = np.array(maturities)
        maturity_loadings = np.array(maturity_loadings)
        factor_vols = np.array(factor_vols)

        if maturities.shape[0] != maturity_loadings.shape[0]:
            raise ValueError("Shapes of maturities and maturity_loadings don't match")

        if factor_vols.shape[0] != maturity_loadings.shape[1]:
            raise ValueError("Shapes of factor_vols and maturity_loadings don't match")

        self.params['maturities'] = maturities
        self.params['loadings'] = maturity_loadings
        self.params['num_factors'] = maturity_loadings.shape[1]
        self.params['factor_vols'] = factor_vols

    def evolve_zero_curve(self, start_curve: ZeroCurve, num_periods: int, dt: float):

        U = self.params['loadings']
        num_factors = self.params['num_factors']
        sigma = self.params['factor_vols']

        maturities = self.params['maturities']

        dW = np.random.randn(num_periods, num_factors) * np.sqrt(dt)

        # increments of PCA factors
        dX = sigma * dW 

        # increments of zero rates
        dZ = U.dot(dX.T)

        starting_rates = start_curve.zero_rate(maturities)

        all_rates = np.cumsum(np.concatenate([[starting_rates], dZ.T]), axis = 0)[1:, :]


        return [ZeroCurve(maturities, rates) for rates in all_rates]

    def create_new(self, num: int, dt: float):

        U = self.params['loadings']
        num_factors = self.params['num_factors']
        sigma = self.params['factor_vols']
        maturities = self.params['maturities']


        dW = np.random.randn(num, num_factors) * np.sqrt(dt)
        dX = sigma * dW
        dZ = U.dot(dX.T)

        return [ZeroCurve(maturities, rates) for rates in dZ.T]


    def fit(self, curves):
        # dZ = UdX. Кривые задаются матрицей Z.
        # в силу спектрального разложения матрицы  - мы можем раложить матрицу ковариации dZ с dZ в прозведение матрицы
        # из лоадингов и диагональной матрицы  с собственными значениями, которые будут являться нашей волатильностью.
        # Следовательно, необоходимо вывести матрицу лоадингов, собственные значения и собственные вектора
        U = self.params['loadings']
        curves_rates = []
        for curve in curves:
            curves_rates.append(curve._rates)
        curves_rates = np.array(curves_rates)
        Cov = np.cov(curves_rates)
        eigvalues, eigvectors = np.linalg.eig(Cov)
        return eigvalues, eigvectors, U

    #  пытался сам написать скореллированные кривые. Не спрослось( (не работает)
    '''def gen_cor_curve(self, dt: float, cor: float):

        vol = self.params['factor_vols']
        maturities = self.params['maturities']

        curv1 = []
        cor_curves = []
        for m in maturities:
            for v in vol:
                curv1.append(np.random.randn(m * 253) * np.sqrt(dt) * v)
                curv_to_cor = np.random.randn(m * 253) * np.sqrt(dt) * v
                x = Symbol('x')
                tmp_curve = np.random.randn(m * 253) * np.sqrt(dt) * x
                tmp = []
                for i in range(m * 253):
                    tmp.append((curv_to_cor[i] - curv_to_cor.mean()) * (tmp_curve[i] - tmp_curve.mean()))
                tmp = np.array(tmp)
                sought_std = solve(tmp.mean() / (v * x) - cor, x)
                cor_curves.append(np.random.randn(m * 253) * np.sqrt(dt))

        return sought_std, curv1, cor_curves'''







