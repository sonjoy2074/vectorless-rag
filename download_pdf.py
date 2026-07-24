import os
import requests

pdf_url= "https://arxiv.org/pdf/2501.12948.pdf"
pdf_path=os.path.join("../data", pdf_url.split('/')[-1])


os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

response = requests.get(pdf_url)
with open(pdf_path, 'wb') as f:
    f.write(response.content)

print(f"Downloaded PDF from {pdf_url} to {pdf_path}")