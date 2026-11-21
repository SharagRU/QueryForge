
import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT_DIR = Path(__file__).resolve().parents[2]
TRAIN_FILE = ROOT_DIR / "data" / "benchmarks" / "train.json"


class SQLRetriever:
    def __init__(self):
        with open(TRAIN_FILE, "r", encoding="utf-8") as file:
            self.examples = json.load(file)

        self.questions = [
            example["question"] for example in self.examples
        ]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            stop_words="english"
        )

        self.question_vectors = self.vectorizer.fit_transform(
            self.questions
        )

    def retrieve(self, question: str):
        query_vector = self.vectorizer.transform([question])

        similarities = cosine_similarity(
            query_vector,
            self.question_vectors
        )[0]

        best_index = similarities.argmax()
        best_example = self.examples[best_index]

        return {
            "matched_question": best_example["question"],
            "sql": best_example["reference_sql"],
            "similarity": round(float(similarities[best_index]), 4)
        }


if __name__ == "__main__":
    retriever = SQLRetriever()

    test_questions = [
        "Show me the top 5 products by revenue",
        "Which cities have the most orders?",
        "Find the average order value by customer"
    ]

    for question in test_questions:
        result = retriever.retrieve(question)

        print("\nQUESTION:", question)
        print("MATCHED:", result["matched_question"])
        print("SIMILARITY:", result["similarity"])
        print("SQL:\n", result["sql"])
