import re
import csv
import time
import requests
from difflib import SequenceMatcher
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "references.tex"
OUTPUT_FILE = "references_with_doi.tex"
REPORT_FILE = "doi_verification_report.csv"

# Put your email here for Crossref's polite pool
EMAIL = "your_email@example.com"

CROSSREF_URL = "https://api.crossref.org/works"

# Minimum similarity required before considering a match
HIGH_CONFIDENCE = 0.90
MEDIUM_CONFIDENCE = 0.80

REQUEST_DELAY = 0.2


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_latex(text):
    """
    Remove common LaTeX formatting so titles can be compared.
    """

    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)

    text = text.replace("``", "")
    text = text.replace("''", "")
    text = text.replace("`", "")
    text = text.replace("~", " ")

    # Remove LaTeX commands
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)

    # Normalize
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def similarity(a, b):
    """
    Calculate title similarity.
    """

    a = clean_latex(a)
    b = clean_latex(b)

    return SequenceMatcher(None, a, b).ratio()


# ============================================================
# EXTRACT BIBITEMS
# ============================================================

def extract_bibitems(text):

    pattern = r"(\\bibitem\{([^}]+)\}.*?)(?=\\bibitem\{|\\end\{thebibliography\})"

    matches = re.findall(pattern, text, re.DOTALL)

    references = []

    for full_entry, key in matches:

        references.append({
            "key": key,
            "text": full_entry.strip()
        })

    return references


# ============================================================
# EXTRACT TITLE
# ============================================================

def extract_title(entry):

    # Most of your references follow:
    #
    # "Title,'' Journal, Year.
    #
    # Try quoted title first.

    match = re.search(
        r"``(.*?)''",
        entry,
        re.DOTALL
    )

    if match:
        return match.group(1).strip()

    # If title has no quotes, try after bibitem
    lines = entry.splitlines()

    if len(lines) >= 2:

        candidate = lines[1].strip()

        # Avoid author-only lines
        if len(candidate) > 20:
            return candidate

    return ""


# ============================================================
# EXTRACT YEAR
# ============================================================

def extract_year(entry):

    years = re.findall(r"\b(20[0-2][0-9])\b", entry)

    if years:
        return int(years[0])

    return None


# ============================================================
# CHECK WHETHER DOI ALREADY EXISTS
# ============================================================

def extract_existing_doi(entry):

    patterns = [
        r"https?://doi\.org/([^\s}]+)",
        r"doi:\s*([^\s,}]+)",
        r"DOI[:\s]+([^\s,}]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            entry,
            re.IGNORECASE
        )

        if match:
            return match.group(1).rstrip(".,;")

    return None


# ============================================================
# SEARCH CROSSREF
# ============================================================

