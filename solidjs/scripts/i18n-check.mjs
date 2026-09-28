#!/usr/bin/env node
/**
 * npm run i18n:check [-- --strict]
 *
 * Offline check (no AI): for each language in src/i18n/languages.json, report
 * strings that are missing, out of date (English changed), or have broken
 * {placeholders}. Runs before every build as a warning; --strict exits 1 so
 * CI can block a release with untranslated text.
 */

import { diffLanguage, languages, loadDict, loadHashes } from './i18n-lib.mjs';

const strict = process.argv.includes('--strict');
const { en } = await import('../src/i18n/en.ts');
const hashes = loadHashes();
let problems = 0;

for (const meta of languages().filter((l) => l.code !== 'en')) {
    const dict = await loadDict(meta.code);
    if (!dict) {
        console.warn(`⚠ ${meta.code} (${meta.name}): no src/i18n/${meta.code}.ts yet — run npm run i18n:translate`);
        problems++;
        continue;
    }
    const { todo, badPlaceholders } = diffLanguage(en, dict, hashes[meta.code] || {});
    if (todo.length) console.warn(`⚠ ${meta.code} (${meta.name}): ${todo.length} new/changed strings need translating`);
    for (const key of badPlaceholders) console.warn(`⚠ ${meta.code}: "${key}" placeholders differ from English`);
    problems += todo.length + badPlaceholders.length;
}

if (problems) {
    console.warn(`i18n: ${problems} issue(s). Missing text shows in English. Fix with: npm run i18n:translate`);
    process.exit(strict ? 1 : 0);
}
console.log('i18n: all languages up to date');
