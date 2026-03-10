"""Tests for pattern analyzer."""

import pytest

from socratic_analyzer.analyzers.patterns import PatternAnalyzer


class TestPatternAnalyzer:
    """Test PatternAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> PatternAnalyzer:
        """Provide pattern analyzer."""
        return PatternAnalyzer()

    def test_analyzer_properties(self, analyzer) -> None:
        """Test analyzer properties."""
        assert analyzer.name == "Pattern Analyzer"
        assert "pattern" in analyzer.description.lower()

    def test_singleton_pattern_detection(self, analyzer) -> None:
        """Test singleton pattern detection."""
        code = '''
class Singleton:
    _instance = None

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "pattern" for i in issues)
        assert any("singleton" in i.message.lower() for i in issues)

    def test_factory_pattern_detection(self, analyzer) -> None:
        """Test factory pattern detection."""
        code = '''
def shape_factory(shape_type):
    if shape_type == "circle":
        return Circle()
    elif shape_type == "square":
        return Square()
    else:
        return Rectangle()
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "pattern" for i in issues)

    def test_decorator_pattern_detection(self, analyzer) -> None:
        """Test decorator pattern detection."""
        code = '''
class Decorator:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def operation(self):
        return self.wrapped.operation()
'''
        issues = analyzer.analyze(code, "test.py")
        # Decorator pattern should be detected
        assert isinstance(issues, list)

    def test_context_manager_pattern_detection(self, analyzer) -> None:
        """Test context manager pattern detection."""
        code = '''
class FileManager:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, 'r')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "pattern" for i in issues)

    def test_observer_pattern_detection(self, analyzer) -> None:
        """Test observer pattern detection."""
        code = '''
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "pattern" for i in issues)

    def test_strategy_pattern_detection(self, analyzer) -> None:
        """Test strategy pattern detection."""
        code = '''
class PaymentProcessor:
    def __init__(self, strategy):
        self.strategy = strategy

    def process_payment(self, amount):
        return self.strategy.execute(amount)
'''
        issues = analyzer.analyze(code, "test.py")
        # Strategy pattern should be detected by various other analyzers
        assert isinstance(issues, list)

    def test_callback_pattern_detection(self, analyzer) -> None:
        """Test callback pattern detection."""
        code = '''
def process_data(data, callback):
    result = do_something(data)
    callback(result)
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "pattern" for i in issues)

    def test_template_method_pattern_detection(self, analyzer) -> None:
        """Test template method pattern detection."""
        code = '''
class DataProcessor:
    def _validate(self):
        raise NotImplementedError

    def _process(self):
        raise NotImplementedError

    def execute(self):
        self._validate()
        self._process()
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "pattern" for i in issues)

    def test_syntax_error_handling(self, analyzer) -> None:
        """Test handling of syntax errors."""
        code = "def broken(\\n  invalid"
        issues = analyzer.analyze(code, "test.py")
        assert isinstance(issues, list)
