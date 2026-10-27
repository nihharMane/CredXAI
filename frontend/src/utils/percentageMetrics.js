export const calculateOverdraftPercentage = (monthsWithOverdraft, observedMonths = 12) => {
  if (String(monthsWithOverdraft ?? '').trim() === '') return null;
  const months = Number(monthsWithOverdraft);
  const observed = Number(observedMonths);
  if (!Number.isInteger(months) || !Number.isInteger(observed)
    || observed < 1 || observed > 12 || months < 0 || months > observed) return null;
  return Number(((months / observed) * 100).toFixed(2));
};

export const calculateBillPaymentPercentage = (paidOnTime, totalBills) => {
  if (String(paidOnTime ?? '').trim() === '' || String(totalBills ?? '').trim() === '') return null;
  const paid = Number(paidOnTime);
  const total = Number(totalBills);
  if (!Number.isInteger(paid) || !Number.isInteger(total)
    || total <= 0 || paid < 0 || paid > total) return null;
  // The model API accepts percentages to two decimal places; its preprocessing
  // divides by 100, preserving the four-decimal ratio precision used in training.
  return Number(((paid / total) * 100).toFixed(2));
};
