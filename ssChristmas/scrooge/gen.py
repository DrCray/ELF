import html as H
import re
import textwrap

# ---------- Line-wrapping helpers ----------
# The source HTML we generate mixes plain narrative text with <select>...</select>
# blocks. Naively joining everything into one f-string (or joining many blocks with
# "".join()) produces single lines that can run to thousands of characters, which is
# hard to read/diff/edit. These helpers reflow the generated markup onto lines of a
# bounded width WITHOUT ever splitting inside a <select>...</select> tag (which would
# risk corrupting an attribute value, e.g. data-answer="was too far gone" containing a
# space) and without ever splitting a single "word" token.
_SELECT_RE = re.compile(r'(<select.*?</select>)', re.S)

def _tokenize(html_str, atom_re=None):
    """Split html_str on whitespace, but never inside an atomic block (<select>...</select>
    or other atom_re match). Whitespace inside atoms is protected with a placeholder, so
    punctuation touching a block (e.g. '</select>,') stays glued to it — no stray space."""
    atom_re = atom_re or _SELECT_RE
    PH = "\x00"
    protected = atom_re.sub(lambda m: re.sub(r"\s", lambda w: PH + str(ord(w.group())) + PH, m.group()), html_str)
    return [re.sub(PH + r"(\d+)" + PH, lambda m: chr(int(m.group(1))), t) for t in protected.split()]

def wrap_html(html_str, width=100, atom_re=None):
    """Reflow a string of mixed text + <select> markup onto lines <= width chars,
    breaking only between tokens (never inside a <select> block or a word)."""
    lines, cur, cur_len = [], [], 0
    for tok in _tokenize(html_str, atom_re):
        extra = (1 if cur else 0) + len(tok)
        if cur and cur_len + extra > width:
            lines.append(" ".join(cur))
            cur, cur_len = [tok], len(tok)
        else:
            cur.append(tok)
            cur_len += extra
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)

def join_blocks(blocks, sep="\n"):
    """Join a list of HTML block strings (e.g. one per <div>/<p>) with a real
    newline between them, instead of "".join(), so each block starts on its own
    line in the generated source."""
    return sep.join(blocks)

# ---------- Shared CSS ----------
CSS = """
:root{
  --purple:#26215C;
  --purple-light:#3d3680;
  --paper:#faf7f2;
  --card:#ffffff;
  --correct:#1f7a3d;
  --correct-bg:#e3f6e9;
  --incorrect:#a3231f;
  --incorrect-bg:#fbe6e5;
  --border:#e2ddd2;
  --text:#2a2a2a;
}
*{box-sizing:border-box;}
body{
  margin:0;
  font-family:'DM Sans', system-ui, -apple-system, sans-serif;
  background:var(--paper);
  color:var(--text);
  line-height:1.65;
  padding:0 0 4rem;
  max-width:50rem; margin:auto;
}
h1,h2,h3{
  font-family:'Playfair Display', Georgia, serif;
  color:var(--purple);
  line-height:1.25;
}
.wrap{
  max-width:44rem;
  margin:0 auto;
  padding:clamp(1rem,4vw,2rem);
}
header.page-header{
  background:var(--purple);
  color:#fff;
  padding:clamp(1.25rem,4vw,2rem) clamp(1rem,4vw,2rem);
  text-align:center;
}
header.page-header h1{
  color:#fff;
  font-size:clamp(1.4rem,4vw,2rem);
  margin:0 0 .35rem;
}
header.page-header p{margin:0;opacity:.85;font-size:.95rem;}
.section{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:clamp(1rem,3vw,1.75rem);
  margin:1.25rem 0;
}
.section h2{font-size:clamp(1.1rem,3vw,1.4rem);margin-top:0;}
.passage p{margin:0 0 1rem;}
select.blank{
  font:inherit;
  font-weight:600;
  padding:.2rem .45rem;
  border-radius:6px;
  border:1.5px solid var(--purple);
  background:#fff;
  color:var(--purple);
  margin:0 .15rem;
}
select.blank.correct{background:var(--correct-bg);border-color:var(--correct);color:var(--correct);}
select.blank.incorrect{background:var(--incorrect-bg);border-color:var(--incorrect);color:var(--incorrect);}
.vocab-card{
  border:1px solid var(--border);
  border-radius:10px;
  padding:.9rem 1.1rem;
  margin:0 0 .85rem;
  background:var(--paper);
}
.vocab-card .word{font-weight:700;color:var(--purple);font-size:1.05rem;}
.vocab-card .pos{font-style:italic;font-size:.85rem;color:#6a6a6a;margin-left:.4rem;}
.vocab-card .def{margin:.3rem 0;}
.vocab-card .example{font-size:.92rem;color:#4a4a4a;}
.quiz-item{margin:0 0 1.1rem;}
.quiz-item .qnum{font-weight:700;color:var(--purple);margin-right:.3rem;}

/* Sticky toolbar */
.toolbar{
  position:sticky;
  top:0;
  z-index:50;
  display:flex;
  gap:.6rem;
  justify-content:flex-end;
  flex-wrap:wrap;
  padding:.6rem clamp(1rem,4vw,2rem);
  background:rgba(250,247,242,.92);
  backdrop-filter:blur(4px);
  border-bottom:1px solid var(--border);
}
.btn{
  font:inherit;
  font-weight:600;
  font-size:.85rem;
  padding:.5rem 1rem;
  border-radius:999px;
  border:none;
  cursor:pointer;
  color:#fff;
  background:linear-gradient(135deg,var(--purple),var(--purple-light));
  transition:opacity .15s ease;
}
.btn:hover{opacity:.85;}
.btn.secondary{
  background:#fff;
  color:var(--purple);
  border:1.5px solid var(--purple);
}

/* Print-gate modal */
.modal-overlay{
  position:fixed;inset:0;
  background:rgba(38,33,92,.55);
  display:none;
  align-items:center;
  justify-content:center;
  z-index:200;
  padding:1rem;
}
.modal-overlay.open{display:flex;}
.modal-box{
  background:#fff;
  border-radius:12px;
  padding:1.5rem;
  max-width:22rem;
  width:100%;
}
.modal-box h3{margin-top:0;}
.modal-box label{display:block;font-size:.85rem;font-weight:600;margin:.7rem 0 .3rem;}
.modal-box input{
  width:100%;
  padding:.5rem .6rem;
  border-radius:6px;
  border:1.5px solid var(--border);
  font:inherit;
}
.modal-actions{display:flex;justify-content:flex-end;gap:.5rem;margin-top:1.2rem;}

.student-id-line{
  display:none;
  font-size:.85rem;
  color:#555;
  margin:0 0 1rem;
  border-bottom:1px solid var(--border);
  padding-bottom:.5rem;
}
@media print{
  .toolbar,.modal-overlay{display:none !important;}
  .student-id-line{display:block !important;}
  select.blank{border:none;background:none;-webkit-appearance:none;appearance:none;}
}
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
"""

