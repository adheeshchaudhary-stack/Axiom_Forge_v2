import pandas as pd

from forensics.timestamp_check import check_timestamps


def run_portfolio_audit(
    csv_path: str = "data/transactions.csv", df: pd.DataFrame | None = None
) -> dict:
    """
    Run the portfolio latency audit against the given CSV file.

    Returns a dict with:
      - total_rows
      - fraud_rows
      - integrity_score
      - warning (str | None)
    """
    if df is None:
        df = pd.read_csv(csv_path)
    total_rows = len(df)
    fraud_rows = 0

    for _, row in df.iterrows():
        result = check_timestamps(
            lead_created_at=row["lead_time"],
            payment_processed_at=row["payment_time"],
        )

        if result["verdict"].startswith("FRAUD ALERT"):
            fraud_rows += 1

    integrity_score = ((total_rows - fraud_rows) / total_rows) * 100 if total_rows else 0.0

    warning = None
    if integrity_score < 95.0:
        warning = (
            "High synthetic risk detected. Recommend a 20% price hair-cut on the deal valuation."
        )

    return {
        "total_rows": total_rows,
        "fraud_rows": fraud_rows,
        "integrity_score": integrity_score,
        "warning": warning,
    }


def main():
    print("=" * 60)
    print("AXIOM FORGE TRUTH OS - SYSTEM ONLINE")
    print("=" * 60)
    print("CHRONOS-AUDIT: PORTFOLIO LATENCY AUDIT")
    print("-" * 60)

    result = run_portfolio_audit()

    print(f"Total Transactions Audited : {result['total_rows']}")
    print(f"Fraud-Flagged Transactions : {result['fraud_rows']}")
    print("-" * 60)
    print(f"PORTFOLIO INTEGRITY SCORE  : {result['integrity_score']:.2f}%")

    if result["warning"]:
        print(
            "Solution Architect Warning : "
            f"{result['warning']}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()

