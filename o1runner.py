import json
import re
from collections import Counter

ENG_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
HEB_LETTERS = set("אבגדהוזחטיכלמנסעפצקרשתץףךםן")

INVALID_PATTERNS = [
    r"((-|–)\s*){2,}",  # multiple dashes
    r"\.\.\.",
    r"!!+",
    r"\?\?+"
]

def is_sentence_legit(sentence: str) -> (bool, str):
    if not any(ch in HEB_LETTERS for ch in sentence):
        return False, "No Hebrew letters found."
    if any(ch in ENG_CHARS for ch in sentence):
        return False, "Contains English characters."
    for pat in INVALID_PATTERNS:
        if re.search(pat, sentence):
            return False, f"Matches invalid pattern: {pat}"

    allowed_endings = HEB_LETTERS.union({'.', '!', '?', '"', '”', '“', '\''})
    if sentence[-1] not in allowed_endings:
        return False, f"Ends with a suspicious character: '{sentence[-1]}'"

    tokens = sentence.split()
    if len(tokens) < 4:
        return False, "Fewer than 4 tokens."

    return True, "Looks good."

if __name__ == "__main__":
    input_file = "result.jsonl"
    total = 0
    passed = 0
    short_sentences = []
    counter1 = 0
    suspicious_ending_chars = Counter()

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            sentence = data.get("text_sentence", "")
            total += 1
            legit, reason = is_sentence_legit(sentence)
            if not legit:
                if reason == "Fewer than 4 tokens.":
                    short_sentences.append((data["name_protocol"], data["name_speaker"], sentence))
                elif "suspicious character" in reason:
                    counter1 += 1
                    # Extract the suspicious character from the reason string
                    # reason format: Ends with a suspicious character: 'X'
                    # Let's parse it
                    match = re.search(r"Ends with a suspicious character: '(.*)'", reason)
                    if match:
                        suspicious_char = match.group(1)
                        suspicious_ending_chars[suspicious_char] += 1
                else:
                    print(f"Suspicious sentence from {data['name_protocol']} (speaker: {data['name_speaker']}):")
                    print(sentence)
                    print("Reason:", reason)
                    print("-" * 50)
            else:
                passed += 1

    print(f"Total sentences checked: {total}")
    print(f"Passed checks: {passed}")
    print(f"Suspicious: {total - passed}")
    print(f'Number of sentences ending with suspicious characters: {counter1}')

    if short_sentences:
        print("\nSentences with fewer than 4 tokens:")
        for proto, speaker, sent in short_sentences:
            print(f"Protocol: {proto}, Speaker: {speaker}")
            print(sent)
            print("-" * 50)

    # Print top 50 suspicious ending characters
    if suspicious_ending_chars:
        print("\nTop 50 suspicious ending characters:")
        for char, freq in suspicious_ending_chars.most_common(50):
            print(f"'{char}' appeared {freq} times")