MODAL = """
<div class="modal-overlay" id="nameIdOverlay">
  <div class="modal-box">
    <h3>Before you print and save as PDF…</h3>
    <p style="font-size:.9rem;color:#555;margin:0;">Please enter your name and student ID.</p>
    <label for="studentName">Name</label>
    <input type="text" id="studentName" placeholder="Name">
    <label for="studentId">Student ID</label>
    <input type="text" id="studentId" placeholder="ID#">
    <div class="modal-actions">
      <button class="btn secondary" id="modalCancel" type="button">Cancel</button>
      <button class="btn" id="modalConfirm" type="button">Continue &amp; Print</button>
    </div>
  </div>
</div>
"""

MODAL_STUDY = """
<div class="modal-overlay" id="nameIdOverlay">
  <div class="modal-box">
    <h3>Before you print…</h3>
    <p style="font-size:.9rem;color:#555;margin:0;">Please enter your name and student ID. This will appear at the top of your printed page.</p>
    <label for="studentName">Name</label>
    <input type="text" id="studentName" placeholder="Your full name">
    <label for="studentId">Student ID</label>
    <input type="text" id="studentId" placeholder="Your student ID">
    <div class="modal-actions">
      <button class="btn secondary" id="modalCancel" type="button">Cancel</button>
      <button class="btn" id="modalConfirm" type="button">Continue &amp; Print</button>
    </div>
  </div>
</div>
"""

