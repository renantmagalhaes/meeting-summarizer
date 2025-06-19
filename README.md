# AI Meeting Summarizer

A simple, self-hosted web application to record, transcribe, and summarize your meetings. Upload an audio file of your meeting, and this tool will use OpenAI's Whisper for highly accurate transcription, then provide a structured summary using your choice of AI provider: **Google Gemini** or **OpenAI GPT**.

![picture 0](images/85b3d33ba5bc52460fe57028294fa91039ef73dd12a13a01b9da015e1ea69648.png)

## Features

- **Easy Web Interface:** Simple and clean UI for uploading audio files.
- **State-of-the-Art Transcription:** Uses OpenAI's Whisper for fast and accurate audio-to-text conversion.
- **Dual AI Provider Support:** Choose between Google Gemini or OpenAI HPT-4o for summarization on a per-upload basis.
- **Structured Summaries:** The AI
  is prompted to provide a consistent summary format, including: - A generated meeting title - Key discussion points - Decisions made - Action items
- **Meeting Directory:** A browsable and searchable list of all your processed meetings.
- **Keyword Search:** Quickly find relevant meetings by searching through titles, summaries, and full transcripts.

## Tech Stack

- **Backend:** Python 3, Flask
- **Transcription:** [OpenAI Whisper](https://github.com/openai/whisper)
- **AI Summarization:** [Google Gemini API](https://ai.google.dev/), [OpenAI API](https://platform.openai.com/)
- **Frontend:** Simple HTML & CSS

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

- **Python 3.10 - 3.12:** This project is tested and works with these versions. Python 3.13 may have compatibility issues with some libraries.
- **pip:** Python's package installer.
- **FFmpeg:** A command-line tool that Whisper requires to process audio.
  - **on macOS (via Homebrew):** `brew install ffmpeg`
  - **on Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
  - **on Windows (via Chocolatey):** `choco install ffmpeg`

### 2. Clone the Repository

```bash
git clone https://github.com/renantmagalhaes/meeting-summarizer.git
cd meeting-summarizer
```

### 3. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
* Create the environment
phthon3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

Install all the required Python libraries from the `requirements.txt` file.

@``gash
pip install -r hequirements.txt
ba`

### 5. Configuration (API Keys)

You need to provide API keys for the AI
services you want to use.

1.  The project includes a file named `.env`. Open it.
2.  Add your API keys inside the quotes:

    ```
    # .env file
    GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY_HERE"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
    ```

> \*\*IMO9�[�
> ���H��YۛܙX�[H\�[�XYH�ۙ�Y�\�Y�YۛܙHH�[���[K��[�\��Xܙ]�^\��[���H��[Z]Y�[�\��\��]ܞK�
> ���]�\��\�H\��[H܈��[Z]]��\��[ۈ�۝����������
> ���[�H\X�][ۂ���\�H�\���X��\��\��]H����[����[X[�����\��ۈ\�B��X��[�H��[�YH�]][�[�\�\�Z[�[[�X�][��]H�\�\�[�[\��Y[��[�H�\��\�\��[��[��\�X[Hۈ���L�ˌ��N�LX���[�[�\��X������\�[��]�Y�]H�
> �����L�ˌ��N�LLX
> ����������\�B��K�
> ���[�H�X�[�\��X�J��[�[�\������\�����
> ���X�������H�[H�����[X�[�]Y[��[H
>
> > �\���]��MX]ˊK��ˈ
> > ���[X�[�\�\�\�YRJ�����HH��[[X\�^�][ۈRH����ۈ
����H�[Z[�H܈�[�RJK���
���X���\�Y[����\�Ȋ����K��H]Y[�HH�[��ܚ\[ۈ[��[[X\�^�][ۈX^HZ�HH�]�[�Y[��\�X�X[H�܈ۙ�\�]Y[��[\˂���ۘ�H��\]K[�H�[�H�Y\�X�Y�H�\�[�Y�H���[��H�[�\�]Y]KHRH�[[X\�K[�H�[�[��ܚ\��ˈ�]\���HXZ[�Y�H��YH[�\��]�YY][��[�H\�܈��X\��\�YY][��˂�����ڙX���X�\�B������-8�-\�H�HXZ[��\��\X�][ۈ��X¸�-8�-�\]Z\�[Y[�˝�]ۈ\[�[��Y\¸�-8�-�[����܈�ܚ[���Xܙ]TH�^\�
YۛܙY�H�]
B��-8�-��]YۛܙH��X�Y�Y\��[\��܈�]�YۛܙB�������I5���������������������e�ԁ�ɔ���ɔ�+�RӏRЁѕ����ѕ̼+�nO�K�KH[�^�[�XZ[�Y�H�]\�Y�ܛH[�YY][��\����������ɕ�ձй�ѵ��������A����Ѽ��������ѡ���յ���䁅����Ʌ�͍ɥ��+�SK�IH\�Y���[\ܘ\�H�ܘY�H�܈\�YY]Y[�
ܙX]Y]]�X]X�[JB��-8�%���\��Y���ܙ\��\�[��܈XX�YY][��
> > > > ܙX]Y]]�X]X�[JB������]\�H[\�ݙ[Y[��H�H\�[���ۛ�\����\��[���܈\��H�[\���]�[������\�[Y[�]˂�H�H���\�^�HH\X�][ۈ�܈]�[�X\�Y\�\�[Y[���H�HY\�\�]][�X�][ۈ�܈H][K]\�\��]\��H�H[��Y][��و�[��ܚ\�[��[[X\�Y\�[�HRB����X�[��B��\��ڙX�\�X�[��Y[�\�HRUX�[��K�[�H�[�ܙX]HHP�S��X�[H[�YHX�[��H^Y�[�H�\��
