/**
 * SLUSI WMS API Explorer
 *
 * Navigates to soilhealth.dac.gov.in/slusi-visualisation/, selects a state/district,
 * intercepts ALL WMS network requests, and saves the full request/response details
 * to a JSON file for analysis.
 *
 * Usage:
 *   npx playwright test tools/slusi/explore_wms_api.ts --headed
 *
 * Or run directly:
 *   npx ts-node tools/slusi/explore_wms_api.ts
 *
 * Output: tools/slusi/wms_requests_captured.json
 */

import { chromium, Page, Request, Response } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

const TARGET_URL = 'https://soilhealth.dac.gov.in/slusi-visualisation/';

// States and districts to probe — edit these to test different locations
const PROBE_LOCATIONS = [
  { state: 'HIMACHAL PRADESH', district: 'KANGRA' },
  { state: 'HIMACHAL PRADESH', district: 'CHAMBA' },
  { state: 'TELANGANA', district: 'JAYASHANKAR BHUPALLY' },
];

interface CapturedRequest {
  url: string;
  method: string;
  params: Record<string, string>;
  status: number;
  contentType: string;
  timestamp: string;
  // Parsed WMS params
  wms?: {
    request: string;       // GetMap, GetFeatureInfo, GetLegendGraphic
    service: string;
    version: string;
    layers?: string;
    styles?: string;
    format?: string;
    bbox?: string;
    crs?: string;
    width?: string;
    height?: string;
    queryLayers?: string;
    infoFormat?: string;
    x?: string;
    y?: string;
    featureCount?: string;
  };
}

function parseWmsParams(url: string): Record<string, string> {
  const parsed: Record<string, string> = {};
  try {
    const urlObj = new URL(url);
    urlObj.searchParams.forEach((value, key) => {
      parsed[key.toUpperCase()] = value;
    });
  } catch {}
  return parsed;
}

function extractWmsInfo(params: Record<string, string>) {
  return {
    request: params['REQUEST'],
    service: params['SERVICE'],
    version: params['VERSION'],
    layers: params['LAYERS'],
    styles: params['STYLES'],
    format: params['FORMAT'],
    bbox: params['BBOX'],
    crs: params['CRS'] || params['SRS'],
    width: params['WIDTH'],
    height: params['HEIGHT'],
    queryLayers: params['QUERY_LAYERS'],
    infoFormat: params['INFO_FORMAT'],
    x: params['X'] || params['I'],
    y: params['Y'] || params['J'],
    featureCount: params['FEATURE_COUNT'],
  };
}

async function captureWmsRequests(state: string, district: string): Promise<CapturedRequest[]> {
  const captured: CapturedRequest[] = [];
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Intercept all WMS requests
  page.on('request', (request: Request) => {
    const url = request.url();
    if (url.includes('/shc/wms') || url.includes('soilhealth.dac.gov.in')) {
      const params = parseWmsParams(url);
      if (params['REQUEST']) {
        captured.push({
          url,
          method: request.method(),
          params,
          status: 0,
          contentType: '',
          timestamp: new Date().toISOString(),
          wms: extractWmsInfo(params),
        });
      }
    }
  });

  page.on('response', async (response: Response) => {
    const url = response.url();
    if (url.includes('/shc/wms') || url.includes('soilhealth.dac.gov.in')) {
      const entry = captured.find(r => r.url === url && r.status === 0);
      if (entry) {
        entry.status = response.status();
        entry.contentType = response.headers()['content-type'] || '';

        // For GetFeatureInfo responses, capture the actual response body
        if (entry.wms?.request === 'GetFeatureInfo') {
          try {
            const body = await response.text();
            (entry as any).responseBody = body;
          } catch {}
        }
      }
    }
  });

  console.log(`\n=== Probing: ${state} / ${district} ===`);

  await page.goto(TARGET_URL, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);

  // Select state
  console.log(`Selecting state: ${state}`);
  const stateSelect = page.locator('select').first();
  await stateSelect.selectOption({ label: state }).catch(async () => {
    // Try by value or partial text
    const options = await stateSelect.locator('option').allTextContents();
    console.log('Available states:', options.slice(0, 10));
    const match = options.find(o => o.toUpperCase().includes(state.split(' ')[0]));
    if (match) await stateSelect.selectOption({ label: match });
  });
  await page.waitForTimeout(2000);

  // Select district
  console.log(`Selecting district: ${district}`);
  const districtSelect = page.locator('select').nth(1);
  await districtSelect.selectOption({ label: district }).catch(async () => {
    const options = await districtSelect.locator('option').allTextContents();
    console.log('Available districts:', options.slice(0, 10));
    const match = options.find(o => o.toUpperCase().includes(district.split(' ')[0]));
    if (match) await districtSelect.selectOption({ label: match });
  });
  await page.waitForTimeout(3000);

  // Enable Soil Resource Mapping checkbox if not already checked
  const srmCheckbox = page.locator('input[type="checkbox"]').first();
  const isChecked = await srmCheckbox.isChecked().catch(() => false);
  if (!isChecked) {
    await srmCheckbox.click();
    await page.waitForTimeout(2000);
  }

  // Click on the map to trigger GetFeatureInfo requests
  console.log('Clicking map to trigger GetFeatureInfo...');
  const mapCanvas = page.locator('canvas').first();
  const box = await mapCanvas.boundingBox();
  if (box) {
    // Click center of map
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(3000);

    // Click a few more spots to get more data
    await page.mouse.click(box.x + box.width * 0.3, box.y + box.height * 0.4);
    await page.waitForTimeout(2000);
  }

  // Try each nutrient radio button
  const nutrients = ['Nitrogen', 'Phosphorus', 'Potassium', 'Zinc', 'Copper', 'pH'];
  for (const nutrient of nutrients) {
    const radio = page.locator(`text=${nutrient}`).first();
    await radio.click().catch(() => {});
    await page.waitForTimeout(1500);
    if (box) {
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      await page.waitForTimeout(1500);
    }
  }

  await browser.close();
  return captured;
}