SCRIPT_QUIZ = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  const selects = () => document.querySelectorAll('select.blank');

  // ---- Immediate feedback on change ----
  document.body.addEventListener('change', (e) => {
    if (!e.target.matches('select.blank')) return;
    const sel = e.target;
    sel.classList.remove('correct','incorrect');
    if (sel.value === sel.dataset.answer) {
      sel.classList.add('correct');
    } else if (sel.value !== '') {
      sel.classList.add('incorrect');
    }
  });

  // ---- Study Mode: snapshot / reveal / restore ----
  const studyBtn = document.getElementById('studyModeBtn');
  let snapshot = null;
  let inStudy = false;

  studyBtn.addEventListener('click', () => {
    const all = selects();
    if (!inStudy) {
      snapshot = Array.from(all).map(s => ({
        value: s.value,
        classes: Array.from(s.classList)
      }));
      all.forEach(s => {
        s.value = s.dataset.answer;
        s.classList.remove('incorrect');
        s.classList.add('correct');
        s.disabled = true;
      });
      inStudy = true;
      studyBtn.textContent = 'Return to Quiz';
    } else {
      all.forEach((s, i) => {
        const snap = snapshot ? snapshot[i] : null;
        s.disabled = false;
        s.classList.remove('correct','incorrect');
        if (snap) {
          s.value = snap.value;
          snap.classes.forEach(c => { if (c === 'correct' || c === 'incorrect') s.classList.add(c); });
        }
      });
      inStudy = false;
      studyBtn.textContent = 'Study Mode';
    }
  });

  // ---- Print gate: require Name + Student ID first ----
  const printBtn = document.getElementById('printBtn');
  const overlay = document.getElementById('nameIdOverlay');
  const nameInput = document.getElementById('studentName');
  const idInput = document.getElementById('studentId');
  const cancelBtn = document.getElementById('modalCancel');
  const confirmBtn = document.getElementById('modalConfirm');
  const idLine = document.getElementById('studentIdLine');

  printBtn.addEventListener('click', () => {
    overlay.classList.add('open');
    nameInput.focus();
  });
  cancelBtn.addEventListener('click', () => overlay.classList.remove('open'));
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.classList.remove('open'); });

  confirmBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();
    const id = idInput.value.trim();
    if (!name || !id) {
      alert('Please enter both your name and student ID before printing.');
      return;
    }
    idLine.textContent = `Name: ${name}    Student ID: ${id}`;
    overlay.classList.remove('open');
    window.print();
  });
});
</script>
"""

SCRIPT_STUDY = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  const printBtn = document.getElementById('printBtn');
  const overlay = document.getElementById('nameIdOverlay');
  const nameInput = document.getElementById('studentName');
  const idInput = document.getElementById('studentId');
  const cancelBtn = document.getElementById('modalCancel');
  const confirmBtn = document.getElementById('modalConfirm');
  const idLine = document.getElementById('studentIdLine');

  printBtn.addEventListener('click', () => {
    overlay.classList.add('open');
    nameInput.focus();
  });
  cancelBtn.addEventListener('click', () => overlay.classList.remove('open'));
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.classList.remove('open'); });

  confirmBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();
    const id = idInput.value.trim();
    if (!name || !id) {
      alert('Please enter both your name and student ID before printing.');
      return;
    }
    idLine.textContent = `Name: ${name}    Student ID: ${id}`;
    overlay.classList.remove('open');
    window.print();
  });
});
</script>
"""

def esc(s):
    return H.escape(s, quote=True)

def select_html(answer, options):
    """options: list of words (strings) including the answer, in the desired display order."""
    opts = ['<option value="">— choose —</option>']
    for o in options:
        opts.append(f'<option value="{esc(o)}">{esc(o)}</option>')
    return f'<select class="blank" data-answer="{esc(answer)}">' + "".join(opts) + "</select>"


# ================= LESSON: A Christmas Carol (The Literary Lens podcast) =================
import random
random.seed(42)

SLUG = "christmas-carol"
TOPIC = "A Christmas Carol"

MARKDOWN = """Sarah: Welcome back to The Literary Lens, where we talk about stories that shape our world. I’m Sarah. Today, we’re discussing a **timeless classic** that has captured the public's imagination for nearly 185 years.

Mark: And I’m Mark. We’re talking about a famous holiday **classic**. The name might **ring a bell**. It's Charles Dickens' *A Christmas Carol*, often called *Scrooge*.

Sarah: It’s incredible how this short book has managed to **stand the test of time**. Published in 1843, its popularity never **fades**. In fact, the very name of "Scrooge" has become synonymous with the word **miser**.

Mark: Exactly. The story begins the day before Christmas, with Scrooge being cruel to his employee and his own family. But later that night, he **goes through** a **frightening** experience.

Sarah: Right! He is visited by the ghost of his **deceased** business partner, followed by three other spirits: the Ghosts of Christmas Past, Present, and Future. They **point out** where his life is **heading** unless he has a **change of heart**.

Mark: For example, the first spirit shows him that his **obsession** with wealth pushed away the only woman he ever truly loved. She married another man and had a happy family.

Sarah: Then the Ghost of Christmas Present shows him how the Cratchit family finds joy even in **poverty**. The spirit introduces him to Tiny Tim, a boy with a life-threatening illness. Despite his own **condition**, Tiny Tim chooses to bring happiness to everyone around him.

Mark: Finally, the last ghost shows Scrooge the **untimely** death of warm-hearted Tiny Tim. He also shows Scrooge his own lonely, **miserable** death. This fills Scrooge with terrible **regret** over his selfish choices.

Sarah: But this isn't just a sad ghost story; it’s a powerful story about **redemption**. It shows us that anyone can have a **change of heart**.

Mark: So Scrooge wakes up on Christmas morning and decides to **turn over a new leaf**. The angry old man becomes a completely different person.

Sarah: He really has an amazing **transformation**. He **turns into** a warm, happy, and **generous** person. This story tells us that people can change for the better.

Mark: And there have been **countless** movie **adaptations** over the years—more than twenty since 1950. The number of stage productions, TV shows, films, and spin-offs is **staggering**.

Sarah: Oh, definitely! There are animated versions, Broadway versions, big musicals, and even modern comedies. It seems like every **generation** gets its own version.

Mark: And in each **rendition**, the universal message shines through.

Sarah: It really does. The story's **influence** reaches all over the world. Its core theme of personal transformation from selfishness to kindness "resonates" across cultures.

Mark: And on that note, time has **run out** for today's show. Thanks for tuning in, and we’ll see you next time!"""

