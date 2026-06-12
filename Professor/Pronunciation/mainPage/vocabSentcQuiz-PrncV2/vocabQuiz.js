/* vocabQuiz.js — shared logic for all vocab quiz pages */

// ── Shuffle options, pin -- Select -- ──────────────────────────────────────
document.querySelectorAll('select').forEach(select => {
    const options = Array.from(select.options).slice(1);
    for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
    }
    select.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = '-- Select --';
    placeholder.selected = true;
    select.appendChild(placeholder);
    options.forEach(opt => select.appendChild(opt));
    select.value = '';
});

// ── Check answers on change ────────────────────────────────────────────────
document.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', function () {
        const correct = this.getAttribute('data-answer');
        if (this.value === correct) {
            this.classList.remove('incorrect'); this.classList.add('correct');
        } else if (this.value !== '') {
            this.classList.remove('correct'); this.classList.add('incorrect');
        } else {
            this.classList.remove('correct', 'incorrect');
        }
    });
});

// ── Clear selections on unload ─────────────────────────────────────────────
window.addEventListener('beforeunload', () => {
    document.querySelectorAll('select').forEach(s => s.selectedIndex = 0);
});

// ── Study Mode — saves and restores student selections ────────────────────
let answersVisible = false;
let savedSelections = [];

function toggleAnswers() {
    answersVisible = !answersVisible;
    const button = document.getElementById('toggleAnswersBtn');
    const selects = document.querySelectorAll('select');
    if (answersVisible) {
        savedSelections = Array.from(selects).map(select => ({
            value: select.value,
            correct: select.classList.contains('correct'),
            incorrect: select.classList.contains('incorrect')
        }));
        selects.forEach(select => {
            select.value = select.getAttribute('data-answer');
            select.classList.add('correct');
            select.classList.remove('incorrect');
        });
    } else {
        selects.forEach((select, i) => {
            const saved = savedSelections[i];
            if (saved) {
                select.value = saved.value;
                select.classList.toggle('correct', saved.correct);
                select.classList.toggle('incorrect', saved.incorrect);
            }
        });
        savedSelections = [];
    }
    button.textContent = answersVisible ? ' Close Study Mode ' : ' Study Mode ';
}

// ── Word list display ──────────────────────────────────────────────────────
// wordListAnswers must be defined in each page's inline <script> before this runs.
function updateOutput() {
    const output = document.getElementById('output');
    const isColumn = output.classList.contains('column');
    output.innerHTML = isColumn
        ? wordListAnswers.map(w => `<span>${w}</span>`).join('')
        : wordListAnswers.join(' &nbsp; &nbsp; &nbsp; ');
}
function toggleView() {
    const output = document.getElementById('output');
    const button = document.querySelector('.toggle-button');
    output.classList.toggle('column');
    button.textContent = output.classList.contains('column') ? 'Close Column View' : 'View as Column';
    updateOutput();
}
function toggleWordList() {
    const wordList = document.getElementById('theWordList');
    const btn = document.querySelector('.show-hide-button');
    const isHidden = wordList.style.display === 'none' || wordList.style.display === '';
    wordList.style.display = isHidden ? 'block' : 'none';
    btn.textContent = isHidden ? 'Hide Word List' : 'Show Word List';
}
updateOutput();

// ── Student info / PDF button ──────────────────────────────────────────────
const nameInput = document.getElementById('studentName');
const idInput   = document.getElementById('studentID');
const pdfButton = document.getElementById('pdfButton');
const DEFAULTS  = { name: 'Name', id: 'ID' };

function sanitizeInput(input) {
    const temp = document.createElement('div');
    temp.textContent = input;
    return temp.innerHTML;
}
function validateInput(input, fieldName) {
    const s = sanitizeInput(input.trim());
    if (s.length < 2)  { alert(`${fieldName} must be at least 2 characters.`);  return false; }
    if (s.length > 25) { alert(`${fieldName} must be no more than 25 characters.`); return false; }
    return true;
}
function checkEnablePDF() {
    const n = nameInput.value.trim(), i = idInput.value.trim();
    pdfButton.disabled = !(n !== DEFAULTS.name && i !== DEFAULTS.id && n.length >= 2 && i.length >= 2);
}
nameInput.addEventListener('blur', function () {
    const v = this.value.trim();
    if (v !== DEFAULTS.name && v.length > 0)
        this.value = validateInput(v, 'Name') ? sanitizeInput(v) : DEFAULTS.name;
    checkEnablePDF();
});
idInput.addEventListener('blur', function () {
    const v = this.value.trim();
    if (v !== DEFAULTS.id && v.length > 0)
        this.value = validateInput(v, 'ID') ? sanitizeInput(v) : DEFAULTS.id;
    checkEnablePDF();
});
nameInput.addEventListener('input', checkEnablePDF);
idInput.addEventListener('input', checkEnablePDF);
nameInput.addEventListener('focus', function () { if (this.value === DEFAULTS.name) this.value = ''; });
idInput.addEventListener('focus',   function () { if (this.value === DEFAULTS.id)   this.value = ''; });
pdfButton.addEventListener('click', () => window.print());
