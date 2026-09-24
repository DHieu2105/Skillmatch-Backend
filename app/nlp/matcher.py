import math
import re


def calculate_similarity(student_text: str, job_text: str) -> float:
    documents = [
        re.findall(r"\b\w+\b", student_text.lower()),
        re.findall(r"\b\w+\b", job_text.lower()),
    ]
    vocabulary = sorted(set(documents[0]) | set(documents[1]))
    document_count = len(documents)

    vectors = []
    for document in documents:
        term_count = len(document)
        frequencies = {term: document.count(term) for term in vocabulary}
        vector = []

        for term in vocabulary:
            document_frequency = sum(term in item for item in documents)
            inverse_document_frequency = math.log(
                (1 + document_count) / (1 + document_frequency)
            ) + 1
            term_frequency = frequencies[term] / term_count if term_count else 0
            vector.append(term_frequency * inverse_document_frequency)

        vectors.append(vector)

    first_vector, second_vector = vectors
    dot_product = sum(left * right for left, right in zip(first_vector, second_vector))
    first_length = math.sqrt(sum(value * value for value in first_vector))
    second_length = math.sqrt(sum(value * value for value in second_vector))

    if not first_length or not second_length:
        return 0.0

    return dot_product / (first_length * second_length)