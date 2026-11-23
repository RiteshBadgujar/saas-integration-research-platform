"""
Integration Buildability Classifier.
Applies the 5-verdict framework to classify SaaS integration feasibility,
concrete blockers, and technical risks for LLM toolkits.
"""

from typing import Dict, Any, Tuple


class BuildabilityClassifier:
    """Evaluates SaaS applications against the Composio integration feasibility rubric."""

    def classify(
        self,
        app_name: str,
        public_api: str,
        credential_access: str,
        authentication_type: str,
        webhooks: str,
        rate_limits: str,
        existing_blocker: str = "",
        doc_reachable: bool = True
    ) -> Tuple[str, str]:
        """
        Returns: (buildability_verdict, concrete_blocker)
        Verdicts:
          - "Buildable"
          - "Buildable with limitations"
          - "Partner-dependent"
          - "Not currently buildable"
          - "Insufficient evidence"
        """
        # Case 1: Inaccessible documentation
        if not doc_reachable and public_api != "Yes":
            return "Insufficient evidence", "Documentation unreachable and public API availability unconfirmed."

        # Case 2: No public API
        if public_api == "No":
            return "Not currently buildable", "No public API or developer endpoints exposed."

        # Case 3: Partner-gated credentials or enterprise barrier
        if credential_access == "Partner-gated":
            blocker = existing_blocker if existing_blocker else "Requires enterprise contract or formal partner certification for API access."
            return "Partner-dependent", blocker

        # Case 4: Approval required or notable limitations
        limitations = []
        if credential_access == "Approval-required":
            limitations.append("Requires manual vendor approval or app store review for distribution.")

        if webhooks == "Not supported":
            limitations.append("Lacks native webhooks; requires polling for event-driven workflows.")

        # Rate limit checks for severe constraints
        if any(term in rate_limits.lower() for term in ["1 req/", "2 req/", "3 req/sec", "5 req/sec", "leaky bucket"]):
            limitations.append(f"Restricted rate limits ({rate_limits}) restrict rapid agent execution.")

        if existing_blocker and existing_blocker.lower() not in ["none", "none;"]:
            # Check if blocker indicates limitations
            limitations.append(existing_blocker)

        # If there are meaningful limitations, classify as "Buildable with limitations"
        if limitations:
            # Consolidate blocker string
            blocker_desc = "; ".join(dict.fromkeys(limitations)) # deduplicate while preserving order
            return "Buildable with limitations", blocker_desc

        # Case 5: Fully self-serve, active public API with no major blockers
        if public_api == "Yes" and credential_access == "Self-serve":
            return "Buildable", "None"

        # Fallback / Unclear
        if credential_access == "Unclear":
            return "Insufficient evidence", "Credential access terms and developer documentation unclear."

        return "Buildable with limitations", existing_blocker or "Minor capability or permission limitations apply."
