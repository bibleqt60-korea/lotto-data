import json
import os
import urllib.request

API_URL = (
    "https://www.dhlottery.co.kr/"
    "common.do?method=getLottoNumber&drwNo="
)

DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "data",
    "lotto.json",
)


def get_round(round_no):
    url = API_URL + str(round_no)

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


def convert(data):
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


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "latestRound": 0,
            "results": [],
        }

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_data(data):
    os.makedirs(
        os.path.dirname(DATA_FILE),
        exist_ok=True,
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main():
    data = load_data()

    results = data.get("results", [])
    latest = int(data.get("latestRound", 0))

    print(f"기존 최신 회차: {latest}")

    # 최초 실행
    if latest == 0:
        print("최초 데이터 수집을 시작합니다.")

        for round_no in range(1, 1300):
            try:
                result = get_round(round_no)

                if result.get("returnValue") != "success":
                    continue

                results.append(convert(result))

                print(
                    f"{round_no}회 수집 완료"
                )

            except Exception as error:
                print(
                    f"{round_no}회 실패: {error}"
                )

        if not results:
            raise Exception(
                "로또 데이터를 가져오지 못했습니다."
            )

    else:
        # 기존 데이터가 있으면 최신 이후만 확인
        for round_no in range(
            latest + 1,
            latest + 3,
        ):
            try:
                result = get_round(round_no)

                if result.get("returnValue") != "success":
                    continue

                results.append(convert(result))

                print(
                    f"{round_no}회 신규 데이터 추가"
                )

            except Exception as error:
                print(
                    f"{round_no}회 확인 실패: {error}"
                )

    results.sort(
        key=lambda item: item["round"]
    )

    data = {
        "latestRound": results[-1]["round"],
        "results": results,
    }

    save_data(data)

    print(
        f"완료: 총 {len(results)}개 회차"
    )
    print(
        f"최신 회차: {data['latestRound']}회"
    )


if __name__ == "__main__":
    main()