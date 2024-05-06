from flask import Flask, render_template, request, jsonify
import os
from downloader import download_10k_filings, analyze_most_recent_10k_filing, perform_sentiment_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import uuid

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_ticker', methods=['POST'])
def process_ticker():
    ticker = request.form['ticker']
    save_directory = os.path.join(os.getcwd(), ticker)
    os.makedirs(save_directory, exist_ok=True)
    
    progress_messages = []  # List to store progress messages
    
    # Download 10-K filings and yield progress messages
    for progress_message in download_10k_filings(ticker, save_directory):
        progress_messages.append(progress_message)
    
    # Analyze most recent 10-K filing
    analyze_most_recent_10k_filing(ticker, save_directory)
    
    # Perform sentiment analysis on financial results
    extracted_text_path = os.path.join(save_directory, "extracted_text.txt")
    if os.path.exists(extracted_text_path):
        with open(extracted_text_path, 'r', encoding='utf-8') as file:
            text = file.read()
        sentiment_analysis_result = perform_sentiment_analysis(text)
        if sentiment_analysis_result:
            labels = [entry['label'] for entry in sentiment_analysis_result[0]]
            scores = [entry['score'] for entry in sentiment_analysis_result[0]]
            
            # Clear existing plot
            plt.clf()
            
            # Create the bar chart
            plt.bar(labels, scores)
            plt.xlabel('Sentiment Label')
            plt.ylabel('Sentiment Score')
            plt.title('Sentiment Analysis Result')
            
            # Generate a unique filename for the plot
            plot_filename = str(uuid.uuid4()) + '.png'
            
            # Save the chart to a file
            plot_filepath = os.path.join(save_directory, plot_filename)
            plt.savefig(plot_filepath, format='png')
            
            # Encode the plot image to base64
            with open(plot_filepath, 'rb') as file:
                plot_image_data = base64.b64encode(file.read()).decode('utf-8')
            
            # Return the result, progress messages, and plot image
            return jsonify({'result': 'Analysis completed', 'progress_messages': progress_messages, 'plot_image': plot_image_data})
        else:
            return jsonify({'result': 'Sentiment analysis failed', 'progress_messages': progress_messages})
    else:
        return jsonify({'result': 'No extracted text file found', 'progress_messages': progress_messages})

if __name__ == '__main__':
    app.run(debug=True)
