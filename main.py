import os
from pathlib import Path
from typing import cast
import requests
import re
import json

from cookies import load_cookies_from_file
from decrypt import decrypt
from definitions import (
    NextData,
    Question,
    QuestionBank,
    QuestionData,
    Subtopic,
    has_question,
)
from process import process_latex

REV_URL: str = "https://www.revisionvillage.com"
BUILD_ID_REGEX: str = r'(?:buildId\":\")(.+?(?="))'


def get_version() -> str:
    request = requests.get(REV_URL).text
    matches = re.search(BUILD_ID_REGEX, request)
    if matches:
        return str(matches.groups(0)[0])
    else:
        raise ValueError("Could not get version from website!")


def get_question(
    question: Question,
    topic_definition: NextData,
    subtopics: list[Subtopic],
    request_id: str,
    secondary_id: str,
    data: QuestionData,
    cookies: dict[str, str],
):
    path = Path(f"questions/{topic_definition['pageProps']['pageProps']['title']}/")
    matching_topic = [x for x in subtopics if has_question(x, question["id"])]
    if len(matching_topic) == 0:
        raise ValueError("No matching topic found!")
    path /= matching_topic[0]["name"]
    matching_paper = [x for x in data["papers"] if x["id"] == question["paperIds"][0]]
    if len(matching_paper) == 0:
        raise ValueError("No matching paper found!")
    path /= matching_paper[0]["reference"]
    path /= str(question["index"])
    content = decrypt(question["content"], f"{request_id}-{secondary_id}-content")
    mark_scheme = decrypt(
        question["markScheme"], f"{request_id}-{secondary_id}-mark_scheme"
    )

    m = process_latex(content).rstrip().strip()
    ms = process_latex(mark_scheme).rstrip().strip()
    os.makedirs(path, exist_ok=True)

    for image in question["images"]:
        image_path = Path(image["path"])
        file_path = Path(f"{path}/{image_path.name}")
        if file_path.exists():
            continue
        request = requests.get(
            f"https://assets.revisionvillage.com/{image['path']}",
            cookies=cookies,
        )
        with open(file_path, "wb") as f:
            _ = f.write(request.content)

    with open(f"{path}/question.tex", "w") as f:
        _ = f.write(m)
    with open(f"{path}/mark_scheme.tex", "w") as f:
        _ = f.write(ms)

    pass


def main() -> None:
    cookies = load_cookies_from_file("cookies.json")
    version = get_version()
    subject = input("Subject URL: ")
    base_url = f"{REV_URL}/_next/data/{version}/{subject}"
    questionbank = f"{base_url}/questionbank.json"
    question_bank: QuestionBank = cast(
        QuestionBank, json.loads(requests.get(questionbank, cookies=cookies).text)
    )
    for topic in question_bank["pageProps"]["pageProps"]["subjectTree"]["topics"]:
        req_url = f"{base_url}/questionbank/{topic['slug']}.json"
        request = requests.get(req_url, cookies=cookies)
        topic_definition: NextData = cast(NextData, json.loads(request.text))

        data = topic_definition["pageProps"]["dehydratedState"]["queries"][1]["state"][
            "data"
        ]
        request_id = data["requestId"]
        subtopics = topic_definition["pageProps"]["pageProps"]["topic"]["subtopics"]
        secondary_id = [x[1] for x in cookies.items() if "LastAuthUser" in x[0]][0]
        for question in data["questions"]:
            get_question(
                question,
                topic_definition,
                subtopics,
                request_id,
                secondary_id,
                data,
                cookies,
            )


if __name__ == "__main__":
    main()
