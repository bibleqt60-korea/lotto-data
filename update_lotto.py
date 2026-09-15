import json
import os
import urllib.request

SOURCE_URL = (
    "https://smok95.github.io/"
    "lotto/results/all.json"
)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

SOURCE_FILE = os.path.join(
    DATA_DIR, "source_all.json"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR, "lotto.json"
)


def download_source():
    os.makedirs(DATA_DIR, exist_ok=True)

    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        data = response.read()

    with open(
        SOURCE_FILE,
        "wb",
    ) as file:
        file.write(data)


def convert_item(item):
    divisions = item.get("divisions", [])

    def winners(index):
        if index >= len(divisions):
            return 0
        return int(
            divisions[index].get("winners", 0)
        )

    def prize(index):
        if index >= len(divisions):
            return 0
        return int(
            divisions[index].get("prize", 0)
        )

    return {
        "round": int(item["draw_no"]),
        "drawDate": str(item["date"])[:10],
        "numbers": [
            int(number)
            for number in item["numbers"]
        ],
        "bonusNumber": int(
            item["bonus_no"]
        ),
        "firstWinnerCount": winners(0),
        "secondWinnerCount": winners(1),
        "thirdWinnerCount": winners(2),
        "fourthWinnerCount": winners(3),
        "fifthWinnerCount": winners(4),
        "firstPrize": prize(0),
        "secondPrize": prize(1),
        "thirdPrize": prize(2),
        "fourthPrize": prize(3),
        "fifthPrize": prize(4),
    }


def main():
    print("로또 전체 데이터 다운로드 중...")

    download_source()

    with open(
        SOURCE_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        source = json.load(file)

    if not isinstance(source, list):
        raise Exception(
            "원본 데이터 형식이 올바르지 않습니다."
        )

    results = []

    for item in source:
        try:
            result = convert_item(item)

            if (
                result["round"] > 0
                and len(result["numbers"]) == 6
            ):
                results.append(result)

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

    results.sort(
        key=lambda item: item["round"]
    )

    if not results:
        raise Exception(
            "변환된 로또 데이터가 없습니다."
        )

    output = {
        "latestRound": results[-1]["round"],
        "results": results,
    }

    with open(
        OUTPUT_FILE,
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
        f"완료: {len(results)}개 회차 저장"
    )

    print(
        f"최신 회차: "
        f"{results[-1]['round']}회"
    )


if __name__ == "__main__":
    main()