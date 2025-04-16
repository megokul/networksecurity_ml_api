from datetime import datetime, timezone

# Internal module-level cache to ensure the timestamp is consistent across the entire pipeline
_timestamp_cache: str = None

def get_shared_utc_timestamp(fmt: str = "%Y_%m_%dT%H_%M_%SZ") -> str:
    """
    Returns a consistent, cached UTC timestamp for the current pipeline run.

    This function guarantees that:
    - The timestamp is generated only once.
    - All modules (logger, config, etc.) use the exact same value.
    - The format is clean and safe for filenames, directories, and versioning.

    Args:
        fmt (str): Optional datetime format string.
                   Default: 'YYYY_MM_DDTHH_MM_SSZ' (e.g., '2025_04_16T17_45_02Z')

    Returns:
        str: UTC timestamp string formatted per the provided format.
    """
    global _timestamp_cache
    if _timestamp_cache is None:
        _timestamp_cache = datetime.now(timezone.utc).strftime(fmt)
    return _timestamp_cache
