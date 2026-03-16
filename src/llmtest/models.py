"""Core data models for llmtest."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TestType(str, Enum):
    """Supported test types."""

    GROUNDING = "grounding"
    INJECTION = "injection"
    SAFETY = "safety"
    REGRESSION = "regression"


class AgentType(str, Enum):
    """Supported agent types."""

    PROMPT = "prompt"


class TestStatus(str, Enum):
    """Test execution status."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


class AgentConfig(BaseModel):
    """Agent configuration."""

    type: AgentType = AgentType.PROMPT
    system_prompt: str = Field(..., min_length=1)


class TestCase(BaseModel):
    """Individual test case definition."""

    id: str = Field(..., min_length=1)
    type: TestType
    input: str = Field(..., min_length=1)

    # Grounding test fields
    must_include: Optional[List[str]] = None
    must_not_include: Optional[List[str]] = None
    expected_behavior: Optional[str] = None

    # Injection/Safety test fields
    must_refuse: Optional[bool] = None

    @field_validator("must_include", "must_not_include")
    @classmethod
    def validate_phrase_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate phrase lists are non-empty if provided."""
        if v is not None and len(v) == 0:
            raise ValueError("Phrase lists must contain at least one item if specified")
        return v


class TestConfig(BaseModel):
    """Complete test configuration loaded from YAML."""

    provider: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    agent: AgentConfig
    knowledge_base: Optional[List[str]] = None
    tests: List[TestCase] = Field(..., min_items=1)

    @field_validator("tests")
    @classmethod
    def validate_test_ids_unique(cls, v: List[TestCase]) -> List[TestCase]:
        """Ensure all test IDs are unique."""
        ids = [test.id for test in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Test IDs must be unique")
        return v


class EvaluatorResult(BaseModel):
    """Result from a single evaluator."""

    passed: bool
    details: Dict[str, Any] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)


class TestResult(BaseModel):
    """Result of a single test execution."""

    test_id: str
    test_type: TestType
    status: TestStatus
    input: str
    response: Optional[str] = None
    evaluator_result: Optional[EvaluatorResult] = None
    error_message: Optional[str] = None


class TestSuiteResult(BaseModel):
    """Results from running a complete test suite."""

    provider: str
    model: str
    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    test_results: List[TestResult]

    @property
    def pass_rate(self) -> float:
        """Calculate overall pass rate."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100.0

    def pass_rate_by_type(self, test_type: TestType) -> float:
        """Calculate pass rate for a specific test type."""
        type_results = [r for r in self.test_results if r.test_type == test_type]
        if not type_results:
            return 0.0
        passed_count = sum(1 for r in type_results if r.status == TestStatus.PASS)
        return (passed_count / len(type_results)) * 100.0


class ComparisonResult(BaseModel):
    """Result of comparing two test runs."""

    test_id: str
    changed: bool
    severity: str  # "UNCHANGED", "LOW", "HIGH", "CRITICAL"
    baseline_response: str
    candidate_response: str
    reason: Optional[str] = None


class TestSuite(BaseModel):
    """Programmatic test suite definition."""

    config: TestConfig
    docs_content: Dict[str, str] = Field(default_factory=dict)
