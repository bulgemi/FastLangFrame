import csv
from csv import DictWriter
from pathlib import Path

COMMON_FILE_RESULT_NAME = "sk_ens_query_list_as_is_anwser"
common_headers = ["query"]
rewrite_headers = ["rewrite_resp_time", "rewritten_query", "period_queries"]
planner_headers = [
    "plann_resp_time",
    "objective",
    # "assumptions",
    # "comparison_specs",
    "collect_steps",
    "analysis_steps",
]


def sample_test_data_dir():
    # 현재 파일 기준으로 테스트 데이터 디렉토리 설정
    return Path(__file__).parent / "data"


def load_csv_with_headers(file_path: Path):
    """CSV 파일에서 헤더와 데이터를 딕셔너리 형태로 반환합니다."""
    assert file_path.exists(), "Not found file"
    assert file_path.suffix.lower() == ".csv", "Only CSV files are supported"

    with file_path.open(mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames  # 헤더 필드명
        data = list(reader)  # 딕셔너리 형태의 데이터

    return headers, data


def save_test_result_to_csv(
    file_path: Path,
    headers: list[str],
    row: dict[str] = None,
):
    write_header = not file_path.exists()

    with file_path.open(mode="a", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=headers, delimiter=",")
        if write_header:
            writer.writeheader()
        if row:
            complete_row = {header: row.get(header, "") for header in headers}
            writer.writerow(complete_row)
