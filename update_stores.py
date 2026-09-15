import json
import time
from pathlib import Path

import requests


BASE_URL = (
    "https://www.dhlottery.co.kr/"
    "wnprchsplcsrch/selectLtWnShp.do"
)

LOTTO_FILE = Path("data/lotto.json")
DATA_DIR = Path("data/stores")


def get_latest_round():
    if not LOTTO_FILE.exists():
        return 0

    with LOTTO_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    results = data.get("results", [])

    if not results:
        return 0

    rounds = [
        item.get("round", 0)
        for item in results
        if isinstance(item, dict)
    ]

    return max(rounds)


def get_stores(round_no, rank):
    params = {
        "srchWnShpRnk": rank,
        "srchLtEpsd": round_no,
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            },
        )

        response.raise_for_status()

        data = response.json()

    except Exception as error:
        print(
            f"{round_no}회 {rank}등 조회 실패: {error}"
        )
        return []

    result = data.get("data", {})

    if not isinstance(result, dict):
        return []

    stores = result.get("list", [])

    if not isinstance(stores, list):
        return []

    return [
        {
            "name": item.get("shpNm", ""),
            "address": item.get("shpAddr", ""),
            "method": item.get(
                "atmtPsvYnTxt",
                "",
            ),
        }
        for item in stores
        if item.get("shpNm")
    ]


def save_round(
    round_no,
    first,
    second,
):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    available = bool(first or second)

    output = {
        "round": round_no,
        "status": (
            "available"
            if available
            else "waiting"
        ),
        "message": (
            ""
            if available
            else (
                "당첨 판매점 정보가 "
                "아직 업데이트되지 않았습니다."
            )
        ),
        "first": first,
        "second": second,
    }

    path = DATA_DIR / f"{round_no}.json"

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"{path} 저장 완료"
    )


def main():
    round_no = get_latest_round()

    if round_no <= 0:
        print(
            "최신 회차를 찾을 수 없습니다."
        )
        return

    print(
        f"최신 회차: {round_no}"
    )

    first = get_stores(
        round_no,
        1,
    )

    time.sleep(1)

    second = get_stores(
        round_no,
        2,
    )

    print(
        f"1등: {len(first)}곳"
    )
    print(
        f"2등: {len(second)}곳"
    )

    save_round(
        round_no,
        first,
        second,
    )


if __name__ == "__main__":
    main()