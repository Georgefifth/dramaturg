const input = document.querySelector('#sceneInput');
const analyzeButton = document.querySelector('#analyze');
const sampleButton = document.querySelector('#loadSample');
const results = document.querySelector('#results');
const loading = document.querySelector('#loading');
let currentDossier = null;
let liveReady = false;
let decisions = {};

const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

async function loadConfig() {
  const config = await fetch('/api/config').then(response => response.json());
  liveReady = config.liveReady;
  document.querySelector('#modeDot').classList.toggle('ready', liveReady);
  document.querySelector('#modeLabel').textContent = liveReady ? 'Live verification ready' : 'Sample mode · add API keys for live';
  document.querySelector('#liveHint').textContent = liveReady
    ? `Live mode · ${config.rateLimitPerHour} new scenes per hour · repeated scenes use the evidence cache.`
    : 'Live analysis is unavailable. The clearly labeled evidence sample remains available.';
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
    ['Running the first search pass', 'Parallel is retrieving source-linked evidence for every claim…'],
    ['Auditing evidence coverage', 'Gemini is looking for gaps that could materially change a verdict…'],
    ['Researching targeted gaps', 'Parallel may run a focused second pass for up to two claims…'],
    ['Respecting the rate limit', 'Pausing before the evidence-constrained verification pass…'],
    ['Testing the complete record', 'Gemini is classifying sources and checking every claim…']
  ];
  let stage = 0;
  const timer = setInterval(() => {
    const item = stages[Math.min(stage++, stages.length - 1)];
    document.querySelector('#loadingTitle').textContent = item[0];
    document.querySelector('#loadingText').textContent = item[1];
  }, 8500);
  try {
    const response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({scene})});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'Analysis failed');
    renderDossier(payload);
    document.querySelector('#liveHint').textContent = response.headers.get('X-Dramaturg-Cache') === 'HIT'
      ? 'Loaded from the evidence cache. No provider calls were spent.'
      : 'Live dossier complete. Evidence is cached for repeated review.';
  } catch (error) {
    document.querySelector('#liveHint').textContent = error.message;
  } finally {
    clearInterval(timer);
    loading.classList.add('hidden');
    analyzeButton.disabled = !liveReady;
  }
});

function claimOffsets(verdict, scene) {
  let start = verdict.claim.start_offset;
  let end = verdict.claim.end_offset;
  if ((start === null || start === undefined) && verdict.claim.script_quote) {
    start = scene.toLowerCase().indexOf(verdict.claim.script_quote.toLowerCase());
    end = start >= 0 ? start + verdict.claim.script_quote.length : null;
  }
  return {start, end};
}

function renderAnnotatedScene(dossier) {
  const ranges = dossier.verdicts.map(verdict => ({...claimOffsets(verdict, dossier.scene), id:verdict.claim.id, status:verdict.status}))
    .filter(range => Number.isInteger(range.start) && Number.isInteger(range.end) && range.start >= 0 && range.end > range.start)
    .sort((a, b) => a.start - b.start);
  let cursor = 0;
  const parts = [];
  for (const range of ranges) {
    if (range.start < cursor) continue;
    parts.push(escapeHtml(dossier.scene.slice(cursor, range.start)));
    parts.push(`<button class="script-mark ${range.status}" data-claim-id="${escapeHtml(range.id)}">${escapeHtml(dossier.scene.slice(range.start, range.end))}</button>`);
    cursor = range.end;
  }
  parts.push(escapeHtml(dossier.scene.slice(cursor)));
  document.querySelector('#annotatedScene').innerHTML = parts.join('');
}

function renderDossier(dossier) {
  currentDossier = structuredClone(dossier);
  decisions = {};
  document.querySelector('#resultMode').textContent = dossier.mode === 'live' ? 'Live web evidence' : 'Curated evidence sample';
  document.querySelector('#dossierTitle').textContent = dossier.title;
  const order = [['total','Claims'],['verified','Verified'],['inaccurate','Inaccurate'],['conflicted','Conflicted'],['unverified','Unverified']];
  document.querySelector('#scoreGrid').innerHTML = order.map(([key,label]) => `<div class="score ${key}"><b>${dossier.summary[key] || 0}</b><span>${label}</span></div>`).join('');
  const traces = dossier.research_trace || [];
  const researched = traces.filter(trace => trace.status === 'RESEARCHED');
  const initialSources = traces.reduce((sum, trace) => sum + trace.initial_source_count, 0);
  const addedSources = traces.reduce((sum, trace) => sum + trace.added_source_count, 0);
  document.querySelector('#researchSummary').innerHTML = `<div><span class="step">Agent research trace</span><strong>${traces.length} coverage decisions</strong></div><div><b>${initialSources}</b><span>initial sources</span></div><div><b>${researched.length}</b><span>targeted re-searches</span></div><div><b>+${addedSources}</b><span>new sources found</span></div>`;
  const traceByClaim = Object.fromEntries(traces.map(trace => [trace.claim_id, trace]));
  renderAnnotatedScene(dossier);
  document.querySelector('#verdicts').innerHTML = dossier.verdicts.map(verdict => {
    const correction = verdict.correction ? `<div class="correction"><span class="finding-label">Production fix</span><p>${escapeHtml(verdict.correction)}</p></div>` : '';
    const trace = traceByClaim[verdict.claim.id];
    const queryText = trace?.refined_queries?.length ? `<div class="research-queries">${trace.refined_queries.map(query => `<code>${escapeHtml(query)}</code>`).join('')}</div>` : '';
    const researchTrace = trace ? `<div class="claim-research ${trace.status}"><span class="research-status">${trace.status === 'RESEARCHED' ? `Second pass · +${trace.added_source_count} sources` : trace.status === 'SUFFICIENT' ? 'Coverage sufficient' : 'Evidence gap remains'}</span><p>${escapeHtml(trace.rationale)}</p>${queryText}</div>` : '';
    const cited = new Set(verdict.citations || []);
    const sources = verdict.sources.map(source => `<a class="source ${cited.has(source.id) ? 'cited' : ''}" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer"><div class="source-head"><strong><span class="source-id">[${escapeHtml(source.id)}]</span>${escapeHtml(source.title)} ↗</strong><span class="source-stance ${escapeHtml(source.stance || 'CONTEXT')}">${escapeHtml(source.stance || 'CONTEXT')}</span></div><span>${escapeHtml(source.excerpt)}</span></a>`).join('');
    return `<article id="verdict-${escapeHtml(verdict.claim.id)}" class="verdict" data-claim-id="${escapeHtml(verdict.claim.id)}"><div class="verdict-top"><span class="badge ${verdict.status}">${verdict.status}</span><div><div class="claim-category">${escapeHtml(verdict.claim.id)} · ${escapeHtml(verdict.claim.category)}</div><div class="claim-text">“${escapeHtml(verdict.claim.text)}”</div></div><div class="confidence"><b>${verdict.confidence}%</b><span>confidence</span></div></div>${researchTrace}<div class="finding"><span class="finding-label">Finding</span><div><p>${escapeHtml(verdict.finding)}</p>${correction}</div></div><div class="sources"><span class="finding-label">Parallel evidence</span><div class="source-list">${sources || '<span>No usable sources returned</span>'}</div></div><div class="decision-block"><span class="finding-label">Writer decision</span><div><div class="decision-actions"><button class="decision-button" data-decision="ACCEPT_FIX">Accept fix</button><button class="decision-button" data-decision="KEEP_AS_WRITTEN">Keep as written</button><button class="decision-button" data-decision="NEEDS_RESEARCH">Needs research</button></div><input class="decision-note" maxlength="240" placeholder="Optional rationale for the production record"></div></div></article>`;
  }).join('');
  updateDecisionSummary();
  results.classList.remove('hidden');
  results.scrollIntoView({behavior:'smooth', block:'start'});
}

