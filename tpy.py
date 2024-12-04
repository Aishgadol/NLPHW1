import os
import re
from docx import Document

# Define the directory containing the .docx files
directory = "TextFiles"

# Dictionary to map Hebrew numeral words to integers
hebrew_word_to_num = {
    "אחד": 1, "שניים": 2, "שלושה": 3, "ארבעה": 4, "חמישה": 5, "שישה": 6, "שבעה": 7, "שמונה": 8, "תשעה": 9,
    "עשרה": 10, "עשרים": 20, "שלושים": 30, "ארבעים": 40, "חמישים": 50, "שישים": 60, "שבעים": 70, "שמונים": 80, "תשעים": 90,
    "מאה": 100, "מאתיים": 200, "אלף": 1000, "אלפיים": 2000
}

def parse_hebrew_number(hebrew_text):
    """Convert a Hebrew number phrase into an integer."""
    total = 0
    multiplier = 1
    for word in hebrew_text.split("-"):
        word = word.strip()  # Remove leading/trailing spaces
        if word in hebrew_word_to_num:
            value = hebrew_word_to_num[word]
            if value >= 100:  # Handle hundreds or thousands
                multiplier = value
            else:
                total += value * multiplier
        else:
            continue  # Skip unknown words
    return total

# Regular expressions to find protocol numbers
regex_patterns = [
    r"(?:פרוטוקול מס'|מספר הישיבה)\s*(\d+)",  # Regular numeric pattern
    r"הישיבה ה-(.*?)(?:[\n ]|$)"             # Hebrew numeral pattern
]

# Dictionary to store the results
protocol_data = {}
readable_count = 0
total_files = 0
first_five_unreadable = []  # List to store the first 5 occurrences of -1

# Process each .docx file in the directory
for file in os.listdir(directory):
    if file.endswith(".docx"):  # Ensure it's a .docx file
        total_files += 1
        file_path = os.path.join(directory, file)

        # Open and read the .docx file
        doc = Document(file_path)

        # Combine the first few paragraphs to search for protocol number
        first_few_paragraphs = "\n".join([paragraph.text for paragraph in doc.paragraphs[:10]])

        # Initialize protocol number as not found (-1)
        protocol_number = -1

        # Search for protocol number using each pattern
        for pattern in regex_patterns:
            match = re.search(pattern, first_few_paragraphs)
            if match:
                if pattern == regex_patterns[0]:  # Numeric pattern
                    protocol_number = int(match.group(1))
                elif pattern == regex_patterns[1]:  # Hebrew numeral pattern
                    hebrew_number = match.group(1)
                    protocol_number = parse_hebrew_number(hebrew_number)
                break  # Stop searching once a match is found

        # Store the result
        protocol_data[file] = protocol_number
        if protocol_number != -1:
            readable_count += 1
        elif len(first_five_unreadable) >-1:
            first_five_unreadable.append((file, protocol_number))

# Print the number of readable numbers and total files
print(f"Readable Protocol Numbers: {readable_count} out of {total_files} files.")

# Print the first 5 occurrences of -1
for file, protocol_number in first_five_unreadable:
    print(f"File: {file}, Protocol Number: {protocol_number}")
