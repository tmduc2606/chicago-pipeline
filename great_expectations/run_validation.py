"""Run Great Expectations validation on Bronze or Silver data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from great_expectations.core import ExpectationSuite
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import FileDataContext


def run_validation(
    data_path: str,
    suite_name: str = "chicago_crime_bronze",
    checkpoint_name: str = "bronze_checkpoint",
) -> bool:
    context = FileDataContext(context_root_dir=str(Path(__file__).resolve().parents[2]))

    batch_request = RuntimeBatchRequest(
        datasource_name="spark_s3",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="chicago_crime",
        runtime_parameters={"path": data_path},
        batch_identifiers={"id": "validation_batch"},
    )

    result = context.run_checkpoint(
        checkpoint_name=checkpoint_name,
        batch_request=batch_request,
        run_name=f"run_{suite_name}",
    )

    success = result.success
    stats = result.to_json_dict()

    report_path = Path(__file__).resolve().parents[2] / "great_expectations" / "reports" / f"{suite_name}_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)

    if success:
        print(f"VALIDATION PASSED: {suite_name}")
    else:
        print(f"VALIDATION FAILED: {suite_name}")
        for run_result in result.run_results.values():
            for validation_result in run_result.validation_result.results:
                if not validation_result.success:
                    print(f"  FAIL: {validation_result.expectation_config.expectation_type}")
                    print(f"        {validation_result.result}")

    return success


if __name__ == "__main__":
    data_path = sys.argv[1] if len(sys.argv) > 1 else "s3a://lake/bronze/chicago_crime"
    suite = sys.argv[2] if len(sys.argv) > 2 else "chicago_crime_bronze"
    checkpoint = sys.argv[3] if len(sys.argv) > 3 else "bronze_checkpoint"

    ok = run_validation(data_path, suite, checkpoint)
    sys.exit(0 if ok else 1)
