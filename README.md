# Financial Analysis App

This project provides a web application for conducting financial analysis on companies. Users can enter a company ticker symbol, and the application will download relevant financial 10K filings, perform sentiment analysis (using finBERT), and display the results in a bar chart (matplotlib).
Note: The insights gained dealt with analyzing the sentiment around company profits, as these features would tell me more about the financial health and performance of a company.
With more time/compute power, I would love to implement this utilizing a sliding window approach to tokenization, as Hugging Face's API could only allow for 512 tokens per API call and I was hitting the limit very quickly. 

- **DEMO**: https://youtu.be/qG9Rq3Hi-1c
## Tech Stack

The project utilizes the following technologies:

- **Python**: The backend server is implemented in Python using the Flask framework. Python is chosen for its simplicity and flexibility.
  
- **Flask**: Flask is a lightweight web framework for Python. It's chosen for its simplicity and ease of use in building web applications.

- **Hugging Face Transformers**: I utilized finBERT (Bidirectional Encoder Representations from Transformers) from Hugging Face, to perform sentiment analysis. I chose it as it is trained on a large corpus of financial documents and reports.

- **matplotlib**: Matplotlib is a plotting library for Python. It's used to generate bar charts displaying sentiment analysis results.

- **HTML/CSS/JavaScript**: The frontend of the application is built using HTML, CSS, and JavaScript. HTML for structuring the content, CSS for styling, and JavaScript for dynamic behavior such as handling form submissions and displaying progress messages.


## How to Run

To run the application locally, follow these steps:

1. Install Python 3.x if you haven't already.

2. Clone this repository to your local machine.

   ```bash
   git clone https://github.com/Krish-Mathur/FinTech.git
   ```
3. navigate to the project directory
   ```bash
   cd FinTech
   ```
4. Install the required Python packages using pip.
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Flask application.
   ```bash
   python app.py
   ```
6. Navigate to http://localhost:5000 to access the application.
