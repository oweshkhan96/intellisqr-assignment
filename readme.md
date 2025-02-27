Overview
This project is designed to extract key financial entities from PDF documents using a hybrid approach. The solution combines robust text extraction (using pdfplumber) with heuristic regex-based extraction and leverages an open-source LLM (LLaMA 3.1 via the Ollama API) to format the extracted data into a structured JSON format. This approach is designed to be extensible for future PDFs with similar layouts.

The key financial entities extracted include:

Company Name
Report Date
Profit Before Tax
(Bonus) Additional Financial Details such as Revenue from Operations, Earnings Per Share (EPS), etc.

How It Works
Text Extraction:
The script uses pdfplumber to extract all the text content from each PDF document.

LLM Extraction:
The extracted text is sent to LLaMA 3.1 (via the Ollama API) with a carefully crafted prompt instructing the model to extract key financial entities and return the results in strict JSON format.

Fallback Extraction:
If LLaMA fails to return valid JSON (or returns empty values), the script uses regex-based heuristics to extract:

Company Name (based on keywords)
Report Date (by matching common date patterns)
Profit Before Tax (by capturing the first numeric value following the phrase "Profit before tax")
This ensures that even if the LLM output is unreliable, the system can still provide accurate extraction using direct text processing.

Output:
The final extracted data is structured as JSON and saved to a file (extracted_financial_entities.json). This file contains key-value pairs for each PDF processed.


Install the required packages using pip:

pip install pdfplumber ollama
LLaMA 3.1 Setup
Ensure you have access to the Ollama API with LLaMA 3.1 installed.
Verify your Ollama configuration so that the model can be invoked using:
```
ollama.chat(model="llama3.1", messages=[...])
```

Usage

Prepare Your PDFs:
Place your PDF files in a directory and update the PDF_FILES list in the script (main.py) with the appropriate file paths.

Run the Script: Execute the script by running:
```
python main.py
```
Output:
The script will process each PDF, extract the required financial entities, and save the structured data in extracted_financial_entities.json. The results are also printed to the console.

Expected Output Format
The JSON output file will have a structure similar to:


{
    "1_FinancialResults_05022025142214.pdf": {
        "company_name": "Eveready Industries India Ltd.",
        "report_date": "December 31, 2024",
        "profit_before_tax": "₹15.88 Crores",
        "additional_details": {
            "revenue_from_operations": "₹333.50 Crores",
            "eps": "₹1.80"
        }
    },
    "Amaar raja Earnings Summary.pdf": {
        "company_name": "Amara Raja Energy & Mobility Limited",
        "report_date": "November 04, 2024",
        "profit_before_tax": "₹323.97 Crores",
        "additional_details": {
            "revenue_from_operations": "₹3250.73 Crores",
            "eps": "₹12.87"
        }
    }
}
Note: The actual extracted values depend on the content and formatting of your PDFs.

Extensibility
Adding More PDFs:
To process additional PDFs, simply add their file paths to the PDF_FILES list in the script.

Improving Extraction:
You can fine-tune the regex patterns or adjust the prompt sent to LLaMA 3.1 for better accuracy with different document formats.

LLM Integration:
The system leverages LLaMA 3.1 for formatting. If needed, the prompt can be further refined to handle more complex extraction scenarios.