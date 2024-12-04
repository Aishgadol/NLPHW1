# This Pyton file uses the following encoding: utf-8
import csv
import os
from docx import Document
import re
import sys

exclude_lines = ['מנהל הוועדה:', 'רשמת פרלמנטרית:', 'מוזמנים באמצעים מקוונים:', 'חברי כנסת:', 'יועצת משפטית:',
                 'מנהל/ת הוועדה:', 'חברי הוועדה:', 'חברי הכנסת:', 'משתתפים באמצעים מקוונים:', 'מנהלת הוועדה:',
                 'סדר היום:', 'משתתפים (באמצעים מקוונים):', 'רישום פרלמנטרי:',
                 ' החדשים בנוגע לחפירות בהר הבית – הצעה לסדר של חברי הכנסת:', 'יועץ משפטי:', 'קצרנית פרלמנטרית:',
                 'קצרנית:', 'רצח הירקן בטירה ופעולות משטרת ישראלהיו"ר ש\' וייס:', '(23 בינואר 2008):', '(7 ביוני 2006)',
                 'אי-אמון בממשלה בשל:', 'הצעות חוק:', 'רשמה וערכה:', 'סדר-היום:', 'נוכחים:', 'ייעוץ משפטי:', 'מוזמנים:',
                 'נכחו:']

alef_beit = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש',
             'ת', 'ץ', 'ף', 'ך', 'ם', 'ן']

abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
       'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
       'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


#  save the info of the Sentence
class Sentence:
    tokens = []
    content = ""
    flag_in_corpus = False

    def __init__(self, text):
        # init info: sentence
        self.content = text.replace('\n', '')
        self.content = self.content.strip()
        # regex for date
        self.date_patterns = [
            r"\d{1,2}/\d{1,2}(?:/\d{2,4})",  # DD/MM/YYYY
            r"\d{1,2}\.\d{1,2}(?:\.\d{2,4})",  # DD.MM.YYYY
        ]
        # regex for time
        self.time_pattern = r"\b(?:[0-1]?[0-9]|2[0-3]):[0-5][0-9]\b"
        # regex for acronyms
        self.acronyms_pattern = r'\w+"\w+'
        # regex for numbers percent and price
        self.num_pattern = r'(\d)+(,\d{3})*(\.\d+)?(%|$)?'
        # regex for word that is none of the above
        self.word_pattern = r"([^א-ת0-9'])"
        # create the tokens
        self.create_tokens()
        # check if the there is enough tokens to appear in the corpus
        self.flag_in_corpus = len(self.tokens) > 3

    def create_tokens(self):
        self.tokens = []
        # split to words by spaces
        temp_words = self.content.split()
        # go through all the words
        for word in temp_words:
            try:
                self.add_token(word)
            except:
                pass

    def add_token(self, word):
        # if the word is empty
        if len(word) == 0:
            return
        # if the word is one char like: ',' ':' '/' and etc.
        if len(word) == 1:
            self.tokens.append(word)
            return
        # in all scenarios except else if there is a match we split the word to 3 parts: before, date and after
        # for the before and after words we send the word back to the function
        dates_matchers = [re.search(pattern, word) for pattern in self.date_patterns]
        # check if the word contain a date
        if any(dates_matchers):
            for matcher in dates_matchers:
                if matcher:
                    self.add_token(word[:matcher.start()])
                    self.tokens.append(matcher.group())
                    self.add_token(word[matcher.end():])
                    break
        # check if the word contain a time pattern
        elif matcher := re.search(self.time_pattern, word):
            self.add_token(word[:matcher.start()])
            self.tokens.append(matcher.group())
            self.add_token(word[matcher.end():])
        # check if the word contain a number
        elif matcher := re.search(self.num_pattern, word):
            self.add_token(word[:matcher.start()])
            self.tokens.append(matcher.group())
            self.add_token(word[matcher.end():])
        # check if the word contain acronyms
        elif matcher := re.search(self.acronyms_pattern, word):
            self.add_token(word[:matcher.start()])
            self.tokens.append(matcher.group())
            self.add_token(word[matcher.end():])
        # split the word to words by signs
        else:
            result = [item for item in re.split(self.word_pattern, word) if item]  # filter out empty strings
            self.tokens.extend(result)


