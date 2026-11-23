"""
Automated validation suite for SaaS Integration Research dataset.
Verifies seed lists, schema conformance, uniqueness, category balance,
manual sample stratification, and evidence integrity.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from pydantic import ValidationError

from research.schema import (
    APPROVED_CATEGORIES,
    SaaSAppSeed,
    SaaSAppResearchRecord,
)


class DataValidator:
    """Validates SaaS datasets at various lifecycle stages."""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir

    def validate_seed_catalog(self, seed_path: Path = None) -> Dict[str, Any]:
        """Validates the 100-app seed catalog."""
        if seed_path is None:
            seed_path = self.data_dir / "seed_apps.json"

        errors = []
        warnings = []

        if not seed_path.exists():
            return {"valid": False, "errors": [f"File not found: {seed_path}"], "warnings": []}

        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return {"valid": False, "errors": [f"Malformed JSON in {seed_path}: {e}"], "warnings": []}

        if not isinstance(data, list):
            return {"valid": False, "errors": [f"Root of {seed_path} must be a list."], "warnings": []}

        # 1. Total Count Check
        if len(data) != 100:
            errors.append(f"Expected exactly 100 applications, found {len(data)}.")

        # 2. Uniqueness Check
        seen_names = {}
        for idx, item in enumerate(data):
            name = item.get("app_name", "").strip().lower()
            if not name:
                errors.append(f"Item #{idx} has missing or empty app_name.")
            elif name in seen_names:
                errors.append(f"Duplicate application name detected: '{item.get('app_name')}' (first seen at index {seen_names[name]}).")
            else:
                seen_names[name] = idx

        # 3. Category Distribution Check
        cat_counts = {cat: 0 for cat in APPROVED_CATEGORIES}
        for item in data:
            cat = item.get("category")
            if cat in cat_counts:
                cat_counts[cat] += 1
            else:
                errors.append(f"Unrecognized category '{cat}' for app '{item.get('app_name')}'.")

        for cat, count in cat_counts.items():
            if count != 10:
                errors.append(f"Category '{cat}' must have exactly 10 apps; found {count}.")

        # 4. Manual Verification Sample Check (Stratified: 3 per category = 30 total)
        sample_counts = {cat: 0 for cat in APPROVED_CATEGORIES}
        total_samples = 0
        for item in data:
            if item.get("is_manual_sample", False):
                total_samples += 1
                cat = item.get("category")
                if cat in sample_counts:
                    sample_counts[cat] += 1

        if total_samples != 30:
            errors.append(f"Total manual verification samples must be 30; found {total_samples}.")

        for cat, count in sample_counts.items():
            if count != 3:
                errors.append(f"Category '{cat}' has {count} manual samples; expected exactly 3.")

        # 5. Schema Validation & URL Format
        for idx, item in enumerate(data):
            try:
                seed_obj = SaaSAppSeed(**item)
                # Composio slug consistency
                if seed_obj.composio_existing_support == "Official Toolkit" and not seed_obj.composio_toolkit_slug:
                    errors.append(f"App '{seed_obj.app_name}' is marked 'Official Toolkit' but missing 'composio_toolkit_slug'.")
            except ValidationError as ve:
                for err in ve.errors():
                    errors.append(f"Item #{idx} ({item.get('app_name')}): {err['loc']} -> {err['msg']}")

        is_valid = len(errors) == 0
        return {
            "valid": is_valid,
            "total_apps": len(data),
            "total_manual_samples": total_samples,
            "categories_evaluated": len(cat_counts),
            "errors": errors,
            "warnings": warnings
        }

    def validate_research_dataset(self, dataset_path: Path = None, expect_full: bool = True) -> Dict[str, Any]:
        """Validates the compiled research dataset against full schema rules."""
        if dataset_path is None:
            dataset_path = self.data_dir / "apps.json"

        errors = []
        warnings = []

        if not dataset_path.exists():
            return {"valid": False, "errors": [f"File not found: {dataset_path}"], "warnings": []}

        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return {"valid": False, "errors": [f"Failed to read JSON: {e}"], "warnings": []}

        if expect_full and len(data) != 100:
            errors.append(f"Research dataset contains {len(data)} items; expected 100.")

        for idx, item in enumerate(data):
            try:
                record = SaaSAppResearchRecord(**item)
                # Check dimensional evidence completeness
                dim = record.evidence_by_dimension
                for dim_name, dim_val in [
                    ("authentication", dim.authentication),
                    ("credential_access", dim.credential_access),
                    ("api_capabilities", dim.api_capabilities),
                    ("webhooks", dim.webhooks),
                    ("mcp", dim.mcp),
                ]:
                    if not dim_val or len(dim_val.strip()) < 5:
                        errors.append(f"App '{record.app_name}': dimension evidence '{dim_name}' is empty or too short.")
            except ValidationError as ve:
                for err in ve.errors():
                    errors.append(f"Record #{idx} ({item.get('app_name')}): {err['loc']} -> {err['msg']}")

        return {
            "valid": len(errors) == 0,
            "total_records": len(data),
            "errors": errors,
            "warnings": warnings
        }


def run_cli():
    parser = argparse.ArgumentParser(description="Validate SaaS Integration Research Datasets")
    parser.add_argument("--mode", choices=["seed", "dataset", "all"], default="seed", help="Validation mode")
    parser.add_argument("--seed-file", type=str, default="data/seed_apps.json", help="Path to seed file")
    parser.add_argument("--dataset-file", type=str, default="data/apps.json", help="Path to full dataset file")
    args = parser.parse_args()

    validator = DataValidator()
    overall_valid = True

    if args.mode in ["seed", "all"]:
        print(f"\n--- Validating Seed Catalog: {args.seed_file} ---")
        res = validator.validate_seed_catalog(Path(args.seed_file))
        if res["valid"]:
            print(f"SUCCESS: Seed catalog is valid! {res['total_apps']} unique apps, {res['total_manual_samples']} manual verification samples across {res['categories_evaluated']} categories.")
        else:
            print(f"FAILED: Seed catalog validation failed with {len(res['errors'])} errors:")
            for err in res["errors"]:
                print(f"  ✗ {err}")
            overall_valid = False

    if args.mode in ["dataset", "all"]:
        print(f"\n--- Validating Full Research Dataset: {args.dataset_file} ---")
        res = validator.validate_research_dataset(Path(args.dataset_file))
        if res["valid"]:
            print(f"SUCCESS: Research dataset is valid! {res['total_records']} verified records.")
        else:
            print(f"FAILED: Dataset validation failed with {len(res['errors'])} errors:")
            for err in res["errors"]:
                print(f"  ✗ {err}")
            overall_valid = False

    sys.exit(0 if overall_valid else 1)


if __name__ == "__main__":
    run_cli()
