
from latency_bench.benchmark import Benchmark

def main():
    benchmark = Benchmark()
    benchmark.run_all_with_cprofile()
    # Iterate through each .prof file
    benchmark.process_prof_files()

    benchmark.save_results()

if __name__ == "__main__":
    main()