#!/usr/bin/env node
/**
 * npm run i18n:translate [-- --only=hi,ta] [-- --dry-run]
 *
 * For every language in src/i18n/languages.json, translate ONLY the English
 * strings that are new or changed since the last run, with Gemini, and write
 * src/i18n/<code>.ts. Existing translations (including hand edits) are kept.
 * Review the diff and commit it — builds never call the AI.
 *
 * Auth (one of):
 *   GEMINI_API_KEY=...                      Google AI Studio key
 *   gcloud auth login (default)             Vertex AI; project from GOOGLE_CLOUD_PROJECT or gcloud config
 * Options: I18N_MODEL (default gemini-3.5-flash-lite), I18N_LOCATION (Vertex, default global)
 */

import { execSync } from 'node:child_process';
import { diffLanguage, hash, languages, loadDict, loadHashes, placeholders, saveHashes, writeDict } from './i18n-lib.mjs';

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')));
const only = args.only ? String(args.only).split(',') : null;
const dryRun = 'dry-run' in args;
const MODEL = process.env.I18N_MODEL || 'gemini-3.5-flash-lite';
const CHUNK = 40;

function endpoint() {
    if (process.env.GEMINI_API_KEY) {
        return {
            url: `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${process.env.GEMINI_API_KEY}`,
            headers: {},
        };
    }
    const sh = (cmd) => execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    const project = process.env.GOOGLE_CLOUD_PROJECT || sh('gcloud config get-value project');
    const location = process.env.I18N_LOCATION || 'global';
    const host = location === 'global' ? 'aiplatform.googleapis.com' : `${location}-aiplatform.googleapis.com`;
    return {
        url: `https://${host}/v1/projects/${project}/locations/${location}/publishers/google/models/${MODEL}:generateContent`,
        headers: { Authorization: `Bearer ${sh('gcloud auth print-access-token')}` },
    };
}

async function translateChunk(api, meta, strings) {
    const prompt = `Translate these user-interface strings of CropSense, a farming and livestock app for Indian farmers, from English into ${meta.name} (${meta.label}).
Rules:
- Simple everyday words a village farmer understands; natural, not word-for-word.
- Keep every {placeholder} exactly as written (e.g. {name}, {n}).
- Keep emoji, ₹, numbers, and names like CropSense, WhatsApp, AI unchanged.
- Keep it about as short as the English (these are buttons and labels).
Return ONLY a JSON object with exactly the same keys and the translated strings as values.

${JSON.stringify(strings, null, 1)}`;

    const res = await fetch(api.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...api.headers },
        body: JSON.stringify({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.2, responseMimeType: 'application/json' },
        }),
    });
    if (!res.ok) throw new Error(`Gemini ${res.status}: ${(await res.text()).slice(0, 300)}`);
    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.map((p) => p.text || '').join('') || '{}';
    return JSON.parse(text.slice(text.indexOf('{'), text.lastIndexOf('}') + 1));
}

const { en } = await import('../src/i18n/en.ts');
const hashes = loadHashes();
const targets = languages().filter((l) => l.code !== 'en' && (!only || only.includes(l.code)));
let api = null;
let failed = false;

for (const meta of targets) {
    if (!/^[a-z]{2,3}$/.test(meta.code)) {
        console.error(`✗ ${meta.code}: language codes must be 2-3 lowercase letters`);
        failed = true;
        continue;
    }
    const dict = { ...((await loadDict(meta.code)) || {}) };
    const langHashes = (hashes[meta.code] ||= {});
    const { todo, adopted } = diffLanguage(en, dict, langHashes);

    for (const key of adopted) langHashes[key] = hash(en[key]);
    console.log(`${meta.code} (${meta.name}): ${todo.length} to translate, ${Object.keys(en).length - todo.length} up to date`);
    if (!todo.length || dryRun) {
        if (dryRun && todo.length) console.log(`  would translate: ${todo.join(', ')}`);
        continue;
    }

    api ||= endpoint();
    for (let i = 0; i < todo.length; i += CHUNK) {
        const keys = todo.slice(i, i + CHUNK);
        try {
            const out = await translateChunk(api, meta, Object.fromEntries(keys.map((k) => [k, en[k]])));
            for (const key of keys) {
                const value = out[key];
                if (typeof value !== 'string' || !value.trim()) {
                    console.warn(`  ! ${key}: no translation returned (English will show)`);
                } else if (placeholders(value) !== placeholders(en[key])) {
                    console.warn(`  ! ${key}: placeholders changed ("${value}") — skipped`);
                } else {
                    dict[key] = value.trim();
                    langHashes[key] = hash(en[key]);
                }
            }
        } catch (err) {
            console.error(`  ✗ ${meta.code} chunk ${i / CHUNK + 1}: ${err.message}`);
            failed = true;
        }
    }
    writeDict(meta.code, en, dict, meta);
    console.log(`  ✓ wrote src/i18n/${meta.code}.ts`);
}

if (!dryRun) saveHashes(hashes);
process.exit(failed ? 1 : 0);
