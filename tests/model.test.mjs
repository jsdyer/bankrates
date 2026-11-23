import test from 'node:test';
import assert from 'node:assert/strict';
import {subtractMonths} from '../web/series.mjs';
test('date range clamps month ends including leap years',()=>{assert.equal(subtractMonths('2024-03-31',1),'2024-02-29');assert.equal(subtractMonths('2023-03-31',1),'2023-02-28');});
test('monthly ranges retain month precision across a year boundary',()=>{assert.equal(subtractMonths('2026-01',2),'2025-11');});