async function main() {
  const allResults: Record<string, CapturedRequest[]> = {};

  for (const location of PROBE_LOCATIONS) {
    const key = `${location.state}__${location.district}`;
    try {
      const requests = await captureWmsRequests(location.state, location.district);
      allResults[key] = requests;

      // Print summary
      console.log(`\n--- ${key} ---`);
      console.log(`Total WMS requests captured: ${requests.length}`);

      const byType = requests.reduce((acc, r) => {
        const type = r.wms?.request || 'unknown';
        acc[type] = (acc[type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      console.log('By request type:', byType);

      // Print unique layer+styles combos
      const layerCombos = new Set(
        requests
          .filter(r => r.wms?.layers)
          .map(r => `layers=${r.wms?.layers} styles=${r.wms?.styles}`)
      );
      console.log('\nUnique layer+styles combinations:');
      layerCombos.forEach(c => console.log(' ', c));

      // Print GetFeatureInfo details
      const featureInfoRequests = requests.filter(r => r.wms?.request === 'GetFeatureInfo');
      if (featureInfoRequests.length > 0) {
        console.log('\nGetFeatureInfo requests:');
        featureInfoRequests.forEach(r => {
          console.log(`  layers=${r.wms?.layers} styles=${r.wms?.styles} status=${r.status}`);
          if ((r as any).responseBody) {
            console.log(`  response: ${(r as any).responseBody.substring(0, 200)}`);
          }
        });
      } else {
        console.log('\n⚠️  No GetFeatureInfo requests captured — map click may not have triggered them');
        console.log('   Try clicking directly on a colored area on the map');
      }

    } catch (err) {
      console.error(`Failed for ${key}:`, err);
      allResults[key] = [];
    }
  }

  // Save full results
  const outputPath = path.join(__dirname, 'wms_requests_captured.json');
  fs.writeFileSync(outputPath, JSON.stringify(allResults, null, 2));
  console.log(`\n✅ Full results saved to: ${outputPath}`);

  // Print analysis summary
  console.log('\n=== ANALYSIS SUMMARY ===');
  for (const [key, requests] of Object.entries(allResults)) {
    const getMapRequests = requests.filter(r => r.wms?.request === 'GetMap');
    const getFeatureInfoRequests = requests.filter(r => r.wms?.request === 'GetFeatureInfo');

    console.log(`\n${key}:`);
    console.log(`  GetMap requests: ${getMapRequests.length}`);
    console.log(`  GetFeatureInfo requests: ${getFeatureInfoRequests.length}`);

    if (getMapRequests.length > 0) {
      const sample = getMapRequests[0];
      console.log(`  Sample GetMap layer: ${sample.wms?.layers}`);
      console.log(`  Sample GetMap styles: ${sample.wms?.styles}`);
      console.log(`  WMS base path: ${new URL(sample.url).pathname}`);
    }
  }
}

main().catch(console.error);