VOCAB = [
    ("timeless classic", "noun phrase", "a famous work that stays popular and important no matter how much time passes",
     "Today, we’re discussing a timeless classic that has captured the public's imagination for nearly 185 years."),
    ("classic", "noun", "a book, film, or song of high quality that people enjoy for many years",
     "We’re talking about a famous holiday classic."),
    ("ring a bell", "idiom", "to sound familiar; to remind you of something you have heard before",
     "The name might ring a bell."),
    ("stand the test of time", "idiom", "to stay popular, useful, or valued for a long time",
     "It’s incredible how this short book has managed to stand the test of time."),
    ("fades", "verb", "slowly becomes weaker or less noticeable until it disappears",
     "Published in 1843, its popularity never fades."),
    ("miser", "noun", "a person who loves money and hates spending it, even when they have a lot",
     "The very name of 'Scrooge' has become synonymous with the word miser."),
    ("goes through", "phrasal verb", "experiences something, especially something difficult or unpleasant",
     "But later that night, he goes through a frightening experience."),
    ("frightening", "adjective", "making someone feel afraid; scary",
     "But later that night, he goes through a frightening experience."),
    ("deceased", "adjective", "dead; no longer living (a formal word)",
     "He is visited by the ghost of his deceased business partner."),
    ("point out", "phrasal verb", "to show or tell someone something so that they notice it",
     "They point out where his life is heading unless he has a change of heart."),
    ("heading", "verb (-ing)", "moving or developing in a particular direction",
     "They point out where his life is heading unless he has a change of heart."),
    ("change of heart", "noun phrase", "a change in someone’s opinion, feelings, or attitude",
     "It shows us that anyone can have a change of heart."),
    ("obsession", "noun", "something a person thinks about all the time, often in an unhealthy way",
     "The first spirit shows him that his obsession with wealth pushed away the only woman he ever truly loved."),
    ("poverty", "noun", "the state of being very poor",
     "The Ghost of Christmas Present shows him how the Cratchit family finds joy even in poverty."),
    ("condition", "noun", "an illness or health problem that someone has for a long time",
     "Despite his own condition, Tiny Tim chooses to bring happiness to everyone around him."),
    ("untimely", "adjective", "happening too early or at the wrong time",
     "The last ghost shows Scrooge the untimely death of warm-hearted Tiny Tim."),
    ("miserable", "adjective", "very unhappy or uncomfortable",
     "He also shows Scrooge his own lonely, miserable death."),
    ("regret", "noun", "a feeling of sadness about something you did or did not do",
     "This fills Scrooge with terrible regret over his selfish choices."),
    ("redemption", "noun", "being saved from evil or wrongdoing; making up for past mistakes",
     "This isn't just a sad ghost story; it’s a powerful story about redemption."),
    ("turn over a new leaf", "idiom", "to change your behavior and start acting in a better way",
     "Scrooge wakes up on Christmas morning and decides to turn over a new leaf."),
    ("transformation", "noun", "a complete change in someone’s appearance or character",
     "He really has an amazing transformation."),
    ("turns into", "phrasal verb", "changes and becomes something different",
     "He turns into a warm, happy, and generous person."),
    ("generous", "adjective", "happy to give money, time, or help to others",
     "He turns into a warm, happy, and generous person."),
    ("countless", "adjective", "too many to be counted; very many",
     "There have been countless movie adaptations over the years."),
    ("adaptations", "noun", "films, plays, or TV shows made from a book or another story",
     "There have been countless movie adaptations over the years—more than twenty since 1950."),
    ("staggering", "adjective", "very surprising or shocking, especially because it is so large",
     "The number of stage productions, TV shows, films, and spin-offs is staggering."),
    ("generation", "noun", "all the people born and living at about the same time",
     "It seems like every generation gets its own version."),
    ("rendition", "noun", "a particular performance or version of a song, play, or story",
     "And in each rendition, the universal message shines through."),
    ("influence", "noun", "the power to affect how people think or behave",
     "The story's influence reaches all over the world."),
    ("run out", "phrasal verb", "to be used up or finished so that there is no more left",
     "And on that note, time has run out for today's show."),
]
WORDS = [v[0] for v in VOCAB]
VOCAB_BY_WORD = {v[0]: v for v in VOCAB}

