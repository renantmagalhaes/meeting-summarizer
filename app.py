import os
import uuid
from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from werkzeug.utils import secure_filename
import whisper
import google.generativeai as genai
import openai
from dotenv import load_dotenv
from datetime import datetime

# --- Configuration ---
load_dotenv()

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'mp4'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = 'supersecretkey'

# --- AI Client Initialization ---
# Configure Gemini API
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    gemini_model = None

# Configure OpenAI API
try:
    openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
except Exception as e:
    print(f"Error configuring OpenAI API: {e}")
    openai_client = None

# Load the Whisper model
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("Whisper model loaded.")


# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_summary_prompt(transcript):
    return f"""
    Please act as a professional meeting assistant. Based on the following transcript,
    provide a response in two parts:

    First, a single-line title for the meeting that summarizes its main purpose.
    The title must start with "Title: ".

    Second, a concise summary of the meeting. The summary must include these three sections:
    1.  **Key Discussion Points:** A bulleted list of the main topics that were discussed.
    2.  **Decisions Made:** A clear list of any final decisions or agreements reached.
    3.  **Action Items:** A list of tasks assigned, including who is responsible if mentioned.

    If a section has no relevant information, state "None."

    ---
    MEETING TRANSCRIPT:
    {transcript}
    ---
    """

def summarize_with_gemini(transcript):
    """Generates summary using Google Gemini."""
    if not gemini_model:
        raise Exception("Gemini model is not configured. Check your GOOGLE_API_KEY.")
    prompt = create_summary_prompt(transcript)
    response = gemini_model.generate_content(prompt)
    return response.text

def summarize_with_openai(transcript):
    """Generates summary using OpenAI GPT."""
    if not openai_client:
        raise Exception("OpenAI client is not configured. Check your OPENAI_API_KEY.")
    prompt = create_summary_prompt(transcript)
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert meeting summarization assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_meeting_details(job_id):
    """Helper to get all metadata for a given meeting ID."""
    meeting_dir = os.path.join(app.config['PROCESSED_FOLDER'], job_id)
    details = {'id': job_id, 'title': job_id, 'date': None, 'summary': '', 'transcript': '', 'provider': 'gemini'}
    try:
        mtime = os.path.getmtime(meeting_dir)
        details['date'] = datetime.fromtimestamp(mtime).strftime('%b %d, %Y')
        with open(os.path.join(meeting_dir, 'title.txt'), 'r') as f: details['title'] = f.read().strip()
        with open(os.path.join(meeting_dir, 'summary.md'), 'r') as f: details['summary'] = f.read()
        with open(os.path.join(meeting_dir, 'transcript.txt'), 'r') as f: details['transcript'] = f.read()
        with open(os.path.join(meeting_dir, 'provider.txt'), 'r') as f: details['provider'] = f.read().strip()
    except FileNotFoundError:
        pass
    return details


# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio_file' not in request.files:
            flash('No file part'); return redirect(request.url)
        file = request.files['audio_file']
        if file.filename == '':
            flash('No selected file'); return redirect(request.url)
        
        ai_provider = request.form.get('ai_provider', 'gemini')
        
        if file and allowed_file(file.filename):
            job_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            try:
                print(f"[{job_id}] Transcribing {filename}...")
                result = whisper_model.transcribe(upload_path, fp16=False)
                transcript = result['text']
                print(f"[{job_id}] Transcription complete.")

                print(f"[{job_id}] Summarizing with {ai_provider.upper()}...")
                if ai_provider == 'openai':
                    full_response_text = summarize_with_openai(transcript)
                else:
                    full_response_text = summarize_with_gemini(transcript)
                print(f"[{job_id}] Summarization complete.")

                title = f"Meeting - {job_id[:8]}"; summary = full_response_text
                lines = full_response_text.split('\n')
                if lines[0].lower().startswith('title:'):
                    title = lines[0][len('title:'):].strip()
                    summary = '\n'.join(lines[1:]).strip()
                
                processed_dir = os.path.join(app.config['PROCESSED_FOLDER'], job_id)
                os.makedirs(processed_dir, exist_ok=True)
                with open(os.path.join(processed_dir, 'transcript.txt'), 'w') as f: f.write(transcript)
                with open(os.path.join(processed_dir, 'summary.md'), 'w') as f: f.write(summary)
                with open(os.path.join(processed_dir, 'title.txt'), 'w') as f: f.write(title)
                with open(os.path.join(processed_dir, 'provider.txt'), 'w') as f: f.write(ai_provider)

            except Exception as e:
                flash(f'An error occurred during processing: {e}'); return redirect(request.url)
            finally:
                if os.path.exists(upload_path): os.remove(upload_path)
            
            return redirect(url_for('view_result', job_id=job_id))

    search_query = request.args.get('q', '').strip()
    all_meeting_ids = sorted(os.listdir(app.config['PROCESSED_FOLDER']), reverse=True)
    meetings_to_display = []
    if search_query:
        for job_id in all_meeting_ids:
            details = get_meeting_details(job_id)
            if (search_query.lower() in details['title'].lower() or
                search_query.lower() in details['summary'].lower() or
                search_query.lower() in details['transcript'].lower()):
                meetings_to_display.append(details)
    else:
        for job_id in all_meeting_ids:
            meetings_to_display.append(get_meeting_details(job_id))

    return render_template('index.html', meetings=meetings_to_display, search_query=search_query)


@app.route('/result/<job_id>')
def view_result(job_id):
    try:
        details = get_meeting_details(job_id)
        if not details.get('summary'): raise FileNotFoundError
        return render_template('result.html', **details)
    except FileNotFoundError:
        flash('Result not found.'); return redirect(url_for('index'))


@app.route('/chat/<job_id>', methods=['POST'])
def chat_with_transcript(job_id):
    """API endpoint to handle chat interactions with a transcript."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request. Message is missing.'}), 400

    user_message = data['message']
    ai_provider = data.get('provider', 'gemini')

    try:
        details = get_meeting_details(job_id)
        transcript = details.get('transcript')
        if not transcript:
            return jsonify({'error': 'Transcript not found.'}), 404

        chat_prompt = f"""
        You are an intelligent meeting assistant. You have been provided with the full transcript of a meeting.
        Your task is to answer the user's question based *only* on the information contained within this transcript.
        Do not make up information. If the answer is not in the transcript, say so.

        ---
        FULL MEETING TRANSCRIPT:
        {transcript}
        ---

        USER'S QUESTION:
        "{user_message}"
        """

        if ai_provider == 'openai' and openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": chat_prompt}]
            )
            ai_response = response.choices[0].message.content
        elif gemini_model:
            response = gemini_model.generate_content(chat_prompt)
            ai_response = response.text
        else:
            return jsonify({'error': f'AI provider {ai_provider} not available.'}), 500

        return jsonify({'reply': ai_response})

    except Exception as e:
        print(f"Error during chat processing: {e}")
        return jsonify({'error': 'An internal error occurred.'}), 500


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    
    app.run(debug=True, host='0.0.0.0', port=port)