#  save the info of the paragraph
class Paragraph:
    name_speaker = ""
    content = ""
    sentences = []

    def __init__(self, name_speaker, content):
        # init info: name of speaker and content
        self.name_speaker = name_speaker
        self.content = content
        # create the sentences of the content
        self.create_sentences()

    def create_sentences(self):
        self.sentences = []

        # list of ending marks
        sentence_endings = ['.', '!', '?', '\n', ';']

        start_index = 0

        # go through each character in the text
        for i, ch in enumerate(self.content):
            # check if the current character is an end of a sentence
            if ch in sentence_endings:
                if start_index != i:
                    # check if after the . there is a digit
                    if ch == '.' and i + 1 < len(self.content) and self.content[i + 1].isdigit():
                        continue  # for sentences like 15.8
                    # after ending sign sentence, needs to be 'space' / letter / (/n)
                    if i + 1 < len(self.content) and self.content[i + 1] not in alef_beit \
                            and self.content[i + 1] != ' ' and self.content[i + 1] != '\n':
                        continue  # for sentences like quote

                    # get the sentence
                    sentence = self.content[start_index:i + 1].strip()

                    # check if the sentence is legal
                    if check_sentence(sentence):
                        self.sentences.append(Sentence(sentence))
                # update the start index for the next line
                start_index = i + 1


#  save the info of the protocol
class Protocol:
    name_protocol = ""
    number_knesset = 0
    type_protocol = ""
    paragraph_list = []

    def __init__(self, name):
        # init info: name, number and type
        self.name_protocol = name
        self.number_knesset = name[:2]
        if name[5] == 'v':
            self.type_protocol = "committee"
        else:
            self.type_protocol = "plenary"
        # find the names and the content of the speakers
        self.find_name_and_content()

    def find_name_and_content(self):
        self.paragraph_list = []

        try:
            # read the docs file
            doc = Document(folder_path + '/' + self.name_protocol)
        except Exception as error:
            print("Error reading document " + self.name_protocol + " : " + str(e))
            return  # exit if an error occur

        # flag to see if we started save the content
        flag_start_paragraph = False
        content = ""
        speaker = ""
        # go through the paragraphs
        for paragraph in doc.paragraphs:
            par_text = paragraph.text
            # par_text = par_text.replace('\n', '')
            # get rid of spaces from the right
            par_text = par_text.rstrip()
            # check if the line is a speaker
            # if the line has underline and : and it isn't in the forbidden word list
            if check_exclude(par_text) and par_text and check_underline(paragraph) \
                    and check_for_colon(par_text):
                if content != "" and speaker:
                    # clean the name
                    speaker_clean_name = clean_name(speaker)
                    # check after the cleaning that the speaker name isn't empty
                    if speaker_clean_name:
                        # add the speaker and content as a paragraph of the protocol
                        self.paragraph_list.append(Paragraph(speaker_clean_name, content))
                # update the speaker name
                speaker = par_text
                # clean the content
                content = ""
                # start read the paragraphs
                flag_start_paragraph = True
            # start write the content
            elif flag_start_paragraph and len(par_text) > 0:
                # write the paragraph
                content += paragraph.text
        # add the last speaker and content
        if content != "":
            speaker_clean_name = clean_name(speaker)
            self.paragraph_list.append(Paragraph(speaker_clean_name, content))


def create_protocols(path):
    # regex title check
    reg = r"[0-9]{2}_pt(m|v)_(.)*"
    # read the docs file from the folder
    file_list = os.listdir(path)
    protocol_list = []
    # create the protocol instance
    for name in file_list:
        if re.match(reg, name) and name.endswith(".docx"):
            protocol_list.append(Protocol(name))
        else:
            print("the name of the file is illegal: " + name)
    return protocol_list


