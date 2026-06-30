import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("AQ.Ab8RN6KG1UAuYV1UiCTCfrgyEPfj8axQj4otVVFVPcxVTc0NPQ"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_plan(tasks):

    prompt = f"""
You are an AI Productivity Coach.

Analyze these tasks:

{tasks}

Return ONLY clean HTML (no markdown, no ```html).

Format:

<h2>🎯 Priority Task</h2>
<p>Which task should be completed first and why (2-3 lines).</p>

<h2>📅 Today's Plan</h2>
<ul>
<li>Task 1 (estimated time)</li>
<li>Task 2 (estimated time)</li>
<li>Break reminder</li>
</ul>

<h2>💡 Productivity Tips</h2>
<ul>
<li>3 short tips only</li>
</ul>

<h2>🔥 Motivation</h2>
<p>One motivational sentence.</p>

Rules:
- Keep the response under 200 words.
- Be concise.
- Don't repeat the task list.
- Don't explain obvious things.
"""
    response = model.generate_content(prompt)

    return response.text