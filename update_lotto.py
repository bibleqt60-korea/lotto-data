import json
import os
import urllib.request

BASE_URL = (
    "https://www.dhlottery.co.kr/"
    "common.do?method=getLottoNumber&drwNo="
)

OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    "data",
    "lotto.json",
)


def get_round(round_no):
    url = BASE_URL + str(round_no)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def convert_item(data):
    return {
        "round": int(data["drwNo"]),
        "drawDate": data["drwNoDate"],
        "numbers": [
            int(data["drwtNo1"]),
            int(data["drwtNo2"]),
            int(data["drwtNo3"]),
            int(data["drwtNo4"]),
            int(data["drwtNo5"]),
            int(data["drwtNo6"]),
        ],
        "bonusNumber": int(data["bnusNo"]),
        "firstWinnerCount": int(
            data.get("firstPrzwnerCo", 0)
        ),
        "secondWinnerCount": int(
            data.get("secondPrzwnerCo", 0)
        ),
        "thirdWinnerCount": int(
            data.get("thirdPrzwnerCo", 0)
        ),
        "fourthWinnerCount": int(
            data.get("fourthPrzwnerCo", 0)
        ),
        "fifthWinnerCount": int(
            data.get("fifthPrzwnerCo", 0)
        ),
        "firstPrize": int(
            data.get("firstWinamnt", 0)
        ),
        "secondPrize": int(
            data.get("secondWinamnt", 0)
        ),
        "thirdPrize": int(
            data.get("thirdWinamnt", 0)
        ),
        "fourthPrize": int(
            data.get("fourthWinamnt", 0)
        ),
        "fifthPrize": int(
            data.get("fifthWinamnt", 0)
        ),
    }


def main():
    results = []

    for round_no in range(1, 1300):
        try:
            data = get_round(round_no)

            if data.get("returnValue") != "success":
                continue

            results.append(convert_item(data))

        except Exception:
            continue

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