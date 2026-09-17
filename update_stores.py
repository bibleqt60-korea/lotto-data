import json
import time
from pathlib import Path
import requests

BASE_URL = "https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do"
LOTTO_FILE = Path("data/lotto.json")
DATA_DIR = Path("data/stores")
START_ROUND = 262

def get_rounds():
    if not LOTTO_FILE.exists():
        return []

    with LOTTO_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    results = data.get("results", [])

    if not isinstance(results, list):
        return []

    rounds = []

    for item in results:
        if not isinstance(item, dict):
            continue

        try:
            round_no = int(item.get("round", 0))
        except (TypeError, ValueError):
            continue

        if round_no >= START_ROUND:
            rounds.append(round_no)

    return sorted(set(rounds))


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
            headers={"User-Agent": "Mozilla/5.0"},
        )

        response.raise_for_status()
        data = response.json()

    except Exception as error:
        print(f"{round_no}회 {rank}등 조회 실패: {error}")
        return []

    result = data.get("data", {})

    if not isinstance(result, dict):
        return []

    stores = result.get("list", [])

    if not isinstance(stores, list):
        return []

    output = []

    for item in stores:
        if not isinstance(item, dict):
            continue

        name = item.get("shpNm", "")

        if not name:
            continue

        output.append({
            "name": name,
            "address": item.get("shpAddr", ""),
            "method": item.get("atmtPsvYnTxt", ""),
        })

    return output


def save_round(round_no, first, second):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    available = bool(first or second)

    data = {
        "round": round_no,
        "status": "available" if available else "waiting",
        "message": (
            ""
            if available
            else "당첨 판매점 정보가 아직 업데이트되지 않았습니다."
        ),
        "first": first,
        "second": second,
    }

    path = DATA_DIR / f"{round_no}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"{round_no}회 저장 완료 "
        f"(1등 {len(first)}곳 / 2등 {len(second)}곳)"
    )


def main():
    rounds = get_rounds()

    if not rounds:
        print("로또 회차 데이터를 찾을 수 없습니다.")
        return

    print(
        f"확인할 회차: "
        f"{rounds[0]} ~ {rounds[-1]}"
    )

    added = 0
    skipped = 0

    for round_no in rounds:
        path = DATA_DIR / f"{round_no}.json"

        if path.exists():
            print(f"{round_no}회 이미 존재 → 건너뜀")
            skipped += 1
            continue

        print(f"{round_no}회 판매점 조회 중...")

        first = get_stores(round_no, 1)

        time.sleep(1)

        second = get_stores(round_no, 2)

        save_round(
            round_no,
            first,
            second,
        )

        added += 1

        time.sleep(1)

    print()
    print(
        f"완료: {added}개 추가 / "
        f"{skipped}개 기존 데이터"
    )


if __name__ == "__main__":
    main()
