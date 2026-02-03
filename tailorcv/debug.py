from pathlib import Path

from loaders.job_loader import load_job


def main():
    # CHANGE THIS PATH to any job.txt you want to test
    job_path = Path("tailorcv/examples/jobs/sample_job.txt")

    job = load_job(job_path)

    print("\n" + "=" * 80)
    print("JOB LOADER DEBUG OUTPUT")
    print("=" * 80)

    print(f"\nJob file: {job_path}")
    print(f"Raw text length:     {len(job.raw_text)} characters")
    print(f"Cleaned text length: {len(job.cleaned_text)} characters")

    reduction = 100 * (1 - len(job.cleaned_text) / max(len(job.raw_text), 1))
    print(f"Reduction:           {reduction:.1f}%")

    print("\nTop extracted keywords:")
    for i, kw in enumerate(job.keywords, start=1):
        print(f"{i:2d}. {kw}")

    print("\nCleaned text preview (first 500 chars):")
    print("-" * 80)
    print(job.cleaned_text[:500])
    print("-" * 80)


if __name__ == "__main__":
    main()
