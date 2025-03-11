.PHONY: run_case1 run_case2 all

# Test Case 1
QUERY1 := llm
MAX_RESULTS1 := 30

# Test Case 2
QUERY2 := quantum
MAX_RESULTS2 := 10

run_case1:
	python3 ../arxiv2tex.py --query $(QUERY1) --max_results $(MAX_RESULTS1) --prefix llm --engine latex

run_case2:
	python3 ../arxiv2tex.py --query $(QUERY2) --max_results $(MAX_RESULTS2) --prefix quantum --cls ltjsarticle --translate ja

all: run_case1 run_case2