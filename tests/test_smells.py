"""Tests for code smell detector."""

import pytest

from socratic_analyzer.analyzers.smells import CodeSmellDetector


class TestCodeSmellDetector:
    """Test CodeSmellDetector."""

    @pytest.fixture
    def detector(self) -> CodeSmellDetector:
        """Provide code smell detector."""
        return CodeSmellDetector()

    def test_detector_properties(self, detector) -> None:
        """Test detector properties."""
        assert detector.name == "Code Smell Detector"
        assert "smell" in detector.description.lower()

    def test_long_method_detection(self, detector) -> None:
        """Test detection of long methods."""
        code = '''
def long_method():
    """ Long method with many lines."""
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x1 = 27
    y1 = 28
    z1 = 29
    a1 = 30
    b1 = 31
    c1 = 32
    d1 = 33
    e1 = 34
    f1 = 35
    g1 = 36
    h1 = 37
    i1 = 38
    i2 = 39
    j1 = 40
    k1 = 41
    l1 = 42
    m1 = 43
    n1 = 44
    o1 = 45
    p1 = 46
    q1 = 47
    r1 = 48
    s1 = 49
    t1 = 50
    u1 = 51
    return x + y
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "long" in i.message.lower() for i in issues)

    def test_too_many_parameters(self, detector) -> None:
        """Test detection of too many parameters."""
        code = '''
def function_with_many_params(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "parameter" in i.message.lower() for i in issues)

    def test_global_variable_detection(self, detector) -> None:
        """Test detection of global variable usage."""
        code = '''
global_var = 10

def modify_global():
    global global_var
    global_var = 20
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "global" in i.message.lower() for i in issues)

    def test_bare_except_detection(self, detector) -> None:
        """Test detection of bare except clause."""
        code = '''
try:
    risky_operation()
except:
    pass
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "except" in i.message.lower() for i in issues)

    def test_broad_exception_detection(self, detector) -> None:
        """Test detection of overly broad exception handling."""
        code = '''
try:
    do_something()
except Exception:
    pass
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "exception" in i.message.lower() for i in issues)

    def test_mutable_default_argument_detection(self, detector) -> None:
        """Test detection of mutable default arguments."""
        code = '''
def function_with_mutable_default(items=[]):
    items.append(1)
    return items
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "mutable" in i.message.lower() for i in issues)

    def test_god_class_detection(self, detector) -> None:
        """Test detection of god classes."""
        code = '''
class GodClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass
'''
        issues = detector.analyze(code, "test.py")
        assert any(i.issue_type == "smell" and "method" in i.message.lower() for i in issues)

    def test_magic_number_detection(self, detector) -> None:
        """Test detection of magic numbers."""
        code = '''
x = 42
y = 3.14159
z = 999
'''
        issues = detector.analyze(code, "test.py")
        # Should have at least one magic number issue
        magic_issues = [i for i in issues if i.issue_type == "smell" and "magic" in i.message.lower()]
        assert len(magic_issues) > 0

    def test_syntax_error_handling(self, detector) -> None:
        """Test handling of syntax errors."""
        code = "def broken(\\n  invalid"
        issues = detector.analyze(code, "test.py")
        assert isinstance(issues, list)

    def test_empty_code_analysis(self, detector) -> None:
        """Test analysis of empty code."""
        issues = detector.analyze("", "test.py")
        assert isinstance(issues, list)
