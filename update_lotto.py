import json
import os
import urllib.request

API_URL = (
    "https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do"
    "?srchLtEpsd=all"
)

OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    "data",
    "lotto.json",
)


def get_data():
    request = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=30,
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def convert_item(item):
    return {
        "round": int(item.get("drwtNo", 0)),
        "drawDate": str(
            item.get("drwNoDate", "")
        ),
        "numbers": [
            int(item.get("drwtNo1", 0)),
            int(item.get("drwtNo2", 0)),
            int(item.get("drwtNo3", 0)),
            int(item.get("drwtNo4", 0)),
            int(item.get("drwtNo5", 0)),
            int(item.get("drwtNo6", 0)),
        ],
        "bonusNumber": int(
            item.get("bnusNo", 0)
        ),
        "firstWinnerCount": int(
            item.get("firstPrzwnerCo", 0)
        ),
        "secondWinnerCount": int(
            item.get("secondPrzwnerCo", 0)
        ),
        "thirdWinnerCount": int(
            item.get("thirdPrzwnerCo", 0)
        ),
        "fourthWinnerCount": int(
            item.get("fourthPrzwnerCo", 0)
        ),
        "fifthWinnerCount": int(
            item.get("fifthPrzwnerCo", 0)
        ),
        "firstPrize": int(
            item.get("firstWinamnt", 0)
        ),
        "secondPrize": int(
            item.get("secondWinamnt", 0)
        ),
        "thirdPrize": int(
            item.get("thirdWinamnt", 0)
        ),
        "fourthPrize": int(
            item.get("fourthWinamnt", 0)
        ),
        "fifthPrize": int(
            item.get("fifthWinamnt", 0)
        ),
    }


def main():
    data = get_data()

    raw_list = data.get("list", [])

    results = [
        convert_item(item)
        for item in raw_list
        if isinstance(item, dict)
    ]

    results = [
        item
        for item in results
        if item["round"] > 0
        and len(item["numbers"]) == 6
    ]

    results.sort(
        key=lambda item: item["round"]
    )

    output = {
        "latestRound": (
            results[-1]["round"]
            if results
            else 0
        ),
        "results": results,
    }

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True,
    )

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

    if results:
        print(
            f"최신 회차: "
            f"{results[-1]['round']}회"
        )


if __name__ == "__main__":
    main()