# Vertical Farm AI Assistant

An educational Streamlit prototype combining plant photo analysis with environmental screening.

## Run on Windows (VS Code PowerShell)

```powershell
cd VerticalFarmAI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, skip activation and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Live AI

Enter your own OpenAI API key in the app when prompted, or set the `OPENAI_API_KEY` environment variable. API usage may incur charges. Never publish your key in code or screenshots. Without a key, environmental screening still works, but photo analysis does not.

## Technical approach

- Pretrained vision-language model: GPT-4.1 mini via OpenAI Responses API (image + text)
- Rule-based environmental flags, not an ML prediction
- VPD calculated from air temperature and relative humidity
- No training dataset, custom-trained model, or measured classification accuracy

## Suggested demo

1. Show sliders and VPD changes.
2. Upload a clear lettuce leaf photo.
3. Enter a symptom note and a valid API key.
4. Click Analyze plant health and explain uncertainty in the report.
5. Discuss limitations: image ambiguity, lighting, lack of leaf temperature and lab confirmation.
