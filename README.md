### Replication package

This folder contains the replication materials for the thesis _Cracks in the Platform: Detecting Inconsistencies and Workarounds in Low-Code Applications_ by MohammadAmin Zaheri. It includes the experimental applications and datasets (Chapter 5), the LLM prompts, outputs, and calibrations (Chapter 6), and the assessment artifacts (Chapter 7).

### Prerequisites
- Python 3.11.7
- Windows 11 (tested platform; apps use Tk/CustomTkinter)
- Install dependencies:
```bash
pip install customtkinter==5.2.2 tkcalendar pillow
```

### Layout
- `ch5/`
  - `code/`: TA apps (Open/Predetermined/Controlled), HR app, REG app, common widgets, and themes/icons
  - `data/`: HR/REG/TA datasets (chunked CSVs)
  - `instructions/`: task PDFs for each app
  - `exit_survey.xlsx`, `stat_tests.xlsx`, `user_workaround_data.csv`
- `ch6/`
  - `prompts/`: prompt-emp.txt, prompt-conf.txt
  - `LLM-results/`: model-specific outputs for employee and conference tasks 
  - `calibrations/`: calibration spreadsheets
  - `workarounds_assessment-v3.xlsx`
- `ch7/`
  - `instructions/`: assessment PDFs
  - `llm-mapping.txt`, `user-study-results.xlsx`

### Run the Chapter 5 apps
1) Open a terminal and change directory so assets resolve correctly:
```bash
cd material/rep/ch5/code
```
2) Launch an app:
```bash
python ta1.py    # TA - Open
python ta2.py    # TA - Predetermined
python ta3.py    # TA - Controlled
python hr.py     # HR
python reg.py    # REG
```
3) Follow the corresponding PDF in `material/rep/ch5/instructions`.
4) Logs and saved data will appear under `m_*/logs/<user_name>/` created at runtime.

Note: The datasets intentionally contain fields that do not map 1:1 to the forms (e.g., TA "Bonus", multi-valued topics in REG, multiple phone numbers in HR) to elicit user workarounds.

### LLM prompts and outputs (Chapter 6)
- Prompts are in `material/rep/ch6/prompts/`.
- Model outputs are provided under `material/rep/ch6/LLM-results/<Model>/` (separate files for employee and conference tasks).
- Calibration sheets are in `material/rep/ch6/calibrations/`.
- Re-running can yield different outputs; the provided files enable verification.