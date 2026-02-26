def check_timestamps(lead_created_at, payment_processed_at):
    """
    Compare two timestamps and flag suspiciously low latency.

    Parameters
    ----------
    lead_created_at : float
        Timestamp (e.g. seconds) when the lead was created.
    payment_processed_at : float
        Timestamp (e.g. seconds) when the payment was processed.

    Returns
    -------
    dict
        Contains a 'verdict' string and a 'remediation_tip' string.
    """
    latency = abs(payment_processed_at - lead_created_at)

    if latency < 0.5:
        return {
            "verdict": "FRAUD ALERT: Zero-Latency Paradox",
            "remediation_tip": (
                "Internal systems suggest this is likely bot-generated traffic. "
                "Investigate the Lead Source IP."
            ),
        }

    return {
        "verdict": "Verification Successful",
        "remediation_tip": "Metric within healthy human-interaction bounds.",
    }

