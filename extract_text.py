# extract_text.py
import pdfplumber


def extract_text_from_pdf(path: str) -> str:
    full_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n\n".join(full_text)


if __name__ == "__main__":
    text = extract_text_from_pdf("The-Global-50-2025-Eng.pdf")
    with open("full_text.txt", "w", encoding="utf8") as out:
        out.write(text)
    print("Text extraction complete.")
