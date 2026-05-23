
from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'math_key'

PROGRESS_FILE = 'progress.json'

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'completed_topics': []}

def save_progress(data):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f)

TOPICS = {
    'mnozice': {
        'name': '📦 Množice (vključno z neenačbami in intervali)',
        'order': 1,
        'theory': '==================== MNOŽICE ====================\n\n📌 KAJ JE MNOŽICA?\nMnožica je zbirka različnih stvari. Tem stvarem rečemo ELEMENTI.\n\n🔤 POMEN SIMBOLOV:\n∈ = "je element"\n∉ = "ni element"\n⊂ = "je podmnožica"\n∅ = prazna množica\n\n🔗 OPERACIJE:\nA ∪ B = unija (vse v A ali B)\nA ∩ B = presek (skupni elementi)\nA \\ B = razlika (v A, ni pa v B)\nA^c = komplement (vse razen A)\n\n==================== INTERVALI ====================\n[2,5] = zaprt (vključno 2 in 5)\n(2,5) = odprt (brez 2 in 5)\n(2,∞) = vsa števila večja od 2\n(-∞,2] = vsa števila manjša ali enaka 2\n\n==================== NEENAČBE ====================\nLinearna: 2x+3 > 7 → x > 2 → (2,∞)\nKvadratna: x²-4 < 0 → -2 < x < 2 → (-2,2)\nAbsolutna: |x-2| < 5 → -3 < x < 7 → (-3,7)',
        'exercises': [
            {'q': 'A = {1,2,3}, B = {3,4,5}. A ∪ B = ?', 'correct': '{1,2,3,4,5}', 'answer_display': '{1,2,3,4,5}', 'steps': 'Unija = vse kar je v A ali B.'},
            {'q': 'A = {1,2,3}, B = {3,4,5}. A ∩ B = ?', 'correct': '{3}', 'answer_display': '{3}', 'steps': 'Presek = skupni elementi.'}
        ],
        'quiz': [
            {'q': 'Kaj pomeni ∈?', 'options': ['Je podmnožica', 'Je element', 'Unija'], 'correct': 1},
            {'q': 'A∩B = ? (A={1,2,3}, B={3,4,5})', 'options': ['{1,2,3,4,5}', '{3}', '{1,2}'], 'correct': 1}
        ],
        'notes': 'Množice: ∈, ⊂, ∅, ∪, ∩'
    },
    'izjave': {
        'name': '🧠 Izjave in logika',
        'order': 2,
        'theory': '==================== IZJAVE IN LOGIKA ====================\n\n📌 KAJ JE IZJAVA?\nIzjava je trditev, ki je lahko PRAVILNA (P) ali NAPAČNA (N).\n\n🔗 LOGIČNI VEZNIKI:\nP ∧ Q = P in Q (resnično le, če sta obe resnični)\nP ∨ Q = P ali Q (resnično, če je vsaj ena resnična)\nP ⇒ Q = če P potem Q (napačno le, če je P resničen in Q napačen)\n¬P = negacija\n\n🔍 KVANTIFIKATORJA:\n∀ = za vsak\n∃ = obstaja\n\n📜 NEGACIJE:\n¬(∀x P(x)) = ∃x ¬P(x)\n¬(∃x P(x)) = ∀x ¬P(x)',
        'exercises': [
            {'q': 'P: 2+2=4 (P), Q: 3+3=7 (N). P ∧ Q = ?', 'correct': 'N', 'answer_display': 'N (napačno)', 'steps': 'Obe morata biti resnični. Q je napačna.'}
        ],
        'quiz': [
            {'q': 'P: 2+2=4, Q: 3+3=6. P ∧ Q = ?', 'options': ['P', 'N', 'Ni izjava'], 'correct': 0},
            {'q': 'Negacija ∃x: P(x) je:', 'options': ['∃x: ¬P(x)', '∀x: ¬P(x)', '∀x: P(x)'], 'correct': 1}
        ],
        'notes': 'Izjava = P ali N. ∧ (in), ∨ (ali), ⇒ (če-potem), ¬ (ne)'
    }
}

@app.route('/')
def index():
    progress = load_progress()
    return render_template('index.html', topics=TOPICS, progress=progress)

@app.route('/topic/<topic_id>')
def topic_view(topic_id):
    if topic_id not in TOPICS:
        return "Tema ne obstaja", 404
    progress = load_progress()
    return render_template('topic.html', topic=TOPICS[topic_id], topic_id=topic_id, progress=progress)

@app.route('/api/check', methods=['POST'])
def check_answer():
    data = request.json
    user = str(data.get('answer', '')).strip().lower()
    correct = str(data.get('correct', '')).lower()
    is_correct = user == correct or correct in user
    return jsonify({
        'correct': is_correct,
        'correct_answer': data.get('answer_display', ''),
        'steps': data.get('steps', ''),
        'message': '✅ Pravilno!' if is_correct else '❌ Napačno.'
    })

@app.route('/api/quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    answers = data.get('answers', [])
    topic_id = data.get('topic_id')
    quiz = TOPICS[topic_id]['quiz']
    score = 0
    for i, ans in enumerate(answers):
        if i < len(quiz) and ans == quiz[i]['correct']:
            score += 1
    passed = score >= len(quiz) - 1
    if passed:
        progress = load_progress()
        if topic_id not in progress['completed_topics']:
            progress['completed_topics'].append(topic_id)
            save_progress(progress)
    return jsonify({'score': score, 'total': len(quiz), 'passed': passed})

@app.route('/api/reset', methods=['POST'])
def reset():
    save_progress({'completed_topics': []})
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