function focusClaim(id, scrollTarget) {
  document.querySelectorAll('.verdict,.script-mark').forEach(element => element.classList.remove('active'));
  document.querySelector(`#verdict-${CSS.escape(id)}`)?.classList.add('active');
  document.querySelector(`.script-mark[data-claim-id="${CSS.escape(id)}"]`)?.classList.add('active');
  if (scrollTarget === 'verdict') document.querySelector(`#verdict-${CSS.escape(id)}`)?.scrollIntoView({behavior:'smooth', block:'center'});
  if (scrollTarget === 'script') document.querySelector(`.script-mark[data-claim-id="${CSS.escape(id)}"]`)?.scrollIntoView({behavior:'smooth', block:'center'});
}

document.querySelector('#annotatedScene').addEventListener('click', event => {
  const mark = event.target.closest('.script-mark');
  if (mark) focusClaim(mark.dataset.claimId, 'verdict');
});

document.querySelector('#verdicts').addEventListener('click', event => {
  const card = event.target.closest('.verdict');
  if (!card) return;
  const decisionButton = event.target.closest('.decision-button');
  if (decisionButton) {
    setDecision(card, decisionButton.dataset.decision);
    return;
  }
  if (!event.target.closest('a,input,button')) focusClaim(card.dataset.claimId, 'script');
});

document.querySelector('#verdicts').addEventListener('input', event => {
  if (!event.target.classList.contains('decision-note')) return;
  const id = event.target.closest('.verdict').dataset.claimId;
  if (decisions[id]) decisions[id].note = event.target.value.trim();
});

function setDecision(card, decision) {
  const id = card.dataset.claimId;
  decisions[id] = {decision, note:decisions[id]?.note || '', decided_at:new Date().toISOString()};
  card.classList.add('decided');
  card.querySelectorAll('.decision-button').forEach(button => button.classList.toggle('selected', button.dataset.decision === decision));
  const note = card.querySelector('.decision-note');
  note.classList.toggle('visible', decision !== 'ACCEPT_FIX');
  updateDecisionSummary();
}

function updateDecisionSummary() {
  const total = currentDossier?.verdicts.length || 0;
  const values = Object.values(decisions);
  document.querySelector('#decisionCount').textContent = `${values.length} of ${total} decisions made`;
  document.querySelector('#decisionProgress').style.width = `${total ? values.length / total * 100 : 0}%`;
  const labels = {ACCEPT_FIX:'accepted', KEEP_AS_WRITTEN:'kept', NEEDS_RESEARCH:'research'};
  const counts = values.reduce((result, item) => ({...result, [item.decision]:(result[item.decision] || 0) + 1}), {});
  document.querySelector('#decisionBreakdown').textContent = values.length
    ? Object.entries(counts).map(([key,value]) => `${value} ${labels[key]}`).join(' · ')
    : 'The writer retains final authority.';
}

document.querySelector('#exportBtn').addEventListener('click', () => {
  if (!currentDossier) return;
  const decisionLog = currentDossier.verdicts.map(verdict => ({claim_id:verdict.claim.id, claim:verdict.claim.text, ...(decisions[verdict.claim.id] || {decision:'PENDING', note:'', decided_at:null})}));
  const exported = {...currentDossier, decision_log:decisionLog, exported_at:new Date().toISOString()};
  const blob = new Blob([JSON.stringify(exported, null, 2)], {type:'application/json'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'dramaturg-accuracy-dossier.json';
  link.click();
  URL.revokeObjectURL(link.href);
});

loadConfig().catch(() => document.querySelector('#modeLabel').textContent = 'Service status unavailable');