DISTRACTORS = {
    "timeless classic": ["change of heart", "redemption"],
    "classic": ["generation", "miser"],
    "ring a bell": ["stand the test of time", "turn over a new leaf"],
    "stand the test of time": ["ring a bell", "turn over a new leaf"],
    "fades": ["goes through", "heading"],
    "miser": ["classic", "rendition"],
    "goes through": ["turns into", "point out"],
    "frightening": ["generous", "untimely"],
    "deceased": ["staggering", "countless"],
    "point out": ["run out", "goes through"],
    "heading": ["fades", "staggering"],
    "change of heart": ["timeless classic", "rendition"],
    "obsession": ["poverty", "influence"],
    "poverty": ["miser", "adaptations"],
    "condition": ["generation", "influence"],
    "untimely": ["generous", "countless"],
    "miserable": ["generous", "deceased"],
    "regret": ["redemption", "generation"],
    "redemption": ["miser", "condition"],
    "turn over a new leaf": ["stand the test of time", "point out"],
    "transformation": ["adaptations", "poverty"],
    "turns into": ["fades", "point out"],
    "generous": ["untimely", "deceased"],
    "countless": ["untimely", "deceased"],
    "adaptations": ["generation", "influence"],
    "staggering": ["untimely", "deceased"],
    "generation": ["condition", "influence"],
    "rendition": ["miser", "obsession"],
    "influence": ["regret", "poverty"],
    "run out": ["point out", "turns into"],
}

NEW_SENTENCES = {
    "timeless classic": "Many critics call the old black-and-white film a ___ that every student should watch.",
    "classic": "That song from the 1960s is a real ___; even my grandchildren know all the words.",
    "ring a bell": "Sorry, the name Maria Lopez doesn’t ___. Have we met before?",
    "stand the test of time": "Good design will ___, while fashion trends come and go.",
    "fades": "The color of the old poster in the window ___ a little more every summer.",
    "miser": "The old ___ kept all his money hidden under his bed and never bought anything new.",
    "goes through": "Almost every new student ___ a period of homesickness during the first month.",
    "frightening": "Walking home alone through the dark forest was a ___ experience.",
    "deceased": "The lawyer read the will of the ___ woman to her family.",
    "point out": "Could you ___ any mistakes you see in my essay?",
    "heading": "Look at those dark clouds — the storm is ___ our way.",
    "change of heart": "He planned to quit the team, but after talking to the coach, he had a ___.",
    "obsession": "His ___ with video games meant he rarely left his room.",
    "poverty": "Many families in the region still live in ___ without clean water.",
    "condition": "Her heart ___ means she has to avoid heavy exercise.",
    "untimely": "The singer’s ___ death at age 27 shocked his fans around the world.",
    "miserable": "I felt ___ all week because of the rainy weather and my bad cold.",
    "regret": "My biggest ___ is not studying harder in high school.",
    "redemption": "After years of bad choices, the hero finds ___ by saving a child’s life.",
    "turn over a new leaf": "After failing two classes, Tom promised to ___ and study every night.",
    "transformation": "The old warehouse went through a complete ___ and is now a beautiful café.",
    "turns into": "When water freezes, it ___ ice.",
    "generous": "Thanks to a ___ donation, the library bought hundreds of new books.",
    "countless": "The teacher has helped ___ students prepare for their exams.",
    "adaptations": "There have been many film ___ of Shakespeare’s plays.",
    "staggering": "The cost of the new stadium was a ___ two billion dollars.",
    "generation": "My grandparents’ ___ grew up without smartphones or the internet.",
    "rendition": "The choir gave a beautiful ___ of the national anthem.",
    "influence": "Parents have a strong ___ on their children’s eating habits.",
    "run out": "We need to buy more milk before we ___.",
}

def build_options(correct):
    opts = [correct] + DISTRACTORS[correct]
    random.shuffle(opts)
    return opts

