# app.py
from flask import Flask, render_template, request
import pandas as pd
from match_engine import recommend

app = Flask(__name__)

# Load internships CSV at startup
DATA_PATH = 'internships.csv'
raw_df = pd.read_csv(DATA_PATH, dtype=str).fillna('')
internships = raw_df.to_dict(orient='records')


@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    submitted = False

    if request.method == 'POST':
        submitted = True
        education = request.form.get('education', '')
        sector = request.form.get('sector', '')
        state = request.form.get('state', '')
        remote_pref = request.form.get('remote', 'no') == 'yes'
        skills = request.form.getlist('skills')

        user_profile = {
            'education': education,
            'sector': sector,
            'state': state,
            'remote': remote_pref,
            'skills': skills
        }

        results = recommend(user_profile, internships, top_n=5)

    # For the simple UI, provide lists for selects
    education_levels = ['10th', '12th', 'Diploma', 'UG', 'PG', 'PhD']
    sample_skills = sorted(list({s.strip() for s in ';'.join(raw_df['skills'].astype(str)).split(';') if s.strip()}))
    sectors = sorted(list({s.strip() for s in raw_df['sector'].astype(str) if s.strip()}))

    return render_template(
        'index.html',
        education_levels=education_levels,
        sample_skills=sample_skills,
        sectors=sectors,
        results=results,
        submitted=submitted
    )


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)