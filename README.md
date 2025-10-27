## Files Handle

Use 'accept_multiple_files=True' and
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
to allow multi-files uploded

And monitor file change to synchronize the RAG vector collection

## RAG 
### 1. Spliter

Use recursive segmentation 'separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]' to seperate files, making chunks keep semantic information with appropriate size.

### 2. Retrieve

Use MMR method to retrieve chunks. It first retrive 20 chunks and sort by the similarity, then select the 5 most unsimilarity chunks. In order to make the retrieve method more resonable.