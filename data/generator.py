import random
from pathlib import Path

import pandas as pd


def generate_transactions_csv(
    output_path: Path | None = None,
    num_rows: int = 100,
    fraud_ratio: float = 0.1,
) -> Path:
    """
    Generate a synthetic M&A transactions CSV.

    Parameters
    ----------
    output_path : Path, optional
        Full path to the CSV file. Defaults to `data/transactions.csv` in
        the project root if not provided.
    num_rows : int
        Total number of transaction rows to generate.
    fraud_ratio : float
        Approximate fraction of rows that should exhibit the
        "Fraud Paradox" (0.1 second gap).

    Returns
    -------
    Path
        The path to the written CSV file.
    """
    if output_path is None:
        data_dir = Path(__file__).resolve().parent
        output_path = data_dir / "transactions.csv"

    rows = []
    for i in range(1, num_rows + 1):
        # Base lead time (e.g., seconds since some arbitrary epoch)
        lead_time = float(i * 100)

        # Decide whether this row is a "fraud paradox" row
        if random.random() < fraud_ratio:
            gap = 0.1
        else:
            gap = random.uniform(2.0, 10.0)

        payment_time = lead_time + gap

        rows.append(
            {
                "transaction_id": i,
                "lead_time": lead_time,
                "payment_time": payment_time,
            }
        )

    df = pd.DataFrame(rows, columns=["transaction_id", "lead_time", "payment_time"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return output_path


if __name__ == "__main__":
    csv_path = generate_transactions_csv()
    print(f"Generated synthetic transactions CSV at: {csv_path}")

