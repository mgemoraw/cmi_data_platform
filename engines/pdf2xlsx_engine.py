import pdfplumber
import pandas as pd

# Open the PDF file and extract text/tables page by page
pdf_path = "03_04_2017_E_C_Excavator_Productivity_By_Cherinet_Bisetegn_.pdf"

# We will collect all structured data extracted from the document
all_pages_data = []

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        if tables:
            for table in tables:
                df = pd.DataFrame(table)
                df["Source_Page"] = i + 1
                all_pages_data.append(df)
        else:
            # Fallback to extracted text lines if tables are not explicitly detected
            text = page.extract_text()
            if text:
                lines = [line.split() for line in text.split("\n")]
                df = pd.DataFrame(lines)
                df["Source_Page"] = i + 1
                all_pages_data.append(df)

# Combine into a master dataframe
if all_pages_data:
    master_df = pd.concat(all_pages_data, ignore_index=True)
    # Save to Excel format
    master_df.to_excel("Excavator_Productivity_Data.xlsx", index=False)