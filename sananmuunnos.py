import json
import re
from itertools import chain

from flask import Flask, request

WORDS_REGEX = re.compile(r"\S+\W*")
FIRST_VOWELS_REGEX = re.compile(r"(?i)[AEIOUYÅÄÖ]+")


app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    try:
        original_text = json.loads(request.data)
    except json.decoder.JSONDecodeError as e:
        return str(e), 400

    handled_text = do_sananmuunnos(original_text)

    return json.dumps(handled_text, ensure_ascii=False).encode("utf8"), 200


def do_sananmuunnos(original_text):
    words = WORDS_REGEX.findall(original_text)

    if len(words) < 2:
        return original_text

    word_pairs = (word for word in zip(words[0::2], words[1::2]))
    handled_words = chain(*(handle_word_pair(*pair) for pair in word_pairs))
    handled_text = "".join(handled_words) + (words[-1] if len(words) % 2 else "")

    return handled_text


def handle_word_pair(word_1, word_2):
    first_vowels_1 = FIRST_VOWELS_REGEX.search(word_1)
    first_vowels_2 = FIRST_VOWELS_REGEX.search(word_2)

    if first_vowels_1 is None or first_vowels_2 is None:
        return word_1, word_2

    index_1 = first_vowels_1.end()
    index_2 = first_vowels_2.end()

    return word_2[:index_2] + word_1[index_1:], word_1[:index_1] + word_2[index_2:]
