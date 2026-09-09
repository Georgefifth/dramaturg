const input = document.querySelector('#sceneInput');
const analyzeButton = document.querySelector('#analyze');
const sampleButton = document.querySelector('#loadSample');
const results = document.querySelector('#results');
const loading = document.querySelector('#loading');
let currentDossier = null;
let liveReady = false;

const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

async function loadConfig() {
  const config = await fetch('/api/config').then(response => response.json());
  liveReady = config.liveReady;
  document.querySelector('#modeDot').classList.toggle('ready', liveReady);
  document.querySelector('#modeLabel').textContent = liveReady ? 'Live verification ready' : 'Sample mode · add API keys for live';
  document.querySelector('#liveHint').textContent = liveReady
    ? 'Live mode will call Gemini and Parallel Search for this scene.'
    : 'Live analysis is locked until GEMINI_API_KEY and PARALLEL_API_KEY are configured. The evidence sample remains available.';
  analyzeButton.disabled = !liveReady;
}

function setScene(scene) {
  input.value = scene;
  document.querySelector('#charCount').textContent = `${scene.length.toLocaleString()} / 12,000`;
}

input.addEventListener('input', () => document.querySelector('#charCount').textContent = `${input.value.length.toLocaleString()} / 12,000`);

sampleButton.addEventListener('click', async () => {
  sampleButton.disabled = true;
  try {
    const {scene} = await fetch('/api/demo-scene').then(response => response.json());
    setScene(scene);
    const dossier = await fetch('/api/demo').then(response => response.json());
    renderDossier(dossier);
  } finally {
    sampleButton.disabled = false;
  }
});

analyzeButton.addEventListener('click', async () => {
  const scene = input.value.trim();
  if (scene.length < 80) {
    document.querySelector('#liveHint').textContent = 'Add at least 80 characters of screenplay text before verification.';
    input.focus();
    return;
  }
  analyzeButton.disabled = true;
  results.classList.add('hidden');
  loading.classList.remove('hidden');
  const stages = [
    ['Extracting claims', 'Gemini is isolating dates, places, procedures, and period details…'],
    ['Searching the live web', 'Parallel is retrieving source-linked evidence for every claim…'],
    ['Testing the evidence', 'Gemini is comparing each claim only against retrieved sources…']
  ];
  let stage = 0;
  const timer = setInterval(() => {
    const item = stages[Math.min(stage++, stages.length - 1)];
    document.querySelector('#loadingTitle').textContent = item[0];
    document.querySelector('#loadingText').textContent = item[1];
  }, 1800);
  try {
    const response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({scene})});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'Analysis failed');
    renderDossier(payload);
  } catch (error) {
    document.querySelector('#liveHint').textContent = error.message;
  } finally {
    clearInterval(timer);
    loading.classList.add('hidden');
    analyzeButton.disabled = !liveReady;
  }
});

function renderDossier(dossier) {
  currentDossier = dossier;
  document.querySelector('#resultMode').textContent = dossier.mode === 'live' ? 'Live web evidence' : 'Curated evidence sample';
  document.querySelector('#dossierTitle').textContent = dossier.title;
  const order = [['total','Claims'],['verified','Verified'],['inaccurate','Inaccurate'],['conflicted','Conflicted'],['unverified','Unverified']];
  document.querySelector('#scoreGrid').innerHTML = order.map(([key,label]) => `<div class="score ${key}"><b>${dossier.summary[key] || 0}</b><span>${label}</span></div>`).join('');
  document.querySelector('#verdicts').innerHTML = dossier.verdicts.map(verdict => {
    const correction = verdict.correction ? `<div class="correction"><span class="finding-label">Production fix</span><p>${escapeHtml(verdict.correction)}</p></div>` : '';
    const sources = verdict.sources.map(source => `<a class="source" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer"><strong>${escapeHtml(source.title)} ↗</strong><span>${escapeHtml(source.excerpt)}</span></a>`).join('');
    return `<article class="verdict"><div class="verdict-top"><span class="badge ${verdict.status}">${verdict.status}</span><div><div class="claim-category">${escapeHtml(verdict.claim.id)} · ${escapeHtml(verdict.claim.category)}</div><div class="claim-text">“${escapeHtml(verdict.claim.text)}”</div></div><div class="confidence"><b>${verdict.confidence}%</b><span>confidence</span></div></div><div class="finding"><span class="finding-label">Finding</span><div><p>${escapeHtml(verdict.finding)}</p>${correction}</div></div><div class="sources"><span class="finding-label">Parallel evidence</span><div class="source-list">${sources || '<span>No usable sources returned</span>'}</div></div></article>`;
  }).join('');
  results.classList.remove('hidden');
  results.scrollIntoView({behavior:'smooth', block:'start'});
}

document.querySelector('#exportBtn').addEventListener('click', () => {
  if (!currentDossier) return;
  const blob = new Blob([JSON.stringify(currentDossier, null, 2)], {type:'application/json'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'dramaturg-accuracy-dossier.json';
  link.click();
  URL.revokeObjectURL(link.href);
});

loadConfig().catch(() => document.querySelector('#modeLabel').textContent = 'Service status unavailable');
