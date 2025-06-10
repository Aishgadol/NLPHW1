# Knesset Protocol Corpus Processor

## Project Title & Elevator Pitch
Knesset Protocol Corpus Processor transforms Israeli parliamentary transcripts in `.docx` format into a clean sentence-level corpus. It extracts speaker names, splits Hebrew text into normalized sentences, and generates a JSONL or CSV dataset for downstream NLP work.

## Purpose & Objectives
- **Robust extraction** of speaker names and protocol numbers from raw `.docx` files.
- **Accurate sentence segmentation** supporting Hebrew text with numeric and date patterns.
- **Filtering** of corrupt or low-quality sentences (<4 tokens, English text, suspicious punctuation).
- **Outputs** ready for NLP experiments: JSONL records with protocol metadata and sentences.

Success is measured by:
- Complete coverage of valid transcripts in `TextFiles/`.
- No duplicate protocol–speaker–sentence tuples.
- All produced sentences pass the validation checks in `tpy.py` and `o1runner.py`.

## Architecture & Module Breakdown
```
TextFiles/*.docx → final_sol2.py → result.jsonl
                          ↘
                           tpy.py / o1runner.py → quality reports
```
### `final_sol2.py`
- Reads every transcript from the `TextFiles` directory using `python-docx`【F:final_sol2.py†L248-L303】.
- Detects speakers via underline/bold style heuristics【F:final_sol2.py†L204-L211】.
- Splits paragraphs to sentences with `sentence_splitter` which skips numeric and quote artifacts【F:final_sol2.py†L107-L127】.
- Normalizes speaker names by removing titles and departments【F:final_sol2.py†L165-L202】.
- Writes unique `(name_protocol, number_knesset, type_protocol, number_protocol, name_speaker, text_sentence)` tuples to `result.jsonl`【F:final_sol2.py†L292-L314】.

### `processing_knesset_corpus.py`
- Alternative extraction pipeline producing a CSV file. Defines `Sentence`, `Paragraph`, and `Protocol` classes to tokenize and validate content【F:processing_knesset_corpus.py†L24-L208】.
- Command‑line interface expects input/output paths and performs sanity checks before writing the corpus【F:processing_knesset_corpus.py†L312-L346】.

### `tpy.py` and `o1runner.py`
- Provide post‑processing validation: checking sentence length, presence of Hebrew characters, and removal of unusual punctuation or English letters【F:tpy.py†L1-L44】【F:o1runner.py†L1-L32】.
- Output summaries of suspicious sentences and character statistics to aid manual inspection【F:o1runner.py†L34-L40】.

### `runnerup.py`
- Uses `pandas` to examine duplicates in `result.jsonl` and to highlight problematic speaker names containing parentheses【F:runnerup.py†L1-L45】.

## Installation & Environment Setup
1. **Python** 3.12 or newer is required (see `pyvenv.cfg`).
2. Install package dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Ensure LibreOffice or Word is available if you plan to manually inspect `.docx` files (optional).

## Usage & Examples
### Extract the Corpus
```bash
python final_sol2.py            # reads TextFiles/*.docx and writes result.jsonl
```
Expected output includes progress messages such as:
```
now working on: 15_ptm_532756.docx
completed
```
### Validate Generated Sentences
```bash
python tpy.py                   # prints warnings for any problematic rows
python o1runner.py              # prints summary statistics
```
Each script scans `result.jsonl` and reports counts of short sentences, English text, or suspicious characters.

## Outputs & Artifacts
- **`result.jsonl`** – Main corpus; one JSON object per line with protocol metadata and the cleaned sentence.
- **Quality Reports** – Console output from `tpy.py`, `o1runner.py`, or `runnerup.py`. Redirect to text files if persistent logs are needed.
- **Optional CSV** – `processing_knesset_corpus.py` can save the dataset as `output.csv` when run with custom paths.

## Development & Contribution Workflow
- Lint/format using `black` and `isort` before committing.
- Validate scripts compile: `python3 -m py_compile final_sol2.py o1runner.py processing_knesset_corpus.py runnerup.py tpy.py sol1.py` (note: `main.py` contains unresolved merge markers).
- Submit pull requests with a description of dataset changes or code improvements. Ensure new code passes the validation scripts.

## Project Status & Roadmap
This repository represents **alpha-quality** coursework. `main.py` contains merge conflicts and is not executed. Future work includes:
- Cleaning `main.py` and unifying with `final_sol2.py`.
- Adding automated unit tests for sentence segmentation and name extraction.
- Packaging the tool as a Python module with a CLI entry point.

## License & Attribution
No license file is present. We recommend adopting the MIT License for permissive reuse.
