import pytest

from fminus.dsl import LAN
from fminus.exceptions.dsl import ListVariableAlphaError, ListVariableNumError


class TestDsl:

    S = '''
        data: file is a.txt;
        variable:	names are y1-y12;
        model:
        ! 1111111111 aaa
        f1 by y1-y3*0.8;
        f2 by y4, y5@1.5, y6*;
        f3 by y7-y9;
        f4 by y10-y12@1;
        f3 ON f1-f2*2;
        f4 ON f3;
        y1 with y2;
        y3 with y4-y7*0.7;
    '''
    Tree = LAN.parseString(S)

    def test_file_name(self):
        assert self.Tree.data.file_name == 'a.txt'

    def test_ob_var(self):
        var_list = ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9', 'y10', 'y11', 'y12']
        assert list(self.Tree.observed_variable.observed) == var_list

    def test_model_factor_by_zero_latent(self):
        assert self.Tree.model.factor_by[0].latent == 'f1'

    def test_model_factor_by_zero_ob(self):
        f1_ob_vars = [
            {'name': 'y1', 'free': True, 'value': 0.8},
            {'name': 'y2', 'free': True, 'value': 0.8},
            {'name': 'y3', 'free': True, 'value': 0.8}
        ]
        assert list(self.Tree.model.factor_by[0].observes) == f1_ob_vars

    def test_model_factor_by_one_latent(self):
        assert self.Tree.model.factor_by[1].latent == 'f2'

    def test_model_factor_by_one_ob(self):
        f2_ob_vars = [
            {'name': 'y4', 'free': True, 'value': 0.7},
            {'name': 'y5', 'free': False, 'value': 1.5},
            {'name': 'y6', 'free': True, 'value': 0.7},
        ]
        assert list(self.Tree.model.factor_by[1].observes) == f2_ob_vars

    def test_model_factor_by_three_ob(self):
        f3_ob_vars = [
            {'name': 'y7', 'free': False, 'value': 1},
            {'name': 'y8', 'free': True, 'value': 0.7},
            {'name': 'y9', 'free': True, 'value': 0.7},
        ]
        assert list(self.Tree.model.factor_by[2].observes) == f3_ob_vars

    def test_model_factor_by_four_ob(self):
        f4_ob_vars = [
            {'name': 'y10', 'free': False, 'value': 1},
            {'name': 'y11', 'free': False, 'value': 1},
            {'name': 'y12', 'free': False, 'value': 1},
        ]
        assert list(self.Tree.model.factor_by[3].observes) == f4_ob_vars

    def test_regression_on_one_depend(self):
        assert self.Tree.regression_on[0].dependent == 'f3'

    def test_regression_on_two_depend(self):
        assert self.Tree.regression_on[1].dependent == 'f4'

    def test_regression_on_one_independent(self):
        f3_independent_vars = [
            {'name': 'f1', 'free': True, 'value': 2},
            {'name': 'f2', 'free': True, 'value': 2}
        ]
        assert list(self.Tree.regression_on[0].independent) == f3_independent_vars

    def test_regression_on_two_independent(self):
        f4_independent_vars = [
            {'name': 'f3', 'free': True, 'value': 1}
        ]
        assert list(self.Tree.regression_on[1].independent) == f4_independent_vars

    def test_corr_with_zero_lt(self):
        assert self.Tree.corr_with[0].corr_lt == 'y1'

    def test_corr_with_one_lt(self):
        assert self.Tree.corr_with[1].corr_lt == 'y3'

    def test_corr_with_zero_rt(self):
        pass

    def test_corr_with_one_rt(self):
        pass


class TestModelVar:

    def test_mix(self):
        s = '''
                data: file is a.txt;
                variable:
                names are y1-y8;
                model:
                ! 1111111111 aaa
                f1 by y1, y2-y4, y5, y6-y8;
            '''
        tree = LAN.parseString(s)
        f1_ob_vars = [
            {'name': 'y1', 'free': False, 'value': 1},
            {'name': 'y2', 'free': True, 'value': 0.7},
            {'name': 'y3', 'free': True, 'value': 0.7},
            {'name': 'y4', 'free': True, 'value': 0.7},
            {'name': 'y5', 'free': True, 'value': 0.7},
            {'name': 'y6', 'free': True, 'value': 0.7},
            {'name': 'y7', 'free': True, 'value': 0.7},
            {'name': 'y8', 'free': True, 'value': 0.7},
        ]
        assert list(tree.model.factor_by[0].observes) == f1_ob_vars


class TestListVarExc:

    def test_list_variable_alpha_exception(self):
        s = '''
                data: file is a.txt;
                variable: names are x1-y6;
                model:
                ! 1111111111 aaa
                f1 by y1-y3;
                f2 by y4, y5, y6;
            '''
        with pytest.raises(ListVariableAlphaError):
            LAN.parseString(s)

    def test_list_variable_num_exception(self):
        s = '''
                data: file is a.txt;
                variable: names are y6-y1;
                model:
                ! 1111111111 aaa
                f1 by y1-y3;
                f2 by y4, y5, y6;
            '''
        with pytest.raises(ListVariableNumError):
            LAN.parseString(s)

    def test_list_variable_num_eq_exception(self):
        s = '''
                data: file is a.txt;
                variable: names are y1-y1;
                model:
                ! 1111111111 aaa
                f1 by y1-y3;
                f2 by y4, y5, y6;
            '''
        with pytest.raises(ListVariableNumError):
            LAN.parseString(s)