def clean_name(name):
    # clean the name and leaves only the first name and last name\s
    regex = r"(<<.*>>)?\s*(תשובת\s*)?((ה)?(ד\"ר|(מ\"מ ה|ה)?יו\"ר|נשיא הפרלמנט האירופי|עו\"ד|((ה)?משנה ל)?ראש הממשלה|נצ\"מ|מר|ניצב|טפ(ס)?ר משנה|רשף|פרופ')?\s+)?(((סגן|סגנית)?\s*((ה)?שר(ת|ה)?|מזכיר(ת)?|ועדת)?\s+)?(הכנסת|הכלכלה( והתכנון)?|האנרגיה והמים|החינוך( והתרבות)?|התשתיות הלאומיות(, האנרגיה והמים)?|המודיעין|לשיתוף פעולה אזורי|ההסברה והתפוצות|האוצר|להגנת הסביבה|התעשי(י)?ה(,)? (ו)?המסחר (והתעסוקה)?|לאיכות הסביבה|(החינוך,|המדע,)?\s*התרבות והספורט|התשתיות|המשפטים|(העבודה ו|העבודה,\s*)?הרווחה\s*(והבריאות|והשירותים החברתיים)?|הבינוי והשיכון|התחבורה( והבטיחות בדרכים)?|המשטרה|הבריאות|החקלאות( ופיתוח הכפר)?|התקשורת|במשרד ראש הממשלה|הפנים|(ה|ל)ביטחון( פנים)?|המדע והטכנולוגיה|התקשורת|העלייה והקליטה|לקליטת\s*העלי(י)?ה|התיירות|החוץ|למודיעין|לאזרחים ותיקים|(לנושאים אסטרטגיים )?ו?לענייני (דתות|מודיעין)?)?)?\s*\-?\s*([א-ת\s'\"\-]*)(\s*(\(.*\))?:|:)(<<.*>>)?"
    if matcher := re.search(regex, name):
        # replace multiple spaces with a single space
        speaker = re.sub(r"\s+", ' ', matcher.group(35))
        # clean spaces from the sides
        return speaker.strip()
    else:
        return ""


def check_exclude(text):
    # check if the word is in the forbidden lines
    for line in exclude_lines:
        if line in text:
            return False
    return True


def check_for_colon(text):
    # check for : sign
    if ':' in text and (
            text[-1] == ':' or text.split(':')[-1].strip()[0] == '>' or text.split(':')[-1].strip()[0] == '<'):
        return True
    return False


def check_underline(para):
    # check if the sentence is underlined
    # there is 3 ways - 1. in style.base_style.font.underline 2. style.font.underline
    if para.style is not None and ((para.style.base_style is not None and para.style.base_style.font.underline) or (
            para.style.font is not None and para.style.font.underline)):
        return True
    # 3. run.underline : we go through all the runs because the first one isn't necessarily enough
    elif para.runs:
        for run in para.runs:
            if run.underline:
                return True
    return False


def check_sentence(sentence):
    # check that the sentence is legal
    # check that the sentence doesn't contain - - pattern
    pattern = r"((-|–)\s*){2}((-|–)\s*)*"
    if re.search(pattern, sentence):
        return False
    flag = 0
    # check that the sentence doesn't contain English letters and that contain at list one Hebrew letter
    for ch in sentence:
        if ch in abc:
            return False
        if ch in alef_beit:
            flag = 1
    return flag


def write_to_csv(path, protocol_list):
    try:
        # open the csv file
        with open(path, mode='w', encoding='utf-8', newline='') as csv_file:
            # create titles of the columns to the csv file
            fieldnames = ['name_protocol', 'number_knesset', 'type_protocol', 'name_speaker', 'text_sentence']
            # create a csv writer
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            # write the titles in the csv
            writer.writeheader()
            # write the info to the csv file
            for protocol in protocol_list:
                for paragraph in protocol.paragraph_list:
                    for sentence in paragraph.sentences:
                        if sentence.flag_in_corpus:
                            writer.writerow({
                                'name_protocol': protocol.name_protocol,
                                'number_knesset': protocol.number_knesset,
                                'type_protocol': protocol.type_protocol,
                                'name_speaker': paragraph.name_speaker,
                                'text_sentence': " ".join(sentence.tokens)
                            })
        print("CSV saved successfully at " + path)
    except Exception as error:
        print("Error occurred while writing to CSV: " + str(e))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # gets the path from sys
        folder_path = sys.argv[1]
        save_path = sys.argv[2]
    else:
        folder_path = input("Enter the path to the docs folder: ")
        save_path = input("Enter the path to save CSV file: ")
    while True:
        # check if the folder path exists
        if os.path.isdir(folder_path):
            break  # exit if path exist
        else:
            # repeat until a valid save path
            print("Folder path doesn't exist. Please try again.")
        # enter the path of the csv file
        folder_path = input("Enter the path to the docs folder: ")
    while True:
        if save_path.endswith(".csv"):
            # try to write to see if path exist
            try:
                with open(save_path, 'w') as f:
                    f.write("Test")  # write a test string
                break  # exit if successful
            except Exception as e:
                print("Error: " + str(e) + "." + " Please provide a valid save path.")
        else:
            print("The save path isn't a CSV file. Please try again.")
        # enter the path to save the csv file
        save_path = input("Enter the path to save CSV file: ")

    # create protocols
    protocols = create_protocols(folder_path)
    # write the data to a csv file
    write_to_csv(save_path, protocols)

