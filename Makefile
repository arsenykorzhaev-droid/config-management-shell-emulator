.PHONY: run test clean

run:
 python src/main.py

test:
 python -m unittest discover tests -v

clean:
 find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true