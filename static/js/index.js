// Uncurated samples (App. J of the paper): the first 64 samples of the main configuration, (lambda, zeta) = (0.1, 0.9),
// d_z = 256, first training seed, guidance w = 2. FIDs are the w = 2 rows of Tables 2 and 3 (three-seed means).
const SAMPLE_SETS = {
  fmnist: { label: 'FashionMNIST', res: '32×32', learned: '6.8 ± 0.7', prior: '21.9 ± 0.7' },
  cifar10: { label: 'CIFAR10', res: '32×32', learned: '21.3 ± 0.7', prior: '33.7 ± 1.0' },
  celeba: { label: 'CelebA', res: '64×64', learned: '6.3 ± 0.2', prior: '11.1 ± 0.3' },
  ffhq: { label: 'FFHQ', res: '64×64', learned: '9.8 ± 0.3', prior: '15.7 ± 0.7' },
};

const state = { set: 'celeba' };

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'text') node.textContent = v;
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) node.append(c);
  return node;
}

function renderTabs() {
  const tabs = document.getElementById('sample-tabs');
  tabs.replaceChildren(...Object.entries(SAMPLE_SETS).map(([key, s]) => {
    const a = el('a', { href: '#samples', role: 'tab', 'aria-selected': String(key === state.set), text: s.label });
    a.addEventListener('click', (e) => {
      e.preventDefault();
      state.set = key;
      renderSamples();
    });
    return el('li', { class: key === state.set ? 'is-active' : '' }, a);
  }));
}

function panel(key, kind, title, fid) {
  const s = SAMPLE_SETS[key];
  return el('figure', { class: `sample-panel${kind === 'learned' ? ' is-learned' : ''}` }, [
    el('img', {
      src: `static/samples/${key}_${kind}_w2.png`, alt: `64 uncurated ${s.label} samples, ${title}`,
      loading: 'lazy', width: '521', height: '521',
    }),
    el('figcaption', {}, [title, el('span', { class: 'fid', text: `FID ${fid} (w = 2)` })]),
  ]);
}

function renderSamples() {
  renderTabs();
  const s = SAMPLE_SETS[state.set];
  document.getElementById('sample-pair').replaceChildren(
    panel(state.set, 'learned', 'z from the learned latent prior', s.learned),
    panel(state.set, 'prior', 'z ~ p(z) = N(0, I)', s.prior),
  );
  document.getElementById('sample-note').textContent =
    `${s.label}, ${s.res}. 64 samples per panel, first training seed, guidance w = 2, 50 Heun steps.`;
}

// ---- BibTeX ----
function setupCopy() {
  const btn = document.getElementById('copy-bibtex');
  btn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(document.getElementById('bibtex-code').textContent);
      btn.textContent = 'Copied';
    } catch (e) {
      btn.textContent = 'Select and copy';
    }
    setTimeout(() => { btn.textContent = 'Copy'; }, 1600);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  setupCopy();
  renderSamples();
});
