"""Step 0: run the full analysis and cache the results (outputs/results/*, outputs/cache/results.pkl)."""
from _bootstrap import run_and_cache

if __name__ == "__main__":
    run_and_cache()
    print("Analysis complete. Headline numbers in outputs/results/headline.json")
