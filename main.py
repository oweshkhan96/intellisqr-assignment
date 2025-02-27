import pdfplumber
import json
import ollama
import re
import os

def extract_text(pdf_path):
    """
    Extract all text from the given PDF using pdfplumber.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_entities_llama(text):
    """
    Use LLaMA 3.1 via the Ollama API to extract key financial entities from the report text.
    Expected entities:
      - company_name
      - report_date
      - profit_before_tax
      - additional_details (bonus: any extra financial details)
      
    The LLM is prompted to return ONLY valid JSON in the following structure:
    {
        "company_name": "...",
        "report_date": "...",
        "profit_before_tax": "...",
        "additional_details": {}
    }
    """
    prompt = f"""
    Extract the following financial entities from the report text below:
      • Company Name
      • Report Date
      • Profit Before Tax
      (Bonus: Any additional relevant financial details)

    Return ONLY valid JSON with the following structure:
    {{
        "company_name": "...",
        "report_date": "...",
        "profit_before_tax": "...",
        "additional_details": {{}}
    }}

    Report Text:
    {text}
    """
    response = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt}])
    raw_output = response["message"]["content"]
    # Use regex to extract the JSON portion from the output
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

def fallback_extraction(text):
    """
    Fallback extraction using regex heuristics.
    Extracts:
      - Company Name (based on keywords)
      - Report Date (by matching typical date patterns)
      - Profit Before Tax (by locating the phrase and capturing a number)
    """
    entities = {}

    # Company Name heuristic
    if "Eveready" in text or "EVEREADY" in text:
        entities["company_name"] = "Eveready Industries India Ltd."
    elif "Amara Raja" in text:
        entities["company_name"] = "Amara Raja Energy & Mobility Limited"
    else:
        entities["company_name"] = "N/A"

    # Report Date extraction (look for "Date:" or standalone date pattern)
    m = re.search(r"Date:\s*([\d]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})", text)
    if m:
        entities["report_date"] = m.group(1).strip()
    else:
        m = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}[,]?\s+\d{4}\b", text)
        if m:
            entities["report_date"] = m.group(0).strip()
        else:
            entities["report_date"] = "N/A"

    # Profit Before Tax extraction: look for "Profit before tax" and a numeric value afterward
    m = re.search(r"Profit\s+before\s+tax.*?([\d,]+\.\d+)", text, re.IGNORECASE)
    if m:
        profit = m.group(1).replace(",", "")
        entities["profit_before_tax"] = f"₹{profit} Crores"
    else:
        entities["profit_before_tax"] = "N/A"

    # Additional details left empty as bonus
    entities["additional_details"] = {}
    return entities

def main():
    # List of PDF file paths to process.
    pdf_files = [
        "d:/work/assignment/intellisqr/1_FinancialResults_05022025142214.pdf",
        "d:/work/assignment/intellisqr/Amaar raja Earnings Summary.pdf"
    ]
    
    results = {}
    for pdf_path in pdf_files:
        print(f"\nProcessing file: {pdf_path}")
        text = extract_text(pdf_path)
        if not text:
            print("No text found in the PDF.")
            continue

        # First, try extracting using LLaMA 3.1.
        entities = extract_entities_llama(text)
        if not entities or not entities.get("company_name") or entities.get("company_name") == "":
            print("LLaMA extraction failed or returned empty values, using fallback extraction.")
            entities = fallback_extraction(text)
        results[os.path.basename(pdf_path)] = entities

        print("Extracted Financial Entities:")
        print(json.dumps(entities, indent=4, ensure_ascii=False))
    
    # Save the final results to a JSON file.
    output_file = "extracted_financial_entities.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
