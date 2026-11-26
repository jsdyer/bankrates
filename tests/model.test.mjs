import test from 'node:test';
import assert from 'node:assert/strict';
import {subtractMonths,policyChanges,nextPolicyEvent} from '../web/series.mjs';
test('date range clamps month ends including leap years',()=>{assert.equal(subtractMonths('2024-03-31',1),'2024-02-29');assert.equal(subtractMonths('2023-03-31',1),'2023-02-28');});
test('monthly ranges retain month precision across a year boundary',()=>{assert.equal(subtractMonths('2026-01',2),'2025-11');});

test('observed target changes omit holds and missing points',()=>{assert.deepEqual(policyChanges(['2026-01-01','2026-01-02','2026-01-05','2026-01-06'],[2.25,null,2.25,2.5]),[{date:'2026-01-06',previousDate:'2026-01-05',before:2.25,after:2.5,points:.25}]);});
test('calendar selects explicit future date only',()=>{assert.equal(nextPolicyEvent([{date:'2026-12-09'}],'2026-12-10'),null);assert.equal(nextPolicyEvent([{date:'2027-01-27'},{date:'2026-12-09'}],'2026-11-26').date,'2026-12-09');});