# ---------- Markdown parsing ----------
_MD_RE = re.compile(r'(\*\*.+?\*\*|\*[^*]+?\*)')
def parse_lines():
    """Return list of (speaker, text) from MARKDOWN."""
    out = []
    for para in [p.strip() for p in MARKDOWN.split("\n\n") if p.strip()]:
        spk, txt = para.split(":", 1)
        out.append((spk.strip(), txt.strip()))
    return out

def render_md(text, bold_fn):
    """Escape plain text, render *italics* as <em>, and bold via bold_fn(word)."""
    parts = []
    for tok in _MD_RE.split(text):
        if tok.startswith("**") and tok.endswith("**"):
            parts.append(bold_fn(tok[2:-2]))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            parts.append(f"<em>{esc(tok[1:-1])}</em>")
        else:
            parts.append(esc(tok))
    return "".join(parts)

LINES = parse_lines()
_BOLD = [b for _, t in LINES for b in re.findall(r'\*\*(.+?)\*\*', t)]
assert set(_BOLD) == set(WORDS), (set(_BOLD) ^ set(WORDS))
assert set(DISTRACTORS) == set(WORDS) == set(NEW_SENTENCES)
for w, d in DISTRACTORS.items():
    assert w not in d and all(x in WORDS for x in d), w

TOOLBAR_QUIZ = '''
<div class="toolbar">
  <button id="studyModeBtn" class="btn secondary" type="button">Study Mode</button>
  <button id="printBtn" class="btn" type="button">Print / Save PDF</button>
</div>
'''

def page(title, subtitle, toolbar, inner, script, extra_css=""):
    body = f'''{toolbar}
<header class="page-header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</header>
<div class="wrap">
  <p class="student-id-line" id="studentIdLine"></p>

{inner}

</div>
{MODAL}
{script}
</body>
</html>'''
    return HEAD.format(title=title, css=CSS + extra_css) + body

# ---------- 1. Study cards ----------
def gen_study_cards():
    cards = join_blocks(f'''<div class="vocab-card">
  <span class="word">{esc(w)}</span><span class="pos">({esc(p)})</span>
  <p class="def">{esc(d)}</p>
  <p class="example"><em>"{esc(e)}"</em></p>
</div>''' for w, p, d, e in VOCAB)
    toolbar = '''
<div class="toolbar" style="display:none;">
  <button id="printBtn" class="btn" type="button">Print / Save PDF</button>
</div>
'''
    inner = f'''<div class="section">
  <h2>Word List</h2>
{cards}
</div>'''
    return page(f"{TOPIC} — Vocabulary Study",
                f"{len(VOCAB)} key words and phrases from the podcast (reference)",
                toolbar, inner, SCRIPT_STUDY)

# ---------- 2. Article cloze ----------
def gen_article_cloze():
    blank = lambda w: select_html(w, build_options(w))
    paras = []
    for spk, txt in LINES:
        body = f"<strong>{esc(spk)}:</strong> " + render_md(txt, blank)
        paras.append(f"<p>{wrap_html(body, width=100)}</p>")
    inner = f'''<div class="section passage">
  <h2>Fill in the Blanks</h2>
  <p style="font-size:.9rem;color:#666;">Read the podcast conversation about <em>A Christmas Carol</em> and choose the word or phrase that best completes each sentence.</p>
{join_blocks(paras)}
</div>'''
    return page(f"{TOPIC} — Article Cloze", "Vocabulary-in-context practice",
                TOOLBAR_QUIZ, inner, SCRIPT_QUIZ)

# ---------- 3. Definition cloze ----------
def gen_def_cloze():
    items = []
    for i, (w, p, d, e) in enumerate(VOCAB, 1):
        sel = select_html(w, build_options(w))
        items.append(f'''<div class="quiz-item">
  <span class="qnum">{i}.</span>{esc(d[0].upper()+d[1:])} — this word or phrase is {sel}.
</div>''')
    inner = f'''<div class="section">
  <h2>Check Your Understanding</h2>
  <p style="font-size:.9rem;color:#666;">Choose the word or phrase that matches each definition.</p>
{join_blocks(items)}
</div>'''
    return page(f"{TOPIC} — Vocabulary Quiz", "Match each word to its definition",
                TOOLBAR_QUIZ, inner, SCRIPT_QUIZ)

