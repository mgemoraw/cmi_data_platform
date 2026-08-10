import fitz  # PyMuPDF (no Poppler installation needed)
import easyocr
import pandas as pd
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

class ScannedPDFExtractorEngine:

    def __init__(
        self,
        pdf_path: str,
        output_excel: str = "Extracted_Excavator_Data.xlsx",
    ):
        self.pdf_path = pdf_path
        self.output_excel = output_excel
        # Initialize EasyOCR reader (English)
        print("Initializing OCR engine...")
        self.reader = easyocr.Reader(["en"])

    def run(self):
        doc = fitz.open(self.pdf_path)
        all_pages_data = []

        print(f"Opened PDF with {len(doc)} pages.")

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            print(f"Processing page {page_idx + 1}/{len(doc)} with OCR...")

            # Render page to PNG image bytes in memory (300 DPI for high clarity)
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")

            # Perform OCR on image bytes
            ocr_results = self.reader.readtext(img_bytes, detail=0)

            if ocr_results:
                # Group extracted text/numbers into a row per line
                df = pd.DataFrame(ocr_results, columns=["Extracted_Text"])
                df["Source_Page"] = page_idx + 1
                all_pages_data.append(df)

        if all_pages_data:
            master_df = pd.concat(all_pages_data, ignore_index=True)
            master_df.to_excel(self.output_excel, index=False)
            print(f"Extraction complete! Saved to {self.output_excel}")
            return master_df
        else:
            print("No data could be extracted.")
            return None


if __name__ == "__main__":
    pdf_path = (
        "03_04_2017_E_C_Excavator_Productivity_By_Cherinet_Bisetegn_.pdf"
    )
    extractor = ScannedPDFExtractorEngine(pdf_path)
    extractor.run()