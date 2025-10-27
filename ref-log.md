Use AI help handle PDF reading.
```
if file_obj.name.endswith(".pdf"):
    try:
        pdf_bytes = file_obj.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                content += page_text + "\n"
    except Exception as e:
        print("PDF read error")
        continue 
```