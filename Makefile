.PHONY: test lint run simulate clean

test:
	python3 -m unittest discover -s tests -p "test_*.py"

lint:
	python3 -m py_compile src/cloud_agent_swarm/**/*.py

simulate:
	python3 -m cloud_agent_swarm.cli.main simulate --scenario oom_cascade

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
