import pdfplumber
import ollama
import asyncio


pdf_path = "pdf_sample_files\A Brief Tour of Generative AI on Google Cloud.pdf"
model="gemma3:1b" #<Your LLM name>
init_prompt= """
You are an expert GCP professional Machine Learning. 
You are trying to study for your next certification and needs to read a lot of pdfs. 
You want to get that information simplified and simplified. 
Output should be in markdown.

Content: {content}
"""


def extract_text_from_pdf(pdf_path):
    # using pdfplumber
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
    return "\n".join(all_text)


async def analyze_resume_with_ollama(resume_text):
    prompt = init_prompt.format(content=resume_text)

    print("##########################################")
    output = ""
    for response in ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        output += response['message']['content']
    print(output)


async def main():
    # Step 1: Extract text from the PDF
    resume_text = extract_text_from_pdf(pdf_path)
    # Step 2: Analyze resume using Ollama
    await analyze_resume_with_ollama(resume_text)


if __name__ == "__main__":
    asyncio.run(main())
