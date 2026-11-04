// Runs a generated create-forms.gs against a minimal FormApp mock and prints what it built as JSON.
// Usage: node scripts/tests/mock_apps_script.js path/to/create-forms.gs
'use strict';
const fs = require('fs');
const vm = require('vm');

const built = [];
const calls = [];

function chain(kind, record) {
  const target = { kind, ...record };
  return new Proxy(target, {
    get(obj, prop) {
      if (prop in obj) return obj[prop];
      if (typeof prop !== 'string') return undefined;
      return (...args) => {
        calls.push(`${kind}.${prop}`);
        if (prop === 'setChoiceValues' || prop === 'setRows' || prop === 'setColumns') {
          const values = args[0];
          if (!Array.isArray(values) || values.length === 0) throw new Error(`${kind}.${prop} needs a list`);
          if (new Set(values).size !== values.length) throw new Error(`${kind}.${prop}: duplicate values`);
        }
        if (prop === 'setBounds' && (args[0] > 1 || args[1] < 3 || args[1] > 10)) {
          throw new Error('setBounds out of range');
        }
        if (prop === 'setTitle' && (!args[0] || typeof args[0] !== 'string')) throw new Error('empty title');
        obj[prop + ':args'] = args;
        return new Proxy(obj, this);
      };
    },
  });
}

function makeForm(title) {
  const form = { title, items: [], published: false, accepting: false };
  const api = {
    setDescription: (d) => { form.description = d; return api; },
    setProgressBar: () => api, setCollectEmail: () => api, setAllowResponseEdits: () => api,
    setShowLinkToRespondAgain: () => api, setConfirmationMessage: (m) => { form.confirmation = m; return api; },
    setCustomClosedFormMessage: () => api, setLimitOneResponsePerUser: () => api,
    supportsAdvancedResponderPermissions: () => true,
    setPublished: (v) => { form.published = v; return api; },
    setAcceptingResponses: (v) => {
      if (v && !form.published) throw new Error('setAcceptingResponses on an unpublished form');
      form.accepting = v; return api;
    },
    getEditUrl: () => `https://docs.google.com/forms/d/${form.id}/edit`,
    getPublishedUrl: () => `https://docs.google.com/forms/d/e/${form.id}/viewform`,
    shortenFormUrl: () => `https://forms.gle/${form.id.slice(0, 8)}`,
    setDestination: () => api, getId: () => form.id, getResponses: () => [],
  };
  form.id = 'F' + (built.length + 1) + 'abcdefgh';
  for (const name of ['TextItem', 'ParagraphTextItem', 'MultipleChoiceItem', 'CheckboxItem', 'ListItem', 'ScaleItem',
    'GridItem', 'CheckboxGridItem', 'DateItem', 'TimeItem', 'PageBreakItem', 'SectionHeaderItem']) {
    api['add' + name] = () => { const item = chain(name, {}); form.items.push(item); return item; };
  }
  built.push(form);
  return api;
}

const validation = () => {
  const v = { setHelpText: () => v, requireTextIsEmail: () => v, requireNumber: () => v, build: () => ({}) };
  return v;
};

const sandbox = {
  FormApp: { create: makeForm, createTextValidation: validation, DestinationType: { SPREADSHEET: 'SPREADSHEET' } },
  SpreadsheetApp: { create: (t) => ({ getId: () => 'S1', getUrl: () => 'https://docs.google.com/spreadsheets/d/S1' }) },
  PropertiesService: { getScriptProperties: () => ({ setProperty: () => {}, getProperty: () => '0' }) },
  ScriptApp: { newTrigger: () => ({ forForm: () => ({ onFormSubmit: () => ({ create: () => ({}) }) }) }) },
  Logger: { log: () => {} },
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), sandbox);
const results = vm.runInContext('createAllForms()', sandbox);
console.log(JSON.stringify({
  results,
  forms: built.map((f) => ({ title: f.title, items: f.items.length, published: f.published, accepting: f.accepting })),
}, null, 2));
