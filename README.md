# credibility_assessment

Simple Flask application to evaluate a Transition Plan PDF against a list of
questions using the OpenAI API. Results are scored according to the answers
returned by the model.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide your OpenAI API key as environment variable `OPENAI_API_KEY` before
   running the app:
   ```bash
   export OPENAI_API_KEY=YOUR_KEY
   ```
3. Start the server:
   ```bash
   python app.py
   ```

## Usage

1. Open `http://localhost:5000` in your browser.
2. Upload a PDF (max 5 MB) containing the Transition Plan.
3. Click **Start Enhanced Assessment**. The application processes each question
   from `questions.json`, calls the OpenAI API and displays progress while the
   assessment is running. When finished, the answers and scores are listed.

The file `questions.json` contains the list of questions and can be replaced
with your own.
