from dotenv import load_dotenv
import os
import json
import requests
import asyncio
from pageindex import PageIndexClient
import pageindex.utils as utils

load_dotenv()

#Interface with PageIndex client
PAGEINDEX_API_KEY  = os.getenv("PAGEINDEX_API_KEY")

pi_client = PageIndexClient(api_key=PAGEINDEX_API_KEY)

#Download the pdf document 

ROOT_DIR = path(__file__).resolve().parent.parent

pdf_url = "https://arxiv.org/pdf/2305.10403.pdf"
pdf_path = ROOT_DIR / "data" / pdf_url.split("/")[-1]


pdf_path.parent.mkdir(parents=True, exist_ok=True)

response = requests.get(pdf_url)
with open(pdf_path, "wb") as f:
    f.write(response.content)

print(f"Downloaded PDF to {pdf_path}")

#step 5: Upload the PDF to PageIndex

doc_info = pi_client.upload_document(pdf_path)
doc_id = doc_info["document_id"]
print(f"Uploaded document to PageIndex with ID: {doc_id}")


#step 6: create an index

import time

print(f"waiting for index to be created for document ID: {doc_id}")

max_retries = 30
retry_count = 0

while not pi_client.is_retrieval_ready(doc_id):
    if retry_count >= max_retries:
        print("Timeout: Index not ready after maximum retries.")
        break
    print(f"Index not ready yet. Retrying in 5 seconds... (Attempt {retry_count + 1}/{max_retries})")
    time.sleep(5)
    retry_count += 1

if pi_client.is_retrieval_ready(doc_id):
    print("Success! Document is ready for retrieval.")
    tree_info = pi_client.get_document_tree(doc_id)
    utils.print_tree(tree_info)

else:
    tree= None

#step 7: initialize the LLM 

from langchain.chat_models import chatGoogleGennerativeAI

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
)

#Step 8: Define Retrieval Function(Vectorless Retrieval)


def retrieve_answer(query, doc_id):

    response = pi_client.submit_query(doc_id, query)
    retrieval_id = response["retrieval_id"]

    if not retrieval_id:
        print("Error: Retrieval ID not found in the response.")
        return None
    while True:
        response = pi_client.get_retrieval_status(doc_id, retrieval_id)
        status = response.get("status")

        if status == "completed":
            break
        elif status == "failed":
            return []
        
        time.sleep(1)

    nodes = response.get("retrieved_nodes", [])
    context = []

    nodes = retrieval.get("retrieved_nodes", [])
    contexts = []

    for node in nodes[:top_k]:
        relevant_contents = node.get("relevant_contents", [])
        
        for group in relevant_contents:
            for item in group:
                content = item.get("relevant_content")
                if content:
                    contexts.append(content)

    return contexts