def search_crossref(title, year=None):

    params = {
        "query.title": title,
        "rows": 5,
        "mailto": EMAIL
    }

    if year:
        params["filter"] = f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"

    headers = {
        "User-Agent":
            f"DOI-Extractor/1.0 (mailto:{EMAIL})"
    }

    try:

        response = requests.get(
            CROSSREF_URL,
            params=params,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        items = data["message"]["items"]

        return items

    except Exception as e:

        print(f"Crossref error: {e}")

        return []


# ============================================================
# FIND BEST MATCH
# ============================================================

def find_best_match(title, year):

    results = search_crossref(title, year)

    if not results:

        return None

    best = None
    best_score = 0

    for item in results:

        crossref_titles = item.get("title", [])

        if not crossref_titles:
            continue

        crossref_title = crossref_titles[0]

        score = similarity(
            title,
            crossref_title
        )

        # Year check
        year_match = False

        published = item.get("published-print") or \
                    item.get("published-online") or \
                    item.get("issued")

        if published:

            try:

                crossref_year = published["date-parts"][0][0]

                if year and crossref_year == year:
                    year_match = True

            except Exception:
                pass

        # Slight bonus when publication year matches
        adjusted_score = score

        if year_match:
            adjusted_score += 0.03

        if adjusted_score > best_score:

            best_score = adjusted_score

            best = {
                "doi": item.get("DOI"),
                "title": crossref_title,
                "score": score,
                "adjusted_score": adjusted_score,
                "year_match": year_match,
                "publisher": item.get("publisher", ""),
                "type": item.get("type", "")
            }

    return best


# ============================================================
# CONFIDENCE CLASSIFICATION
# ============================================================

def classify_match(result):

    if result is None:
        return "NOT FOUND"

    score = result["adjusted_score"]

    if score >= HIGH_CONFIDENCE:

        return "VERIFIED"

    elif score >= MEDIUM_CONFIDENCE:

        return "REVIEW"

    else:

        return "LOW CONFIDENCE"


# ============================================================
# ADD DOI TO LATEX
# ============================================================

def add_doi_to_entry(entry, doi):

    if not doi:
        return entry

    doi_line = (
        f"[Online]. Available: "
        f"\\url{{https://doi.org/{doi}}}"
    )

    # If DOI already exists, don't duplicate
    if "doi.org/" in entry.lower():

        return entry

    # Remove trailing whitespace
    entry = entry.rstrip()

    # Ensure period
    if not entry.endswith("."):
        entry += "."

    entry += " " + doi_line

    return entry


# ============================================================
# MAIN
# ============================================================

def main():

    input_path = Path(INPUT_FILE)

    if not input_path.exists():

        print(
            f"ERROR: Cannot find {INPUT_FILE}"
        )

        return

    text = input_path.read_text(
        encoding="utf-8"
    )

    references = extract_bibitems(text)

    print("=" * 70)
    print("DOI EXTRACTION STARTED")
    print("=" * 70)

    print(
        f"References detected: {len(references)}"
    )

    results = []

    updated_references = []

    already_have = 0
    verified = 0
    review = 0
    not_found = 0

    for index, ref in enumerate(references, start=1):

        key = ref["key"]
        entry = ref["text"]

        title = extract_title(entry)
        year = extract_year(entry)

        existing_doi = extract_existing_doi(entry)

        print()
        print(
            f"[{index}/{len(references)}] {key}"
        )

        print(
            f"Title: {title}"
        )

        # ----------------------------------------------------
        # Already has DOI
        # ----------------------------------------------------

        if existing_doi:

            print(
                f"Already has DOI: {existing_doi}"
            )

            already_have += 1

            results.append({
                "number": index,
                "bibkey": key,
                "title": title,
                "year": year,
                "doi": existing_doi,
                "match_score": 1.0,
                "year_match": True,
                "status": "ALREADY PRESENT",
                "source_title": "",
                "publisher": ""
            })

            updated_references.append(entry)

            continue

        # ----------------------------------------------------
        # Search Crossref
        # ----------------------------------------------------

        if not title:

            print("Could not extract title.")

            not_found += 1

            results.append({
                "number": index,
                "bibkey": key,
                "title": "",
                "year": year,
                "doi": "",
                "match_score": 0,
                "year_match": False,
                "status": "TITLE NOT FOUND",
                "source_title": "",
                "publisher": ""
            })

            updated_references.append(entry)

            continue

        result = find_best_match(
            title,
            year
        )

        time.sleep(
            REQUEST_DELAY
        )

        # ----------------------------------------------------
        # No match
        # ----------------------------------------------------

        if result is None:

            print("DOI not found.")

            not_found += 1

            results.append({
                "number": index,
                "bibkey": key,
                "title": title,
                "year": year,
                "doi": "",
                "match_score": 0,
                "year_match": False,
                "status": "NOT FOUND",
                "source_title": "",
                "publisher": ""
            })

            updated_references.append(entry)

            continue

        # ----------------------------------------------------
        # Classify
        # ----------------------------------------------------

        status = classify_match(result)

        doi = result["doi"]

        print(
            f"DOI: {doi}"
        )

        print(
            f"Similarity: "
            f"{result['adjusted_score']:.3f}"
        )

        print(
            f"Status: {status}"
        )

        if status == "VERIFIED":

            verified += 1

            # Automatically add DOI
            updated_entry = add_doi_to_entry(
                entry,
                doi
            )

        elif status == "REVIEW":

            review += 1

            # Add DOI but mark for manual review
            updated_entry = add_doi_to_entry(
                entry,
                doi
            )

        else:

            not_found += 1

            updated_entry = entry

        updated_references.append(
            updated_entry
        )

        results.append({
            "number": index,
            "bibkey": key,
            "title": title,
            "year": year,
            "doi": doi or "",
            "match_score": round(
                result["adjusted_score"],
                4
            ),
            "year_match": result["year_match"],
            "status": status,
            "source_title": result["title"],
            "publisher": result["publisher"]
        })

    # ========================================================
    # REBUILD LATEX
    # ========================================================

    output_text = text

    for ref, updated in zip(
        references,
        updated_references
    ):

        output_text = output_text.replace(
            ref["text"],
            updated,
            1
        )

    Path(
        OUTPUT_FILE
    ).write_text(
        output_text,
        encoding="utf-8"
    )

    # ========================================================
    # WRITE CSV REPORT
    # ========================================================

    fieldnames = [
        "number",
        "bibkey",
        "title",
        "year",
        "doi",
        "match_score",
        "year_match",
        "status",
        "source_title",
        "publisher"
    ]

    with open(
        REPORT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            results
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("DOI EXTRACTION COMPLETE")
    print("=" * 70)

    print(
        f"Total references:     {len(references)}"
    )

    print(
        f"Already had DOI:      {already_have}"
    )

    print(
        f"Verified automatically:{verified}"
    )

    print(
        f"Needs manual review:  {review}"
    )

    print(
        f"Not found:            {not_found}"
    )

    print()
    print(
        f"Created: {OUTPUT_FILE}"
    )

    print(
        f"Created: {REPORT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()