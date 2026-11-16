import { createChart, createTable, csvDownload, get, setOptions, subtractMonths } from './series.mjs';

const fields = Object.fromEntries(['group', 'primary', 'comparison', 'from', 'through'].map(id => [id, get(id)]));
const chart = createChart();
const table = createTable();
const days = [...document.querySelectorAll('[data-months]')];
let data;
let exportData;
const nativeFormatters = {
  rates: value => value.toFixed(2) + '%',
  fx: value => value.toFixed(value < .1 ? 6 : 4),
  index: value => value.toFixed(2),
};
const presets = {
  rates: ['V39079', 'BD.CDN.5YR.DQ.YLD'],
  fx: ['FXUSDCAD', 'FXEURCAD'],
  index: ['FXUSDCAD', 'FXEURCAD'],
};

function latest(key) {
  const values = data.tracks[key].data;
  const index = values.findLastIndex(Number.isFinite);
  return [values[index], data.dates[index]];
}

function renderOverview() {
  for (const [id, key, group] of [
    ['policy', 'V39079', 'rates'], ['bond', 'BD.CDN.5YR.DQ.YLD', 'rates'], ['fx', 'FXUSDCAD', 'fx'],
  ]) {
    const [value, date] = latest(key);
    get('hero-' + id).textContent = nativeFormatters[group](value);
    get('hero-' + id + '-date').textContent = ' · ' + date;
  }
  get('snapshot').textContent = 'Snapshot built ' + data.built.slice(0, 10) + ' UTC';
}

function seriesOptions(primary, comparison) {
  const group = fields.group.value === 'rates' ? 'rates' : 'fx';
  const rows = Object.entries(data.tracks).filter(([, track]) => track.group === group)
    .map(([key, track]) => [key, track.label]);
  setOptions(fields.primary, rows, primary);
  setOptions(fields.comparison, [['', 'None'], ...rows.filter(([key]) => key !== fields.primary.value)], comparison);
}

function range(months) {
  const last = data.dates.at(-1);
  const target = months ? subtractMonths(last, months) : data.dates[0];
  fields.from.value = target < data.dates[0] ? data.dates[0] : target;
  fields.through.value = last;
}

function showStatus(message, isError = false) {
  const status = get('status');
  status.textContent = message;
  status.classList.toggle('error', isError);
  status.hidden = !message;
}

function render() {
  const min = fields.from.value;
  const max = fields.through.value;
  const group = fields.group.value;
  const ids = [fields.primary.value, fields.comparison.value].filter(Boolean);
  const indexes = data.dates.map((_, n) => n).filter(n => data.dates[n] >= min && data.dates[n] <= max
    && ids.some(key => Number.isFinite(data.tracks[key].data[n])));
  const badRange = !min || !max || min > max;
  days.forEach(button => button.setAttribute('aria-pressed', String(max === data.dates.at(-1)
    && min === (Number(button.dataset.months) ? subtractMonths(max, Number(button.dataset.months)) : data.dates[0]))));
  get('plot').hidden = badRange || !indexes.length;
  get('export').disabled = get('plot').hidden;
  if (get('plot').hidden) {
    showStatus(badRange ? 'Choose a start date on or before the end date.' : 'No observations for the selected series and date range.');
    return;
  }
  showStatus('');
  const dates = indexes.map(n => data.dates[n]);
  const format = nativeFormatters[group];
  const tracks = ids.map(key => {
    const track = data.tracks[key];
    const raw = indexes.map(n => track.data[n]);
    const baseline = raw.findIndex(Number.isFinite);
    return {
      label: track.label,
      raw,
      baseline,
      step: key === 'V39079' || key === 'V39078',
      values: group === 'index' ? raw.map(value => value === null ? null : 100 * value / raw[baseline]) : raw,
    };
  });
  chart({ dates, tracks, format, breakGaps: false });
  get('chart-title').textContent = tracks.map(track => track.label).join(' and ');
  const shown = group === 'rates' ? 'Percent' : group === 'fx'
    ? 'Canadian dollars per unit of each selected currency' : 'Indexed to 100 at the first available observation';
  const baselineNote = group === 'index' ? ' · ' + tracks.filter(t => t.baseline >= 0).map(t => t.label + ' starts ' + dates[t.baseline]).join(' · ') : '';
  get('chart-description').textContent = shown + ' · ' + dates.length.toLocaleString('en-CA') + ' observation dates' + baselineNote;
  const endpoint = 'https://www.bankofcanada.ca/valet/observations/' + ids.join(',') + '/json';
  get('source-link').href = endpoint + '?' + new URLSearchParams({ start_date: min, end_date: max });
  table(['Date', ...tracks.map(track => track.label)], dates.map((date, n) => [
    date, ...tracks.map(track => Number.isFinite(track.values[n]) ? format(track.values[n]) : '—'),
  ]));
  exportData = {
    headings: ['date', ...ids.map(id => id + ' (' + data.tracks[id].unit + ')')],
    rows: dates.map((date, n) => [date, ...tracks.map(track => track.raw[n])]),
  };
  history.replaceState(null, '', '?' + new URLSearchParams({
    view: group, series: ids[0], compare: ids[1] ?? '', from: min, through: max,
  }));
}

fields.group.addEventListener('change', () => {
  seriesOptions(...presets[fields.group.value]);
  render();
});
fields.primary.addEventListener('change', () => {
  seriesOptions(fields.primary.value, fields.comparison.value);
  render();
});
[fields.comparison, fields.from, fields.through].forEach(field => field.addEventListener('change', render));
days.forEach(button => button.addEventListener('click', () => { range(Number(button.dataset.months)); render(); }));
get('export').addEventListener('click', () => csvDownload('bankrate-lab-observations.csv', exportData.headings, exportData.rows));

async function load() {
  get('retry').hidden = true;
  showStatus('Loading observations…');
  try {
    const response = await fetch('./snapshot.json');
    if (!response.ok) throw new Error('Snapshot HTTP ' + response.status);
    data = await response.json();
    if (!data.dates?.length || !data.tracks) throw new Error('Invalid snapshot');
    renderOverview();
    const query = new URLSearchParams(location.search);
    const group = query.get('view');
    if (Object.hasOwn(presets, group)) fields.group.value = group;
    seriesOptions(query.get('series') ?? presets[fields.group.value][0], query.get('compare') ?? presets[fields.group.value][1]);
    for (const key of ['from', 'through']) {
      fields[key].min = data.dates[0];
      fields[key].max = data.dates.at(-1);
    }
    range(12);
    for (const key of ['from', 'through']) {
      const value = query.get(key);
      if (/^\d{4}-\d{2}-\d{2}$/.test(value ?? '') && value >= fields[key].min && value <= fields[key].max) fields[key].value = value;
    }
    get('controls').hidden = false;
    render();
  } catch (error) {
    get('snapshot').textContent = 'Data unavailable';
    showStatus('Could not open the data snapshot. Retry, or use the official source links below.', true);
    get('retry').hidden = false;
  }
}
get('retry').addEventListener('click', load);
load();
