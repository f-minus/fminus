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
    '''
    Tree = LAN.parseString(S)

    def test_file_name(self):
        assert self.Tree.data.file_name == 'a.txt'

    def test_ob_var(self):
        var_list = ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9', 'y10', 'y11', 'y12']
        assert list(self.Tree.observed_variable.observes) == var_list

    def test_model_factor_by(self):
        assert self.Tree.model.factor_by[0].latent == 'f1'
        f1_ob_vars = [
            {'name': 'y1', 'free': True, 'value': 0.8},
            {'name': 'y2', 'free': True, 'value': 0.8},
            {'name': 'y3', 'free': True, 'value': 0.8}
        ]
        assert list(self.Tree.model.factor_by[0].observes) == f1_ob_vars
        assert self.Tree.model.factor_by[1].latent == 'f2'
        f2_ob_vars = [
            {'name': 'y4', 'free': True, 'value': 0.7},
            {'name': 'y5', 'free': False, 'value': 1.5},
            {'name': 'y6', 'free': True, 'value': 0.7},
        ]
        assert list(self.Tree.model.factor_by[1].observes) == f2_ob_vars
        f3_ob_vars = [
            {'name': 'y7', 'free': False, 'value': 1},
            {'name': 'y8', 'free': True, 'value': 0.7},
            {'name': 'y9', 'free': True, 'value': 0.7},
        ]
        assert list(self.Tree.model.factor_by[2].observes) == f3_ob_vars
        f4_ob_vars = [
            {'name': 'y10', 'free': False, 'value': 1},
            {'name': 'y11', 'free': False, 'value': 1},
            {'name': 'y12', 'free': False, 'value': 1},
        ]
        assert list(self.Tree.model.factor_by[3].observes) == f4_ob_vars


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
