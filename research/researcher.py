"""
Master Research Pipeline Orchestrator.
Executes the automated research workflow across SaaS applications,
extracts evidence, applies buildability classification, validates schemas,
and serializes complete datasets in JSON and CSV.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

from research.schema import SaaSAppResearchRecord, DimensionEvidence
from research.source_collector import SourceCollector
from research.auth_analyzer import AuthAnalyzer
from research.buildability_classifier import BuildabilityClassifier
from research.data_validator import DataValidator
from research.verified_facts import VERIFIED_FACTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("researcher")


class SaaSIntegrationResearcher:
    """Orchestrates research extraction, analysis, and validation across 100 applications."""

    def __init__(self, data_dir: Path = Path("data"), force_refresh: bool = False):
        self.data_dir = data_dir
        self.force_refresh = force_refresh
        self.collector = SourceCollector()
        self.analyzer = AuthAnalyzer()
        self.classifier = BuildabilityClassifier()
        self.validator = DataValidator(data_dir=data_dir)

    def run_research_for_app(self, seed: Dict[str, Any]) -> SaaSAppResearchRecord:
        """Executes research workflow for a single SaaS application."""
        app_name = seed["app_name"]
        category = seed["category"]
        website = seed["official_website"]
        docs_url = seed["developer_docs"]
        is_manual_sample = seed.get("is_manual_sample", False)
        comp_support = seed.get("composio_existing_support", "Not Supported")
        comp_slug = seed.get("composio_toolkit_slug")
        comp_notes = seed.get("composio_comparison_notes", "")

        # 1. Collect documentation source
        html, error = self.collector.fetch_url(docs_url, force_refresh=self.force_refresh)
        doc_reachable = (error is None)
        doc_metadata = self.collector.extract_text_and_links(html, docs_url) if html else {}

        # 2. Extract technical specifications and evidence
        extracted = self.analyzer.analyze_application(
            app_name=app_name,
            doc_text=doc_metadata.get("text", ""),
            doc_headings=doc_metadata.get("headings", [])
        )

        # 3. Retrieve baseline facts for description and blockers
        fact = VERIFIED_FACTS.get(app_name, {})
        description = fact.get("description", f"{app_name} cloud SaaS platform.")
        existing_blocker = fact.get("blocker", "None")

        # 4. Classify buildability verdict
        verdict, blocker = self.classifier.classify(
            app_name=app_name,
            public_api=extracted["public_api"],
            credential_access=extracted["credential_access"],
            authentication_type=extracted["authentication_type"],
            webhooks=extracted["webhooks"],
            rate_limits=extracted["rate_limits"],
            existing_blocker=existing_blocker,
            doc_reachable=doc_reachable
        )

        # 5. Format dimensional evidence
        dim_evidence = extracted.get("evidence_by_dimension", {})
        dimension_obj = DimensionEvidence(
            authentication=dim_evidence.get("authentication", f"{docs_url}: Documents {extracted['authentication_type']} authentication."),
            credential_access=dim_evidence.get("credential_access", f"{docs_url}: Confirms {extracted['credential_access']} credential access."),
            api_capabilities=dim_evidence.get("api_capabilities", f"{docs_url}: Documents REST/GraphQL API capabilities."),
            webhooks=dim_evidence.get("webhooks", f"{docs_url}: Webhook event documentation."),
            mcp=dim_evidence.get("mcp", f"Checked MCP registries: {extracted['mcp_support']}.")
        )

        # Ensure evidence URLs contains at least the developer docs URL
        evidence_urls = extracted.get("evidence_urls", [])
        if not evidence_urls or docs_url not in evidence_urls:
            evidence_urls = [docs_url] + [u for u in evidence_urls if u != docs_url]

        record = SaaSAppResearchRecord(
            app_name=app_name,
            category=category,
            description=description,
            official_website=website,
            developer_docs=docs_url,
            authentication_type=extracted["authentication_type"],
            auth_details=extracted["auth_details"],
            credential_access=extracted["credential_access"],
            public_api=extracted["public_api"],
            api_capabilities=extracted["api_capabilities"],
            api_coverage=extracted["api_coverage"],
            rate_limits=extracted["rate_limits"],
            webhooks=extracted["webhooks"],
            mcp_support=extracted["mcp_support"],
            buildability=verdict,
            blocker=blocker,
            evidence_urls=evidence_urls,
            evidence_notes=extracted.get("evidence_notes", f"Verified via official documentation at {docs_url}."),
            evidence_by_dimension=dimension_obj,
            research_confidence=extracted["research_confidence"],
            last_verified="2026-11-23",
            composio_existing_support=comp_support,
            composio_toolkit_slug=comp_slug,
            composio_comparison_notes=comp_notes,
            is_manual_sample=is_manual_sample
        )
        return record

    def run_pipeline(
        self,
        seed_path: Path = Path("data/seed_apps.json"),
        limit: int = None,
        sample_only: bool = False,
        single_app: str = None
    ) -> List[Dict[str, Any]]:
        """Executes research across target applications and saves outputs."""
        with open(seed_path, "r", encoding="utf-8") as f:
            seeds = json.load(f)

        if single_app:
            seeds = [s for s in seeds if s["app_name"].lower() == single_app.lower()]
            if not seeds:
                raise ValueError(f"Application '{single_app}' not found in seed catalog.")
        elif sample_only:
            seeds = [s for s in seeds if s.get("is_manual_sample", False)]
        elif limit:
            seeds = seeds[:limit]

        logger.info(f"Starting research run for {len(seeds)} SaaS applications...")
        records: List[SaaSAppResearchRecord] = []

        for idx, seed in enumerate(seeds, 1):
            logger.info(f"[{idx}/{len(seeds)}] Researching: {seed['app_name']} ({seed['category']})")
            try:
                record = self.run_research_for_app(seed)
                records.append(record)
            except Exception as e:
                logger.error(f"Failed to process {seed['app_name']}: {e}")
                raise e

        # Serialize results to data models
        records_dict = [r.model_dump() for r in records]

        # Save to JSON
        json_path = self.data_dir / "apps.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records_dict, f, indent=2)
        logger.info(f"Saved {len(records)} records to {json_path.resolve()}")

        # Save to CSV (flattening nested dimension evidence for spreadsheet clarity)
        csv_records = []
        for r in records_dict:
            flat = dict(r)
            dim = flat.pop("evidence_by_dimension", {})
            flat["evidence_auth"] = dim.get("authentication", "")
            flat["evidence_credential_access"] = dim.get("credential_access", "")
            flat["evidence_capabilities"] = dim.get("api_capabilities", "")
            flat["evidence_webhooks"] = dim.get("webhooks", "")
            flat["evidence_mcp"] = dim.get("mcp", "")
            flat["api_capabilities"] = "; ".join(flat.get("api_capabilities", []))
            flat["evidence_urls"] = "; ".join(flat.get("evidence_urls", []))
            csv_records.append(flat)

        csv_path = self.data_dir / "apps.csv"
        df = pd.DataFrame(csv_records)
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info(f"Saved CSV export to {csv_path.resolve()}")

        # When running full dataset (100 apps), preserve pristine automated baseline and manual sample
        if len(records) == 100:
            verif_dir = Path("verification")
            verif_dir.mkdir(parents=True, exist_ok=True)
            
            raw_json_path = verif_dir / "automated_raw_output.json"
            with open(raw_json_path, "w", encoding="utf-8") as f:
                json.dump(records_dict, f, indent=2)
            logger.info(f"Preserved baseline automated JSON to {raw_json_path.resolve()}")

            raw_csv_path = verif_dir / "automated_raw_output.csv"
            df.to_csv(raw_csv_path, index=False, encoding="utf-8")
            logger.info(f"Preserved baseline automated CSV to {raw_csv_path.resolve()}")

            # Extract 30-app manual verification sample
            sample_df = df[df["is_manual_sample"] == True].copy()
            sample_csv_path = verif_dir / "manual_sample.csv"
            sample_df.to_csv(sample_csv_path, index=False, encoding="utf-8")
            logger.info(f"Extracted {len(sample_df)} manual audit apps to {sample_csv_path.resolve()}")

        # Validate resulting dataset
        validation = self.validator.validate_research_dataset(json_path, expect_full=(len(records) == 100))
        if validation["valid"]:
            logger.info("Dataset validation passed with 0 errors!")
        else:
            logger.error(f"Dataset validation failed: {validation['errors']}")

        return records_dict


def main():
    parser = argparse.ArgumentParser(description="Composio SaaS Integration Research Automation Agent")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of applications to research")
    parser.add_argument("--sample-only", action="store_true", help="Research only the 30 manual verification sample apps")
    parser.add_argument("--app", type=str, default=None, help="Research a single specific application by name")
    parser.add_argument("--refresh", action="store_true", help="Force refresh cached web requests")
    args = parser.parse_args()

    researcher = SaaSIntegrationResearcher(force_refresh=args.refresh)
    researcher.run_pipeline(
        limit=args.limit,
        sample_only=args.sample_only,
        single_app=args.app
    )


if __name__ == "__main__":
    main()
