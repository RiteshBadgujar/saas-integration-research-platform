"""
Data schema and validation models for SaaS Integration Research.
Enforces strict contracts, enums, evidence anchoring, and Composio parity checks.
"""

from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, HttpUrl, Field, field_validator, model_validator

# Approved 10 Categories
APPROVED_CATEGORIES = [
    "CRM and Sales",
    "Project Management",
    "Communication and Collaboration",
    "Marketing Automation",
    "Customer Support",
    "Finance and Accounting",
    "HR and Recruitment",
    "Developer Tools",
    "Analytics and Business Intelligence",
    "Storage and Document Management"
]

# Allowed Enums
AuthenticationType = Literal[
    "OAuth 2.0",
    "API Key",
    "Personal Access Token (PAT)",
    "Basic Auth",
    "Bearer JWT",
    "Hybrid",
    "None / Unknown"
]

CredentialAccess = Literal[
    "Self-serve",
    "Approval-required",
    "Partner-gated",
    "Unclear"
]

PublicApi = Literal["Yes", "No", "Limited"]

ApiCoverage = Literal["Broad", "Moderate", "Limited", "Unknown"]

WebhooksSupport = Literal["Supported", "Not supported", "Unknown"]

MCPSupport = Literal[
    "Official MCP",
    "Third-party MCP",
    "Not Found in Checked Sources",
    "Unknown"
]

BuildabilityVerdict = Literal[
    "Buildable",
    "Buildable with limitations",
    "Partner-dependent",
    "Not currently buildable",
    "Insufficient evidence"
]

ResearchConfidence = Literal["High", "Medium", "Low"]

ComposioSupport = Literal[
    "Official Toolkit",
    "Community / Experimental",
    "Not Supported"
]


class DimensionEvidence(BaseModel):
    """Granular evidence anchoring for distinct operational dimensions."""
    authentication: str = Field(..., description="Evidence URL and excerpt confirming authentication method")
    credential_access: str = Field(..., description="Evidence URL and excerpt confirming credential self-serve or gating")
    api_capabilities: str = Field(..., description="Evidence URL and excerpt confirming primary API endpoints and operations")
    webhooks: str = Field(..., description="Evidence URL and excerpt confirming webhook event notifications")
    mcp: str = Field(..., description="Evidence URL and notes confirming Model Context Protocol status")


class SaaSAppSeed(BaseModel):
    """Seed definition for initial catalog intake."""
    app_name: str
    category: str
    official_website: str
    developer_docs: str
    is_manual_sample: bool = False
    composio_existing_support: ComposioSupport = "Not Supported"
    composio_toolkit_slug: Optional[str] = None
    composio_comparison_notes: str = ""

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in APPROVED_CATEGORIES:
            raise ValueError(f"Category '{v}' not in approved list: {APPROVED_CATEGORIES}")
        return v

    @field_validator("official_website", "developer_docs")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(f"URL must start with http:// or https://: {v}")
        return v


class SaaSAppResearchRecord(BaseModel):
    """Complete verified research record for a SaaS application."""
    app_name: str = Field(..., min_length=1)
    category: str
    description: str = Field(..., min_length=10)
    official_website: str
    developer_docs: str
    authentication_type: AuthenticationType
    auth_details: str = Field(..., min_length=5)
    credential_access: CredentialAccess
    public_api: PublicApi
    api_capabilities: List[str] = Field(default_factory=list)
    api_coverage: ApiCoverage
    rate_limits: str
    webhooks: WebhooksSupport
    mcp_support: MCPSupport
    buildability: BuildabilityVerdict
    blocker: str
    evidence_urls: List[str] = Field(..., min_length=1)
    evidence_notes: str = Field(..., min_length=10)
    evidence_by_dimension: DimensionEvidence
    research_confidence: ResearchConfidence
    last_verified: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    composio_existing_support: ComposioSupport
    composio_toolkit_slug: Optional[str] = None
    composio_comparison_notes: str = ""
    is_manual_sample: bool = False

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in APPROVED_CATEGORIES:
            raise ValueError(f"Category '{v}' is not recognized.")
        return v

    @field_validator("official_website", "developer_docs")
    @classmethod
    def validate_urls(cls, v: str) -> str:
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(f"Invalid URL: {v}")
        return v

    @field_validator("evidence_urls")
    @classmethod
    def validate_evidence_urls(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one evidence URL is required.")
        for url in v:
            if not (url.startswith("http://") or url.startswith("https://")):
                raise ValueError(f"Evidence URL must be a valid HTTP/HTTPS URL: {url}")
        return v

    @model_validator(mode="after")
    def validate_buildability_consistency(self):
        # Enforce logical consistency between credential access, public API, and buildability
        if self.public_api == "No" and self.buildability == "Buildable":
            raise ValueError(f"Inconsistent state: public_api is No, but buildability is Buildable for {self.app_name}")
        if self.credential_access == "Partner-gated" and self.buildability == "Buildable":
            raise ValueError(f"Inconsistent state: credential_access is Partner-gated, so buildability cannot be unconditionally 'Buildable' for {self.app_name}")
        return self