# ---------- 4. Sentence cloze ----------
def gen_sentences_cloze():
    items = []
    for i, (w, p, d, e) in enumerate(VOCAB, 1):
        before, after = NEW_SENTENCES[w].split("___", 1)
        sel = select_html(w, build_options(w))
        items.append(f'<div class="quiz-item"><span class="qnum">{i}.</span>{esc(before)}{sel}{esc(after)}</div>')
    inner = f'''<div class="section">
  <h2>New Sentences — Choose the Correct Word</h2>
  <p style="font-size:.9rem;color:#666;">These sentences are new — they do not come directly from the podcast. Choose the vocabulary word or phrase that best completes each one.</p>
{join_blocks(items)}
</div>'''
    return page(f"{TOPIC} — Vocabulary Cloze", "Practice with new sentences",
                TOOLBAR_QUIZ, inner, SCRIPT_QUIZ)

# ---------- 5. Podcast page ----------
PODCAST_CSS = """
.ep-meta{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;}
.ep-art{width:4.5rem;height:4.5rem;border-radius:10px;flex:none;
  background:linear-gradient(135deg,var(--purple),var(--purple-light));
  color:#fff;display:flex;align-items:center;justify-content:center;
  font-family:'Playfair Display',Georgia,serif;font-size:1.6rem;font-weight:700;}
.ep-meta h2{margin:0;}
.ep-meta p{margin:.15rem 0 0;color:#666;font-size:.9rem;}
.fake-player{display:flex;align-items:center;gap:.9rem;margin-top:1rem;padding:.75rem 1rem;
  border:1.5px solid var(--purple);border-radius:999px;background:var(--paper);text-decoration:none;
  color:var(--text);transition:background .15s ease,box-shadow .15s ease;}
.fake-player:hover{background:#ece9fb;box-shadow:0 4px 14px rgba(38,33,92,.15);}
.fp-play{flex:none;width:2.6rem;height:2.6rem;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,var(--purple),var(--purple-light));color:#fff;font-size:1rem;padding-left:.15rem;}
.fp-body{flex:1;min-width:0;}
.fp-title{display:block;font-weight:600;font-size:.9rem;color:var(--purple);}
.fp-track{display:flex;align-items:center;gap:.6rem;font-size:.75rem;color:#777;margin-top:.25rem;}
.fp-bar{flex:1;height:5px;border-radius:999px;background:var(--border);position:relative;}
.fp-bar::before{content:"";position:absolute;left:0;top:0;bottom:0;width:0;border-radius:999px;background:var(--purple);}
.fp-bar::after{content:"";position:absolute;left:-5px;top:50%;width:11px;height:11px;margin-top:-5.5px;
  border-radius:50%;background:var(--purple);}
.fp-src{flex:none;font-size:.75rem;font-weight:600;color:#a3231f;}
.line{display:flex;gap:.75rem;padding:.6rem .7rem;margin:0 -.7rem .35rem;border-radius:10px;}
.spk{flex:none;width:3.4rem;font-weight:700;font-size:.85rem;padding-top:.15rem;}
.spk.sarah{color:var(--purple);}
.spk.mark{color:#8a5a14;}
.line p{margin:0;}
button.vocab{font:inherit;font-weight:700;color:var(--purple);background:none;border:none;padding:0;
  cursor:pointer;border-bottom:2px dotted var(--purple-light);}
button.vocab:hover,button.vocab.active{background:#ece9fb;}
.def-bar{position:fixed;left:50%;bottom:1rem;transform:translateX(-50%);width:min(40rem,calc(100% - 2rem));
  background:#fff;border:1.5px solid var(--purple);border-radius:12px;padding:.8rem 2.4rem .8rem 1rem;
  box-shadow:0 8px 24px rgba(38,33,92,.18);display:none;z-index:100;}
.def-bar.open{display:block;}
.def-bar .word{font-weight:700;color:var(--purple);}
.def-bar .pos{font-style:italic;font-size:.85rem;color:#6a6a6a;margin-left:.4rem;}
.def-bar p{margin:.2rem 0 0;}
.def-bar .close{position:absolute;top:.4rem;right:.6rem;border:none;background:none;font-size:1.3rem;
  color:#888;cursor:pointer;line-height:1;}
.links{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.75rem;}
.link-card{display:block;text-decoration:none;color:var(--text);border:1px solid var(--border);
  border-radius:10px;padding:.9rem 1.1rem;background:var(--paper);transition:border-color .15s ease;}
.link-card:hover{border-color:var(--purple);}
.link-card strong{display:block;color:var(--purple);font-family:'Playfair Display',Georgia,serif;font-size:1.05rem;}
.link-card span{font-size:.88rem;color:#555;}
@media print{.fake-player,.def-bar,.links-section{display:none !important;}}
"""

