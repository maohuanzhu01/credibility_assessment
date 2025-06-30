import os
import uuid
import json
import threading

from flask import Flask, request, jsonify, send_from_directory
import pdfplumber
import openai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store progress and results per session
progress = {}
results = {}
total_questions = {}

OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview')
QUESTIONS_FILE = 'questions.json'
openai.api_key = os.getenv('OPENAI_API_KEY')

def evaluate(session_id: str, text: str) -> None:
    """Evaluate the PDF text against the questions file."""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    total_questions[session_id] = len(questions)
    progress[session_id] = 0
    res = []
    for q in questions:
        prompt = (
            f"Rispondi alla seguente domanda basandoti sul documento:\n{q['text']}\n\n"
            f"Documento:\n{text}"
        )
        try:
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            answer_raw = response.choices[0].message.content.strip().lower()
        except Exception:
            answer_raw = ''
        if 'si' in answer_raw:
            answer = 'Si'
            score = 1
        elif 'no' in answer_raw:
            answer = 'No'
            score = 0
        else:
            answer = 'Informazioni insufficienti'
            score = 0
        res.append({'question': q['text'], 'answer': answer, 'score': score})
        progress[session_id] += 1
    results[session_id] = res

@app.route('/upload', methods=['POST'])
def upload():
    """Receive PDF, start background assessment, return session id."""
    file = request.files.get('pdf')
    if not file:
        return jsonify({'error': 'No PDF uploaded'}), 400
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    with pdfplumber.open(filepath) as pdf:
        text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
    session_id = str(uuid.uuid4())
    thread = threading.Thread(target=evaluate, args=(session_id, text))
    thread.start()
    return jsonify({'session_id': session_id})

@app.route('/status/<session_id>')
def status(session_id: str):
    """Return progress information for the given session."""
    total = total_questions.get(session_id, 0)
    completed = progress.get(session_id, 0)
    finished = session_id in results
    data = {'total': total, 'completed': completed, 'finished': finished}
    if finished:
        data['results'] = results[session_id]
    return jsonify(data)

@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
