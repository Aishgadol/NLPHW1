import json
import re

# Conditions to test:
# 1. Names with parentheses: Speaker names should not contain parentheses. If found, print a warning.
# 2. Sentences shorter than 4 tokens: If fewer than 4 tokens, print a warning.
# 3. Sentences containing English letters: If English letters appear, print a warning.
# 4. Sentences containing only non-letter characters: If sentence has no Hebrew/English letters, print a warning.
# 5. Sentences containing multiple sequential dashes ('-'): If '--' appears, print a warning.

ENG_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
HEB_CHARS = set("אבגדהוזחטיכלמנסעפצקרשתץףךםן")

def check_speaker_name(name):
    # Check if name contains parentheses after cleaning (shouldn't)
    # If any parentheses remain, it means they weren't removed.
    if '(' in name or ')' in name:
        return "Name contains parentheses."
    return None

def check_sentence_length(sentence):
    tokens = sentence.split()
    if len(tokens) < 4:
        return f"Sentence shorter than 4 tokens, it's len is: {len(tokens)}."
    return None

def check_english_characters(sentence):
    if any(ch in ENG_CHARS for ch in sentence):
        return "Sentence contains English letters."
    return None

def check_letters_presence(sentence):
    # Check if sentence has at least one Hebrew or English letter
    contains_hebrew = any(ch in HEB_CHARS for ch in sentence)
    contains_english = any(ch in ENG_CHARS for ch in sentence)
    if not (contains_hebrew or contains_english):
        return "Sentence contains no Hebrew or English letters."
    return None

def check_multiple_dashes(sentence):
    # Check for repeated dashes pattern
    if re.search(r"((-|–)\s*){2,}", sentence):
        return "Sentence contains multiple sequential dashes."
    return None

if __name__ == "__main__":
    input_file = "result.jsonl"
    total = 0
    warnings_count = 0

    # Counters for each type of warning to summarize at the end
    name_parentheses_count = 0
    short_sentence_count = 0
    english_count = 0
    no_letters_count = 0
    multi_dash_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            total += 1

            name = data.get("name_speaker", "")
            sentence = data.get("text_sentence", "")

            warnings = []

            # Check each condition
            w1 = check_speaker_name(name)
            if w1:
                warnings.append(w1)

            w2 = check_sentence_length(sentence)
            if w2:
                warnings.append(w2)

            w3 = check_english_characters(sentence)
            if w3:
                warnings.append(w3)

            w4 = check_letters_presence(sentence)
            if w4:
                warnings.append(w4)

            w5 = check_multiple_dashes(sentence)
            if w5:
                warnings.append(w5)

            # Print warnings if any
            if warnings:
                warnings_count += len(warnings)
                print(f"Entry from {data.get('name_protocol')} - Speaker: {name}")
                print(f"Sentence: {sentence}")
                for w in warnings:
                    print("Warning:", w)
                    # Tally each warning
                    if w == "Name contains parentheses.":
                        name_parentheses_count += 1
                    elif w == "Sentence shorter than 4 tokens.":
                        short_sentence_count += 1
                    elif w == "Sentence contains English letters.":
                        english_count += 1
                    elif w == "Sentence contains no Hebrew or English letters.":
                        no_letters_count += 1
                    elif w == "Sentence contains multiple sequential dashes.":
                        multi_dash_count += 1
                print("-" * 50)

    print("\n=== Summary ===")
    print(f"Total entries checked: {total}")
    print(f"Total warnings: {warnings_count}")
    print("Breakdown of warnings:")
    print(f" Names with parentheses: {name_parentheses_count}")
    print(f" Sentences shorter than 4 tokens: {short_sentence_count}")
    print(f" Sentences containing English: {english_count}")
    print(f" Sentences with no Hebrew or English letters: {no_letters_count}")
    print(f" Sentences with multiple sequential dashes: {multi_dash_count}")
