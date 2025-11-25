from typing import List, Literal
from pydantic import BaseModel, Field


class MajorIssue(BaseModel):
    issue_type: Literal["Accuracy", "Structure", "Tone", "Recurring"] = Field(
        ...,
        description="The category of the issue. Use 'Recurring' only if the issue appears in past_feedback_context.",
    )
    description: str = Field(
        ...,
        description="A detailed explanation of why this is an issue and its impact on the reader.",
    )
    evidence: str = Field(
        ...,
        description="A URL to a search result verifying the correction, or a reference to specific past feedback.",
    )


class LineByLineComment(BaseModel):
    original_text: str = Field(
        ...,
        description="The exact quote from the blog post that triggered this comment.",
    )
    comment: str = Field(
        ...,
        description="The specific feedback, correction, or suggestion for this line.",
    )


class PeerReviewReport(BaseModel):
    summary: str = Field(
        ...,
        description="A brief, 2-3 sentence high-level overview of the article's quality, strengths, and weaknesses.",
    )
    confidential_recommendation: str = Field(
        ...,
        description="A tailored note to the editor. Common examples: 'Publish with minor edits', 'Reject', 'Needs major rework'.",
    )
    major_issues: List[MajorIssue] = Field(
        default_factory=list,
        description="A list of critical issues that must be addressed before publication.",
    )
    minor_issues: List[str] = Field(
        default_factory=list,
        description="A list of smaller nits, such as grammar errors, minor flow issues, or stylistic preferences.",
    )
    line_by_line_comments: List[LineByLineComment] = Field(
        default_factory=list,
        description="Granular feedback mapped to specific sentences or paragraphs in the text.",
    )
