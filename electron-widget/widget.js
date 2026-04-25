const API_BASE_URL = 'https://mydict.classplay.uz';

const BG_COLORS = [
  '#FFD6C0','#C9F0FF','#D4F5D4','#F2D9FF','#FFF5C0',
  '#C0E8FF','#FFDCD5','#C5FAF0','#E8D9FF','#FFFBC0',
  '#FFE5C0','#D0F0FF','#D8FFD8','#F8D5FF','#FFF0C0',
  '#C5DBFF','#FFD5E0','#C0F5E8','#EDD9FF','#FAFFC0',
];

let currentId = null;
let isAnimating = false;

document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  loadStats();
  fetchWord();
});

async function fetchWord() {
  const params = new URLSearchParams();
  if (currentId) params.set('exclude_id', currentId);
  const url = API_BASE_URL + '/api/word/random' + (params.toString() ? '?' + params.toString() : '');
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.error) {
      renderError(data.message);
      return;
    }
    currentId = data.id;
    renderWord(data);
  } catch (e) {
    renderError('Connection error — is the server running?');
  }
}

function nextWord() {
  if (isAnimating) return;
  isAnimating = true;
  const el = document.getElementById('word-main');
  el.style.opacity = '0';
  el.style.transform = 'translateY(-12px)';
  setTimeout(() => {
    fetchWord();
    isAnimating = false;
  }, 220);
}

document.getElementById('word-area').addEventListener('click', nextWord);

function renderWord(w) {
  const lang = localStorage.getItem('primaryLang') || 'en';

  let main, subA, subB;
  if (lang === 'uz') {
    main = w.word_uz || w.word_en;
    subA = 'EN: ' + w.word_en;
    subB = 'KR: ' + (w.word_kr || '—');
  } else if (lang === 'kr') {
    main = w.word_kr || w.word_en;
    subA = 'EN: ' + w.word_en;
    subB = 'UZ: ' + (w.word_uz || '—');
  } else {
    main = w.word_en;
    subA = 'UZ: ' + (w.word_uz || '—');
    subB = 'KR: ' + (w.word_kr || '—');
  }

  const mainEl = document.getElementById('word-main');
  mainEl.textContent = main;
  mainEl.style.opacity = '1';
  mainEl.style.transform = 'translateY(0)';
  mainEl.style.transition = 'opacity .3s ease, transform .3s ease';

  document.getElementById('sub-a').textContent = subA;
  document.getElementById('sub-b').textContent = subB;

  const defKey = lang === 'uz' ? 'def_uz' : lang === 'kr' ? 'def_kr' : 'def_en';
  const def = w[defKey] || w['def_en'] || w['def_ru'] || '';
  document.getElementById('word-def').textContent = def;

  const transKey = lang === 'uz' ? 'trans_uz' : lang === 'kr' ? 'trans_kr' : 'trans_en';
  const transcription = w[transKey] || w['trans_en'] || '';
  document.getElementById('word-transcription').textContent = transcription;

  // Random background color
  const color = BG_COLORS[Math.floor(Math.random() * BG_COLORS.length)];
  document.getElementById('app').style.backgroundColor = color;
}

function renderError(msg) {
  document.getElementById('word-main').textContent = msg;
  document.getElementById('sub-a').textContent = '';
  document.getElementById('sub-b').textContent = '';
  document.getElementById('word-def').textContent = 'Open Settings → Update Word Base';
}

function loadSettings() {
  updateLangButtons(localStorage.getItem('primaryLang') || 'en');
}

function setPrimary(lang) {
  localStorage.setItem('primaryLang', lang);
  updateLangButtons(lang);
  if (currentId) {
    currentId = null;
    fetchWord();
  }
}

function updateLangButtons(active) {
  ['en', 'uz', 'kr'].forEach(l => {
    document.getElementById('lang-' + l).classList.toggle('active', l === active);
  });
}

async function loadStats() {
  try {
    const { word_count } = await (await fetch(API_BASE_URL + '/api/stats')).json();
    document.getElementById('word-counter').textContent = word_count + ' words';
  } catch (e) {
    /* silent */
  }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.code === 'Space') {
    e.preventDefault();
    nextWord();
  }
});