SCRIPT_PODCAST = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  // ---- Tap a vocabulary word to see its definition ----
  const bar = document.getElementById('defBar');
  const barWord = document.getElementById('defWord');
  const barPos = document.getElementById('defPos');
  const barDef = document.getElementById('defText');
  let activeBtn = null;
  document.querySelectorAll('button.vocab').forEach(b => {
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      if (activeBtn) activeBtn.classList.remove('active');
      activeBtn = b; b.classList.add('active');
      barWord.textContent = b.dataset.word;
      barPos.textContent = '(' + b.dataset.pos + ')';
      barDef.textContent = b.dataset.def;
      bar.classList.add('open');
    });
  });
  document.getElementById('defClose').addEventListener('click', () => {
    bar.classList.remove('open');
    if (activeBtn) activeBtn.classList.remove('active');
  });

});
</script>
"""

_ATOM_RE = re.compile(r'(<button class="vocab".*?</button>)', re.S)
def wrap_atoms(s, width=100):
    return wrap_html(s, width, _ATOM_RE)

def gen_podcast():
    def vocab_btn(w):
        _, p, d, _e = VOCAB_BY_WORD[w]
        return (f'<button class="vocab" type="button" data-word="{esc(w)}" data-pos="{esc(p)}" '
                f'data-def="{esc(d)}">{esc(w)}</button>')
    rows = []
    for spk, txt in LINES:
        rows.append(f'<div class="line" data-speaker="{esc(spk)}">\n'
                    f'  <span class="spk {spk.lower()}">{esc(spk)}</span>\n'
                    f'  <p>{wrap_atoms(render_md(txt, vocab_btn))}</p>\n</div>')
    links = [
        ("vocabulary-study-cards", "Vocabulary Study Cards", "Definitions and examples for every word and phrase."),
        ("article-cloze", "Podcast Cloze", "Fill in the missing words in the full transcript."),
        ("vocab-def-cloze", "Definition Quiz", "Match each definition to the right word."),
        ("vocab-sentences-cloze", "Sentence Cloze", "Use the vocabulary in brand-new sentences."),
    ]
    link_html = join_blocks(
        f'<a class="link-card" href="{SLUG}-{f}.html" target="_blank" rel="noopener"><strong>{t}</strong><span>{d}</span></a>'
        for f, t, d in links)
    toolbar = '''
<div class="toolbar">
  <button id="printBtn" class="btn secondary" type="button">Print / Save PDF</button>
</div>
'''
    inner = f'''<div class="section">
  <div class="ep-meta">
    <div class="ep-art">LL</div>
    <div>
      <h2>A Christmas Carol: The Story of Redemption</h2>
      <p>The Literary Lens · with Sarah &amp; Mark</p>
    </div>
  </div>
  <a class="fake-player" href="YOUTUBE_LINK_HERE" target="_blank" rel="noopener" aria-label="Listen to this episode on YouTube (opens in a new tab)">
    <span class="fp-play" aria-hidden="true">▶</span>
    <span class="fp-body">
      <span class="fp-title">Listen to this episode</span>
      <span class="fp-track"><span>0:00</span><span class="fp-bar"></span><span>--:--</span></span>
    </span>
    <span class="fp-src">YouTube ↗</span>
  </a>
</div>

<div class="section">
  <h2>Transcript</h2>
  <p style="font-size:.9rem;color:#666;">Tap a <strong style="color:var(--purple)">highlighted word</strong> to see what it means.</p>
{join_blocks(rows)}
</div>

<div class="section links-section">
  <h2>Practice the Vocabulary</h2>
  <div class="links">
{link_html}
  </div>
</div>

<div class="def-bar" id="defBar" role="status" aria-live="polite">
  <button class="close" id="defClose" type="button" aria-label="Close">×</button>
  <span class="word" id="defWord"></span><span class="pos" id="defPos"></span>
  <p id="defText"></p>
</div>'''
    # Podcast page reuses the print gate from SCRIPT_STUDY
    return page(f"{TOPIC} — The Literary Lens Podcast",
                "Listen, read along, and learn the key vocabulary",
                toolbar, inner, SCRIPT_STUDY + SCRIPT_PODCAST, PODCAST_CSS)

if __name__ == "__main__":
    import os
    outdir = "/mnt/user-data/outputs"
    os.makedirs(outdir, exist_ok=True)
    for name, fn in [("podcast", gen_podcast),
                     ("vocabulary-study-cards", gen_study_cards),
                     ("article-cloze", gen_article_cloze),
                     ("vocab-def-cloze", gen_def_cloze),
                     ("vocab-sentences-cloze", gen_sentences_cloze)]:
        with open(f"{outdir}/{SLUG}-{name}.html", "w") as f:
            f.write(fn())
    print("done")
