import os
import requests
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
import re
from transformers import BertTokenizer
import time
# Initialize the tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
API_TOKEN = "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"  # Replace with your actual API token

def download_10k_filings(ticker, save_directory):
    dl = Downloader("YourCompanyName", "your.email@example.com", save_directory)

    for year in range(1995, 2024):
        try:
            dl.get("10-K", ticker, after=f"{year}-01-01", before=f"{year+1}-01-01", download_details=False)
            yield f"Downloaded 10-K filing for {ticker} in {year}"
        except Exception as e:
            yield f"Failed to download 10-K filing for {ticker} in {year}: {e}"

def extract_financial_results(html_content, save_directory):
    try:
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all text elements
        text_elements = soup.find_all(text=True)
        
        # Filter out non-textual elements (e.g., scripts, styles)
        text_content = [elem.strip() for elem in text_elements if elem.parent.name not in ['script', 'style']]
        
        # Join text content into a single string
        plain_text = ' '.join(text_content)
        
        # Remove any remaining HTML tags
        plain_text = re.sub(r'<[^>]+>', '', plain_text)
        
        # Extract sentences containing "net sales"
        sentences = [sentence.strip() for sentence in plain_text.split('.') if "profit" in sentence.lower()]
        
        # Join filtered sentences into a single string
        filtered_text = ' '.join(sentences)
        
        # Keep periods and percent symbols
        filtered_text = re.sub(r'[^a-zA-Z0-9\s.%$]', '', filtered_text)
        
        # Remove extra whitespace
        filtered_text = ' '.join(filtered_text.split())
        
        # Construct the filename
        filename = os.path.join(save_directory, "extracted_text.txt")
        
        # Save filtered text to the TXT file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(filtered_text)
        
        return filtered_text
    
    except Exception as e:
        print(f"Error extracting financial results: {e}")
        return None


def perform_sentiment_analysis(text):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # Tokenize the input text
    tokens = tokenizer.tokenize(text)
    
    # Truncate the tokens to fit within the maximum sequence length
    max_seq_length = 510
    truncated_tokens = tokens[:max_seq_length]
    
    # Convert the truncated tokens back to text
    truncated_text = tokenizer.convert_tokens_to_string(truncated_tokens)
    
    print(truncated_text)
    max_retries = 3
    retries = 0
    
    # Retry until the model is loaded or max retries reached
    while retries < max_retries:
        response = requests.post(API_URL, headers=headers, json={"inputs": truncated_text, "wait_for_model": True})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Retry if rate limited
            retry_after = response.headers.get('Retry-After', 5)  # Default wait time of 5 seconds
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            retries += 1
        else:
            print(f"Error: {response.status_code}. Retrying...")
            time.sleep(5)  # Retry after 5 seconds
            retries += 1
    
    return {"error": "Failed to perform sentiment analysis"}

def analyze_most_recent_10k_filing(ticker, save_directory):
    source_directory = os.path.join(save_directory, "sec-edgar-filings", ticker, "10-K")
    latest_filing = None
    latest_time = 0
    
    for root, dirs, _ in os.walk(source_directory):
        for directory in dirs:
            if "-23-" in directory:  # Check if the year "-23-" is in the directory name
                filing_path = os.path.join(root, directory, "full-submission.txt")
                file_time = os.path.getctime(filing_path)
                if file_time > latest_time:
                    latest_time = file_time
                    latest_filing = filing_path
    
    if latest_filing:
        print("Latest 10-K filing content:")
        with open(latest_filing, 'r', encoding='utf-8') as f:
            html_content = f.read()
        financial_results = extract_financial_results(html_content, save_directory)  # Pass save_directory here
        if financial_results:
            print("Performing sentiment analysis on the most recent 10-K filing...")
            time.sleep(5)
            sentiment_analysis_result = perform_sentiment_analysis(financial_results)
            if sentiment_analysis_result:
                return sentiment_analysis_result
            else:
                print("Sentiment analysis failed.")
        else:
            print("Failed to extract financial results from the most recent 10-K filing.")
    else:
        print("No 10-K filing found for sentiment analysis.")

# Example usage

if __name__ == "__main__":
    ticker = input("Enter the company ticker: ")
    script_directory = os.getcwd()  # Get the current working directory
    save_directory = os.path.join(script_directory, ticker)  # Create a directory path to save the filings
    os.makedirs(save_directory, exist_ok=True)  # Create the directory if it doesn't exist
    download_10k_filings(ticker, save_directory)
    analyze_most_recent_10k_filing(ticker, save_directory)
