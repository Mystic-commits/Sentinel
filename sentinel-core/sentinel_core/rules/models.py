from pydantic import BaseModel


class RuleCondition(BaseModel):
    """A single condition for a rule match."""

    extension: str | None = None  # e.g. ".pdf"
    name_contains: str | None = None  # e.g. "invoice"
    regex_pattern: str | None = None  # e.g. "^[0-9]{4}-.*"
    min_size_bytes: int | None = None
    max_size_bytes: int | None = None


class Rule(BaseModel):
    """A classification rule."""

    name: str
    category: str  # e.g. "Documents/Invoices"
    conditions: list[RuleCondition]  # ANY condition match triggers rule? Or ALL?
    # Logic: A rule usually has one set of criteria.
    # Let's say IF extension=.pdf AND name_contains=invoice.
    # So these fields in RuleCondition should be ANDed.
    # If we need OR, we make multiple Rules.
    priority: int = 100  # Lower number = Higher priority


class RuleMatchResult(BaseModel):
    """Result of a classification attempt."""

    file_path: str
    matched_rule: str | None = None
    suggested_category: str | None = None
    confidence: float = 0.0
    reason: str = "No rule matched"
