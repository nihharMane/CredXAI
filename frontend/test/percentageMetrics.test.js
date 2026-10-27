import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateBillPaymentPercentage, calculateOverdraftPercentage } from '../src/utils/percentageMetrics.js';

test('bill payment percentage is rounded to two decimals for the API contract', () => {
  assert.equal(calculateBillPaymentPercentage(2, 3), 66.67);
  assert.equal(calculateBillPaymentPercentage(0, 3), 0);
  assert.equal(calculateBillPaymentPercentage(3, 3), 100);
});

test('bill payment percentage rejects missing or invalid counts instead of substituting zero', () => {
  assert.equal(calculateBillPaymentPercentage('', 3), null);
  assert.equal(calculateBillPaymentPercentage(2, ''), null);
  assert.equal(calculateBillPaymentPercentage(4, 3), null);
  assert.equal(calculateBillPaymentPercentage(1.5, 3), null);
  assert.equal(calculateBillPaymentPercentage(0, 0), null);
});

test('overdraft percentage uses matching two-decimal precision', () => {
  assert.equal(calculateOverdraftPercentage(1), 8.33);
  assert.equal(calculateOverdraftPercentage(0), 0);
  assert.equal(calculateOverdraftPercentage(12), 100);
  assert.equal(calculateOverdraftPercentage('', 12), null);
});
