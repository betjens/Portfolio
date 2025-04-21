# PDF text as a Resume

Read PDFs and gets resumes out of it.

You need ollama in your local machine running. Check this page on how you can get it up. https://ollama.com/

If you already have it installed, then you can just start it up.

```
ollama run gamma3:1b
```

Before running the code, you might need t check the library to use. See below chart to make your selection.

# What library is good for me?

| Feature | pdfplumber | PyMuPDF |
|---------| -----------|----------|
| Text accuracy | ✅ better for complex layout | 👌 fast and good for simple layout |
|Table extraction | ✅ excellent | ❌ limited|
|Layout awareness | ✅ yes | ✅ partial|
|Speed | 🐢 slower | ⚡ faster|
|Images/graphics | ❌ not ideal | ✅ better support|

You will need to update the function `extract_text_from_pdf` to work with the library of election.

Install `requirements.txt` and run the code.