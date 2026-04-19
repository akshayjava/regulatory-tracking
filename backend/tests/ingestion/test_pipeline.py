import pytest
import os
import tempfile
from unittest.mock import MagicMock
from backend.ingestion.pipeline import IngestionPipeline

def test_source_pipeline_error_handling():
    fd, path = tempfile.mkstemp()
    os.close(fd)

    try:
        pipeline = IngestionPipeline(db_path=path)

        # Create a mock source that raises an exception on fetch
        mock_source = MagicMock()
        mock_source.fetch.side_effect = Exception("Intentional error for testing")

        # Replace the congress source with our mock
        pipeline.sources["congress"] = mock_source

        # Run the pipeline just for this source
        stats = pipeline.run("congress")

        # Verify the error was caught and recorded
        assert stats["errors"] == 1
        assert stats["total_processed"] == 0
        assert stats["new"] == 0
    finally:
        os.unlink(path)

def test_source_pipeline_continues_on_error():
    fd, path = tempfile.mkstemp()
    os.close(fd)

    try:
        pipeline = IngestionPipeline(db_path=path)

        # Mock source 1: fails
        mock_failing_source = MagicMock()
        mock_failing_source.fetch.side_effect = Exception("Intentional error")

        # Mock source 2: succeeds
        mock_succeeding_source = MagicMock()
        mock_succeeding_source.fetch.return_value = [
            {"regulation_id": "test-1", "title": "Test Reg 1", "agency": "Test Agency", "source": "congress"}
        ]

        # Replace sources in pipeline
        pipeline.sources = {
            "failing": mock_failing_source,
            "succeeding": mock_succeeding_source
        }

        # Run the pipeline for all sources
        stats = pipeline.run()

        # Verify the error was caught
        assert stats["errors"] == 1

        # Verify the succeeding source was processed
        assert stats["total_processed"] == 1
        assert stats["new"] == 1

    finally:
        os.unlink(path)
