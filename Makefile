.PHONY: help lint format format-check test debug generate

help:
	@echo "Targets:"
	@echo "  lint          Run Ruff lint checks"
	@echo "  format        Format code with Ruff"
	@echo "  format-check  Check formatting with Ruff"
	@echo "  test          Run pytest"
	@echo "  debug         Run TailorCV debug pipeline"
	@echo "  generate      Run TailorCV generate (uses example inputs)"

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

test:
	pytest

debug:
	python -m tailorcv debug

generate:
	python -m tailorcv generate \
		--profile tailorcv/examples/sample_input_profile.yaml \
		--job tailorcv/examples/jobs/sample_job.txt \
		--selection tailorcv/examples/llm_selection_example.json \
		--out /tmp/rendercv_out.yaml
