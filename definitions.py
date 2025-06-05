from typing import TypedDict


class QuestionPart(TypedDict):
    id: str
    video_solution_id: str
    file_id: str
    name: str
    index: int


class QuestionImage(TypedDict):
    file_id: str
    entity_id: str
    entity_type: str
    filename: str
    path: str
    content_type: str


class Question(TypedDict):
    index: int
    id: str
    reference: str
    content: str
    parts: list[QuestionPart]
    images: list[QuestionImage]
    markScheme: str
    paperIds: list[str]


class Paper(TypedDict):
    id: str
    reference: str


class QuestionData(TypedDict):
    questions: list[Question]
    requestId: str
    papers: list[Paper]


class State(TypedDict):
    data: QuestionData


class StateQuery(TypedDict):
    state: State


class DehydratedState(TypedDict):
    queries: list[StateQuery]


class SubtopicQuestion(TypedDict):
    id: str
    name: str
    index: int


class Subtopic(TypedDict):
    id: str
    name: str
    index: int
    description: str
    slug: str
    questions: list[SubtopicQuestion]


def has_question(topic: Subtopic, id: str) -> bool:
    for question in topic["questions"]:
        if question["id"] == id:
            return True
    return False


class Topic(TypedDict):
    id: str
    name: str
    slug: str
    subtopics: list[Subtopic]


class MainPageProps(TypedDict):
    topic: Topic
    title: str
    description: str


class PageProps(TypedDict):
    pageProps: MainPageProps
    dehydratedState: DehydratedState


class NextData(TypedDict):
    pageProps: PageProps


class SubjectTree(TypedDict):
    id: str
    topics: list[Topic]


class QuestionBankSubjects(TypedDict):
    basePath: str
    subjectTree: SubjectTree


class QuestionBankProps(TypedDict):
    pageProps: QuestionBankSubjects


class QuestionBank(TypedDict):
    pageProps: QuestionBankProps
