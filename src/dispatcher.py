"""takes data/data_n.html, divide it into some chunks,
each chunk get its own thread and each thread runs it through parse.py.
parsed data will be keep in memory and will be written to database
it also logs the infos
"""

import sys
import math
import os
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from shared.configured_logger import logger
from parser import parse_korupedia_detail
from result.result import Err, Ok


log = logger.bind(component="dispatcher")

if sys._is_gil_enabled():  # ty: ignore
    logger.warning("GIL is enabled, might not get the best performance")


def _cpu_count() -> int:
    # the fuck do you mean by int | None lol
    c = os.cpu_count()
    if not c:
        return 0

    return c


def get_data_chunk(data_dir, chunk_size: int | None = None) -> list[list[Path]] | None:
    """Splits files inside a directory into smaller sublists (chunks).

    scans the provided directory, retrieves all immediate filesystem entries, and partitions them into batches.
    The chunk size used for slicing, if not provided, will take machine cpu count and divided by two, otherwise will
    batch accordingly to the size provided

    Args:
        data_dir: The path or string path to the directory containing files
            to partition into chunks.
        chunk_size: if not provided, will take machine cpu count and be divided by two

    Returns:
        A nested list of ``Path`` objects where each inner list represents
        a processing chunk, or ``None`` if validation fails or the directory
        does not exist.
    """
    ncpu = _cpu_count()
    cs = chunk_size if chunk_size else (ncpu // 2)

    if chunk_size == 0:
        log.error(
            "chunk_size cannot be zero, either misinput or program cannot get cpu count"
        )
        return None

    d = Path(data_dir)
    if not d.is_dir():
        log.error("data_dir provided is not correct")
        log.info("try using absolute path")
        return None

    items = list(d.iterdir())
    if len(items) == 0:
        log.error("no items provided")
        return None

    cs = math.ceil(len(items) / cs)

    return [items[i : i + cs] for i in range(0, len(items), cs)]


def _process_batch_worker(batch: list[Path]) -> list[dict[str, str]]:
    """Processes all items inside a single chunk sequentially.

    Runs natively in parallel with other batch workers on a GIL-free runtime.
    """
    worker_logger = logger.bind(
        worker_size=len(batch),
        component="worker",
    )

    worker_logger.info("batch worker started")

    success = 0
    failed = 0
    collected: list[dict[str, str]] = []

    for file_path in batch:
        file_logger = worker_logger.bind(file=str(file_path), component="inside_worker")

        match parse_korupedia_detail(file_path):
            case Ok(data):
                success += 1
                collected.append(data)

            case Err(e):
                file_logger.exception(
                    "Failed processing file",
                )
                failed += 1

    worker_logger.info(
        "batch worker completed",
        success=success,
        failed=failed,
    )

    return collected


# TODO: this function is doing too much at the moment, make it more modular next time
def batch_process(data: list[list[Path]], output_csv: Path | None = None) -> None:
    """Spawns parallel native threads matching the total chunk count.

    Args:
        data: A nested list where each sublist represents an independent
            processing chunk mapped directly to a hardware thread execution line.
        output_csv: Path to write the resulting CSV. Defaults to ``database/data.csv``
            in the project root.
    """
    if not data:
        logger.error("no data batches provided")
        return

    if output_csv is None:
        output_csv = Path(__file__).parent.parent / "database/data.csv"

    num_threads = len(data)

    total_files = sum(len(batch) for batch in data)

    log = logger.bind(
        component="batches",
        num_threads=num_threads,
        total_batches=len(data),
        total_files=total_files,
    )

    log.info("starting batch processing")

    completed_workers = 0
    failed_workers = 0
    all_data: list[dict[str, str]] = []

    with ThreadPoolExecutor(
        max_workers=num_threads,
        thread_name_prefix="dispatcher",
    ) as executor:
        futures = {
            executor.submit(
                _process_batch_worker,
                batch,
            ): index
            for index, batch in enumerate(data, start=1)
        }

        for future in as_completed(futures):
            batch_id = futures[future]

            try:
                result = future.result()
                all_data.extend(result)
                completed_workers += 1
                logger.bind(
                    batch_id=batch_id,
                ).info(
                    "worker completed",
                )

            except Exception:
                logger.bind(
                    batch_id=batch_id,
                ).exception(
                    "worker crashed",
                )

    if all_data:
        fieldnames = list({k for row in all_data for k in row})
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_data)
        log.info("csv_written", path=str(output_csv), rows=len(all_data))

    log.info(
        "batch processing finished",
        completed_workers=completed_workers,
        failed_workers=failed_workers,
    )
