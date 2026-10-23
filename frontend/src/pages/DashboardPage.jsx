import React, { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import predictionService from '../services/predictionService';
import { downloadAssessmentPdf } from '../utils/assessmentPdf';
import { logger } from '../utils/logger';
import { calculateBillPaymentPercentage, calculateOverdraftPercentage } from '../utils/percentageMetrics';
import {
  Activity, AlertCircle, ArrowRight, Clock3, Download,
  FileText, History, LoaderCircle, ShieldCheck,
  TrendingDown, TrendingUp
} from 'lucide-react';

const initialForm = {
  loan_amount: '', purpose: '', existing_monthly_debt: '0', repayment_history: 'UNKNOWN',
  age: '', children: '0', family_members: '2', income_type: 'Working', monthly_income: '',
  monthly_installment: '', goods_price: '', owns_car: 'N', owns_property: 'N',
  education: 'Secondary / secondary special', housing_type: 'House / apartment',
  age_range: '26-35', account_tenure_months: '', monthly_spending: '', average_balance: '',
  overdraft_months_with_overdraft: '', bill_paid_on_time_count: '', bill_total_count: '', cashflow_stability_percent: '',
};

const fieldHints = {
  loan_amount: 'Enter the total amount you are requesting in Indian rupees (₹). Example: ₹5,00,000.',
  purpose: 'In a few words, say what you plan to use the loan for. Example: education, home repairs, or business.',
  existing_monthly_debt: 'Enter the total you currently pay each month toward other loans or credit, in ₹ per month. Enter 0 if you have none; do not include this new loan.',
  repayment_history: 'Choose the option that best matches your recent payment record. Select “Not provided / unknown” if you are unsure.',
  age: 'Enter your age in completed years. Example: enter 32 for someone who is 32 years old.',
  children: 'Enter the number of children in your household. Use a whole number, including 0 if none.',
  family_members: 'Enter the number of people in your household, including you. Use a whole number.',
  income_type: 'Choose the option that best describes your main source of income or work.',
  education: 'Choose the highest education level that best describes you.',
  housing_type: 'Choose the option that best describes where you currently live.',
  monthly_income: 'Enter the total income you receive in one month, in Indian rupees (₹). Example: ₹50,000.',
  monthly_installment: 'Enter the proposed payment for this loan in Indian rupees (₹) per month. Use the lender’s quote or estimate.',
  goods_price: 'Enter the price of the item or purchase being financed, in Indian rupees (₹). Example: ₹2,00,000.',
  owns_car: 'Choose Yes if you own a car, otherwise choose No.',
  owns_property: 'Choose Yes if you or your household own property, otherwise choose No.',
  age_range: 'Choose the age range that includes your current age.',
  account_tenure_months: 'Enter how many months you have held this bank or financial account. Example: 24 for two years.',
  monthly_spending: 'Enter your total usual spending in one month, including food, bills, travel and other expenses, in Indian rupees (₹). Example: ₹25,000.',
  average_balance: 'Enter the average amount remaining in your bank account during a month, in Indian rupees (₹). Estimate it from your bank statements. Example: ₹15,000. A negative value is allowed if your average balance was below zero.',
  overdraft_months_with_overdraft: 'Enter how many months in the last 12 months you used an overdraft or had one recorded by your bank. Example: 3 months out of 12 = 25%. The percentage is rounded to two decimal places.',
  bill_paid_on_time_count: 'Enter the number of bills you paid on or before their due dates during the last 12 months. Example: enter 10 if 10 bills were on time.',
  bill_total_count: 'Enter the total bills you had due during the last 12 months. The percentage is on-time bills divided by total bills, rounded to two decimal places. At least one bill is needed to calculate it.',
  cashflow_stability_percent: 'This describes how regularly money comes into your account and how stable your balance remains. Do not guess a percentage. The training pipeline uses the supplied profile’s cashflow_stability_score directly; this project does not document the data provider’s calculation. Enter only a verified score from your profile (0–100). If you do not have one, choose the Traditional model.',
};

const money = (value, digits = 0) => value == null || !Number.isFinite(Number(value))
  ? '—'
  : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: digits }).format(Number(value));

const timestamp = (value) => value ? new Date(value).toLocaleString() : '—';

const Field = ({ label, value, onChange, error, type = 'number', min, max, step, required = true, options, hint, maxLength }) => (
  <label className="block text-xs font-semibold text-slate-700">
    <span>{label}{required && <span className="ml-1 text-rose-600">*</span>}</span>
    {options ? (
      <select required={required} value={value} onChange={(event) => onChange(event.target.value)} className={`mt-1.5 w-full rounded-xl border bg-white px-3 py-2.5 text-sm font-normal text-slate-900 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-100 ${error ? 'border-rose-400' : 'border-slate-200'}`}>
        {options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
    ) : (
      <input required={required} type={type} min={min} max={max} step={step} maxLength={maxLength} value={value} onChange={(event) => onChange(event.target.value)} className={`mt-1.5 w-full rounded-xl border bg-white px-3 py-2.5 text-sm font-normal text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-2 focus:ring-violet-100 ${error ? 'border-rose-400' : 'border-slate-200'}`} />
    )}
    {hint && <span className="mt-1 block text-[11px] font-normal leading-4 text-slate-500">{hint}</span>}
    {error && <span className="mt-1 block text-[11px] font-medium text-rose-600">{error}</span>}
  </label>
);

const SectionTitle = ({ number, children }) => (
  <div className="flex items-center gap-2 border-b border-slate-100 pb-2 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500">
    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-violet-100 text-[10px] text-violet-700">{number}</span>{children}
  </div>
);

const Factors = ({ title, items, positive }) => {
  const Icon = positive ? TrendingUp : TrendingDown;
  return (
    <section className="space-y-2.5">
      <h3 className="flex items-center gap-2 text-xs font-bold text-slate-800"><Icon className={`h-4 w-4 ${positive ? 'text-rose-600' : 'text-emerald-600'}`} />{title}</h3>
      {items.length ? items.slice(0, 4).map((factor, index) => {
        const contribution = Number(factor.contribution);
        return <div key={`${factor.feature}-${index}`} className="flex items-start justify-between gap-2 rounded-lg bg-slate-50 px-3 py-2 text-xs">
          <span className="min-w-0 break-words text-slate-700">{factor.feature || 'Model feature'}</span>
          <span className={`shrink-0 font-mono font-semibold ${positive ? 'text-rose-700' : 'text-emerald-700'}`}>{Number.isFinite(contribution) ? `${contribution > 0 ? '+' : ''}${contribution.toFixed(4)}` : '—'}</span>
        </div>;
      }) : <p className="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">No factors of this type were returned by the model.</p>}
    </section>
  );
};

const DashboardPage = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [model, setModel] = useState(() => searchParams.get('model') === 'alternative' ? 'alternative' : 'traditional');
  const [form, setForm] = useState(initialForm);
  const [fieldErrors, setFieldErrors] = useState({});
  const [prediction, setPrediction] = useState(null);
  const [savedApplication, setSavedApplication] = useState(null);
  const [applications, setApplications] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [formError, setFormError] = useState('');
  const [historyError, setHistoryError] = useState('');
  const [reportError, setReportError] = useState('');
  const [downloading, setDownloading] = useState(false);

  const refreshHistory = async () => {
    setHistoryError('');
    try {
      const records = await predictionService.getHistory();
      const items = Array.isArray(records) ? records : [];
      setApplications(items);
      logger.info('applications.history.loaded', { count: items.length });
    } catch (error) {
      logger.errorOnce(error, 'applications.history.failed', { operation: 'load' });
      setHistoryError(error.response?.data?.message || error.message || 'Application history is unavailable.');
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => { refreshHistory(); }, []);

  const setValue = (name, value) => {
    setForm((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => ({ ...current, [name]: '' }));
  };

  const requiredFields = useMemo(() => model === 'traditional'
    ? ['loan_amount', 'purpose', 'existing_monthly_debt', 'age', 'children', 'family_members', 'income_type', 'monthly_income', 'monthly_installment', 'goods_price', 'owns_car', 'owns_property', 'education', 'housing_type']
    : ['loan_amount', 'purpose', 'existing_monthly_debt', 'age_range', 'account_tenure_months', 'monthly_income', 'monthly_spending', 'average_balance', 'overdraft_months_with_overdraft', 'bill_paid_on_time_count', 'bill_total_count', 'cashflow_stability_percent'], [model]);

  const validate = () => {
    const nextErrors = {};
    requiredFields.forEach((name) => {
      if (String(form[name] ?? '').trim() === '') nextErrors[name] = 'This field is required.';
    });
    const ranges = {
      loan_amount: [0.01, 9999999999999.99], existing_monthly_debt: [0, 9999999999999.99],
      age: [18, 100], children: [0, 20], family_members: [1, 20], monthly_income: [0.01, 1000000000],
      monthly_installment: [0.01, 1000000000], goods_price: [0.01, 1000000000], account_tenure_months: [0, 600],
      monthly_spending: [0, 1000000000], average_balance: [-1000000000, 1000000000],
      overdraft_months_with_overdraft: [0, 12], bill_paid_on_time_count: [0, 1000000],
      bill_total_count: [0, 1000000], cashflow_stability_percent: [0, 100],
    };
    requiredFields.forEach((name) => {
      if (!(name in ranges) || !String(form[name] ?? '').trim()) return;
      const value = Number(form[name]);
      const [min, max] = ranges[name];
      if (!Number.isFinite(value) || value < min || value > max) nextErrors[name] = `Enter a value from ${min} to ${max}.`;
      else if (['age', 'children', 'family_members', 'account_tenure_months', 'overdraft_months_with_overdraft', 'bill_paid_on_time_count', 'bill_total_count'].includes(name) && !Number.isInteger(value)) nextErrors[name] = 'Enter a whole number.';
      else if (['loan_amount', 'existing_monthly_debt'].includes(name) && Math.abs(Math.round(value * 100) - value * 100) > 1e-7) nextErrors[name] = 'Use no more than two decimal places.';
    });
    if (model === 'alternative') {
      const paid = Number(form.bill_paid_on_time_count);
      const total = Number(form.bill_total_count);
      if (Number.isFinite(total) && total === 0) nextErrors.bill_total_count = 'At least one bill is required to calculate a percentage.';
      if (Number.isFinite(paid) && Number.isFinite(total) && paid > total) nextErrors.bill_paid_on_time_count = 'This cannot be greater than the total number of bills.';
      if (Number.isFinite(Number(form.overdraft_months_with_overdraft)) && Number(form.overdraft_months_with_overdraft) > 12) {
        nextErrors.overdraft_months_with_overdraft = 'Enter a number from 0 to 12 months.';
      }
    }
    if (form.purpose.trim().length > 120) nextErrors.purpose = 'Use 120 characters or fewer.';
    setFieldErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError('');
    setReportError('');
    if (submitting || !validate()) return;
    if (!user) {
      setFormError('Your sign-in session could not be verified. Please sign in again.');
      return;
    }

    const numeric = (key) => Number(form[key]);
    const overdraftPercent = calculateOverdraftPercentage(form.overdraft_months_with_overdraft);
    const billPaymentPercent = calculateBillPaymentPercentage(form.bill_paid_on_time_count, form.bill_total_count);
    const common = {
      existing_monthly_debt: numeric('existing_monthly_debt'),
      repayment_history: form.repayment_history,
      purpose: form.purpose.trim(),
    };
    const payload = model === 'traditional' ? {
      ...common,
      age: Math.trunc(numeric('age')),
      children: Math.trunc(numeric('children')),
      family_members: Math.trunc(numeric('family_members')),
      income_type: form.income_type,
      monthly_income: numeric('monthly_income'),
      credit_amount: numeric('loan_amount'),
      monthly_installment: numeric('monthly_installment'),
      goods_price: numeric('goods_price'),
      owns_car: form.owns_car,
      owns_property: form.owns_property,
      education: form.education,
      housing_type: form.housing_type,
    } : {
      ...common,
      age_range: form.age_range,
      account_tenure_months: Math.trunc(numeric('account_tenure_months')),
      monthly_income: numeric('monthly_income'),
      monthly_spending: numeric('monthly_spending'),
      average_balance: numeric('average_balance'),
      overdraft_frequency_percent: overdraftPercent,
      bill_payment_consistency_percent: billPaymentPercent,
      cashflow_stability_percent: numeric('cashflow_stability_percent'),
      loan_amount: numeric('loan_amount'),
    };

    setSubmitting(true);
    logger.info('assessment.submission.started', { model });
    setPrediction(null);
    setSavedApplication(null);
    try {
      const result = model === 'traditional'
        ? await predictionService.predictTraditional(payload)
        : await predictionService.predictAlternative(payload);
      setPrediction(result);
      logger.info('assessment.submission.succeeded', {
        model,
        applicationId: Number.isFinite(Number(result.application_id)) ? Number(result.application_id) : undefined,
      });
      if (result.application_id) {
        try {
          const record = await predictionService.getApplication(result.application_id);
          setSavedApplication(record);
        } catch {
          setReportError('Assessment completed, but the saved report details could not be reloaded. Open application history to try again.');
        }
      } else {
        setReportError('The service returned a result without a saved application ID, so a report cannot be downloaded.');
      }
      await refreshHistory();
    } catch (error) {
      logger.errorOnce(error, 'assessment.submission.failed', { model });
      setFormError(error.response?.data?.message || error.response?.data?.error || error.message || 'The assessment could not be completed. Check the backend and model service, then try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const probability = prediction?.default_probability_percent != null
    ? Number(prediction.default_probability_percent)
    : prediction?.default_probability != null ? Number(prediction.default_probability) * 100 : null;
  const probabilityValid = probability != null && Number.isFinite(probability) && probability >= 0 && probability <= 100;
  const increasingFactors = Array.isArray(prediction?.risk_increasing_factors) ? prediction.risk_increasing_factors : [];
  const reducingFactors = Array.isArray(prediction?.risk_reducing_factors) ? prediction.risk_reducing_factors : [];
  const explanations = Array.isArray(prediction?.explanation) ? prediction.explanation : (typeof prediction?.explanation === 'string' ? [prediction.explanation] : []);

  const downloadCurrentReport = () => {
    setReportError('');
    setDownloading(true);
    try {
      downloadAssessmentPdf(savedApplication);
      logger.info('assessment.pdf.downloaded', { applicationId: savedApplication?.id });
    } catch (error) {
      logger.errorOnce(error, 'assessment.pdf.download_failed', { applicationId: savedApplication?.id });
      setReportError(error.message || 'Unable to generate the PDF report.');
    }
    finally { setDownloading(false); }
  };

  const numberField = (key, label, min, max, step = 'any', hint) => (
    <Field label={label} value={form[key]} onChange={(value) => setValue(key, value)} error={fieldErrors[key]} min={min} max={max} step={step} hint={hint || fieldHints[key]} />
  );
  const selectField = (key, label, options, hint) => (
    <Field label={label} value={form[key]} onChange={(value) => setValue(key, value)} error={fieldErrors[key]} options={options.map((option) => typeof option === 'string' ? ({ value: option, label: option }) : option)} hint={hint || fieldHints[key]} />
  );

  return (
    <div className="mx-auto max-w-[1800px] space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-violet-300">Applicant workspace</div>
          <h1 className="mt-1 text-2xl font-extrabold text-white sm:text-3xl">Credit risk assessment</h1>
          <p className="mt-1 text-sm text-slate-400">Complete your application to receive a model-based risk assessment.</p>
        </div>
        <Link to="/history" className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-slate-200 hover:border-violet-400"><History className="h-4 w-4" />My application history</Link>
      </header>

      <div className="grid items-start gap-4 xl:grid-cols-[minmax(300px,1.05fr)_minmax(280px,0.95fr)_minmax(270px,0.82fr)] 2xl:gap-5">
        <section className="rounded-2xl border border-slate-200 bg-white p-4 text-slate-900 shadow-xl sm:p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div><h2 className="text-base font-bold text-slate-900">Loan application</h2><p className="mt-1 text-xs text-slate-500">Fields marked * are required.</p></div>
            <FileText className="h-5 w-5 text-violet-600" />
          </div>
          <div className="mb-4 grid grid-cols-2 gap-1 rounded-xl bg-slate-100 p-1">
            <button type="button" onClick={() => { setModel('traditional'); setFieldErrors({}); setFormError(''); }} className={`rounded-lg px-2 py-2 text-xs font-semibold transition ${model === 'traditional' ? 'bg-white text-violet-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>Traditional</button>
            <button type="button" onClick={() => { setModel('alternative'); setFieldErrors({}); setFormError(''); }} className={`rounded-lg px-2 py-2 text-xs font-semibold transition ${model === 'alternative' ? 'bg-white text-violet-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>Alternative data</button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {formError && <div role="alert" className="flex gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs leading-5 text-rose-700"><AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />{formError}</div>}

            <section className="space-y-3">
              <SectionTitle number="1">Loan details</SectionTitle>
              <Field type="number" min="0.01" max="9999999999999.99" step="0.01" label="Requested loan amount (₹)" value={form.loan_amount} onChange={(value) => setValue('loan_amount', value)} error={fieldErrors.loan_amount} hint={fieldHints.loan_amount} />
              <Field type="text" maxLength="120" label="Purpose of loan" value={form.purpose} onChange={(value) => setValue('purpose', value)} error={fieldErrors.purpose} hint={fieldHints.purpose} />
              <Field type="number" min="0" max="9999999999999.99" step="0.01" label="Existing monthly debt (₹ per month)" value={form.existing_monthly_debt} onChange={(value) => setValue('existing_monthly_debt', value)} error={fieldErrors.existing_monthly_debt} hint={fieldHints.existing_monthly_debt} />
              {selectField('repayment_history', 'Self-reported repayment history', [
                { value: 'UNKNOWN', label: 'Not provided / unknown' }, { value: 'CURRENT', label: 'Payments current' },
                { value: 'LATE_1_30', label: 'Late by 1–30 days' }, { value: 'LATE_31_90', label: 'Late by 31–90 days' },
                { value: 'LATE_OVER_90', label: 'Late by more than 90 days' },
              ], fieldHints.repayment_history)}
            </section>

            {model === 'traditional' ? (
              <>
                <section className="space-y-3"><SectionTitle number="2">Applicant profile</SectionTitle>
                  {numberField('age', 'Age (years)', '18', '100', '1')}
                  <div className="grid grid-cols-2 gap-3">{numberField('children', 'Children', '0', '20', '1')}{numberField('family_members', 'Family members', '1', '20', '1')}</div>
                  {selectField('income_type', 'Main source of income or work', ['Working', 'Commercial associate', 'Pensioner', 'State servant', 'Businessman', 'Student', 'Unemployed', 'Maternity leave'])}
                  {selectField('education', 'Education', ['Secondary / secondary special', 'Higher education', 'Incomplete higher', 'Lower secondary', 'Academic degree'])}
                  {selectField('housing_type', 'Housing type', ['House / apartment', 'With parents', 'Municipal apartment', 'Rented apartment', 'Office apartment', 'Co-op apartment'])}
                </section>
                <section className="space-y-3"><SectionTitle number="3">Income and assets</SectionTitle>
                  {numberField('monthly_income', 'Monthly income (₹)', '0.01', '1000000000', '0.01')}
                  {numberField('monthly_installment', 'Proposed monthly installment (₹ per month)', '0.01', '1000000000', '0.01')}
                  {numberField('goods_price', 'Purchase or goods price (₹)', '0.01', '1000000000', '0.01')}
                  <div className="grid grid-cols-2 gap-3">{selectField('owns_car', 'Owns a car', [{ value: 'N', label: 'No' }, { value: 'Y', label: 'Yes' }])}{selectField('owns_property', 'Owns property', [{ value: 'N', label: 'No' }, { value: 'Y', label: 'Yes' }])}</div>
                </section>
              </>
            ) : (
              <>
                <section className="space-y-3"><SectionTitle number="2">Account profile</SectionTitle>
                  {selectField('age_range', 'Age range', ['18-25', '26-35', '36-45', '46-55', '55+'])}
                  {numberField('account_tenure_months', 'Account tenure (months)', '0', '600', '1')}
                </section>
                <section className="space-y-3"><SectionTitle number="3">Cashflow and behavior</SectionTitle>
                  {numberField('monthly_income', 'Monthly income (₹)', '0.01', '1000000000', '0.01')}
                  {numberField('monthly_spending', 'Monthly spending (₹)', '0', '1000000000', '0.01')}
                  {numberField('average_balance', 'Average monthly balance (₹)', '-1000000000', '1000000000', '0.01')}
                  {numberField('overdraft_months_with_overdraft', 'Months with overdraft (out of 12)', '0', '12', '1')}
                  <p className="-mt-2 rounded-lg bg-violet-50 px-3 py-2 text-xs font-semibold text-violet-800">Calculated overdraft frequency (0–100%, sent to two decimals): {calculateOverdraftPercentage(form.overdraft_months_with_overdraft)?.toFixed(2) ?? '—'}%</p>
                  {numberField('bill_paid_on_time_count', 'Bills paid on time (last 12 months)', '0', '1000000', '1')}
                  {numberField('bill_total_count', 'Total bills due (last 12 months)', '0', '1000000', '1')}
                  <p className="-mt-2 rounded-lg bg-violet-50 px-3 py-2 text-xs font-semibold text-violet-800">Calculated bill payment consistency (0–100%, sent to two decimals): {calculateBillPaymentPercentage(form.bill_paid_on_time_count, form.bill_total_count)?.toFixed(2) ?? '—'}%</p>
                  {numberField('cashflow_stability_percent', 'Verified cashflow stability score (%)', '0', '100', '0.1')}
                </section>
              </>
            )}

            <p className="rounded-lg bg-violet-50 px-3 py-2 text-[11px] leading-4 text-violet-800">Loan purpose, requested amount, existing debt, and repayment history are saved with your application. Model inputs follow the selected model's supported fields.</p>
            <button type="submit" disabled={submitting} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-700 to-indigo-700 px-4 py-3 text-sm font-bold text-white shadow-md transition hover:from-violet-600 hover:to-indigo-600 disabled:cursor-not-allowed disabled:opacity-60">
              {submitting ? <><LoaderCircle className="h-4 w-4 animate-spin" />Assessing application…</> : <><Activity className="h-4 w-4" />Submit application</>}
            </button>
          </form>
        </section>

        <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4 text-slate-900 shadow-xl sm:p-5" aria-live="polite">
          <header className="flex items-start justify-between gap-3"><div><p className="text-[11px] font-bold uppercase tracking-[0.14em] text-violet-700">Model response</p><h2 className="mt-1 text-base font-bold text-slate-900">Risk overview</h2></div><div className="rounded-xl bg-violet-100 p-2 text-violet-700"><Activity className="h-5 w-5" /></div></header>

          {submitting ? (
            <div className="flex min-h-48 flex-col items-center justify-center gap-3 rounded-xl bg-slate-50 text-center"><LoaderCircle className="h-8 w-8 animate-spin text-violet-600" /><p className="text-sm font-semibold text-slate-800">Sending your application securely</p><p className="max-w-xs text-xs text-slate-500">Waiting for the selected model to return an assessment.</p></div>
          ) : prediction && probabilityValid ? (
            <>
              <div className="rounded-xl bg-slate-50 px-3 pb-3 pt-5 text-center">
                <div className="relative mx-auto h-36 w-full max-w-[250px]">
                  <svg viewBox="0 0 200 125" className="h-full w-full" role="img" aria-label={`Estimated adverse-outcome probability ${probability.toFixed(2)} percent`}>
                    <path d="M 20 112 A 80 80 0 0 1 180 112" fill="none" stroke="#e2e8f0" strokeWidth="16" strokeLinecap="round" pathLength="100" />
                    <path d="M 20 112 A 80 80 0 0 1 180 112" fill="none" stroke="url(#riskGradient)" strokeWidth="16" strokeLinecap="round" pathLength="100" strokeDasharray={`${Math.max(0, Math.min(probability, 100))} 100`} />
                    <defs><linearGradient id="riskGradient"><stop offset="0%" stopColor="#8b5cf6" /><stop offset="100%" stopColor="#4338ca" /></linearGradient></defs>
                  </svg>
                  <div className="absolute inset-x-0 bottom-0"><div className="text-3xl font-extrabold tracking-tight text-slate-900">{probability.toFixed(2)}%</div><div className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-slate-500">Adverse-outcome estimate</div></div>
                </div>
                <div className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-violet-100 px-3 py-1 text-xs font-bold uppercase text-violet-800">{prediction.risk_band?.replaceAll('_', ' ') || 'Category not returned'}</div>
                <p className="mt-2 text-xs leading-5 text-slate-500">This is the probability returned by the selected model, not a lending decision.</p>
              </div>

              <section className="space-y-2"><h3 className="text-sm font-bold text-slate-900">AI analysis</h3>
                {explanations.length ? explanations.map((item, index) => <p key={`${index}-${item}`} className="rounded-lg border border-slate-100 bg-white p-3 text-xs leading-5 text-slate-700">{item}</p>) : <p className="rounded-lg bg-amber-50 p-3 text-xs leading-5 text-amber-800">The saved model response did not include a natural-language explanation.</p>}
                {prediction.disclaimer && <p className="text-[11px] leading-4 text-slate-500">{prediction.disclaimer}</p>}
              </section>

              <div className="space-y-3"><Factors title="Key risk-increasing factors" items={increasingFactors} positive /><Factors title="Key risk-reducing factors" items={reducingFactors} positive={false} /></div>
              <p className="text-[10px] leading-4 text-slate-500">Signed values are contributions to the model score, not percentage-point changes or causal effects.</p>
            </>
          ) : prediction ? (
            <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-800">The model returned an invalid or missing probability. No score has been substituted.</div>
          ) : (
            <div className="flex min-h-64 flex-col items-center justify-center rounded-xl bg-slate-50 px-5 text-center"><div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-700"><Activity className="h-7 w-7" /></div><h3 className="mt-4 font-bold text-slate-800">Your assessment will appear here</h3><p className="mt-2 max-w-xs text-xs leading-5 text-slate-500">Complete the loan application and submit it to view the model's returned probability, risk category, and explanation.</p></div>
          )}
        </section>

        <aside className="space-y-4">
          <section className="rounded-2xl border border-slate-200 bg-white p-4 text-slate-900 shadow-xl sm:p-5">
            <div className="flex items-start gap-3"><div className="rounded-xl bg-indigo-100 p-2 text-indigo-700"><ShieldCheck className="h-5 w-5" /></div><div><p className="text-[11px] font-bold uppercase tracking-[0.14em] text-indigo-700">Saved application</p><h2 className="mt-1 text-base font-bold text-slate-900">Risk assessment summary</h2></div></div>
            {prediction ? (
              <div className="mt-4 space-y-3 text-xs">
                <div className="flex justify-between gap-3 border-b border-slate-100 pb-2"><span className="text-slate-500">Application ID</span><strong className="text-slate-900">{prediction.application_id ? `#${prediction.application_id}` : 'Not saved'}</strong></div>
                <div className="flex justify-between gap-3 border-b border-slate-100 pb-2"><span className="text-slate-500">Category</span><strong className="text-slate-900">{prediction.risk_band?.replaceAll('_', ' ') || 'Not returned'}</strong></div>
                <div className="flex justify-between gap-3 border-b border-slate-100 pb-2"><span className="text-slate-500">Model used</span><strong className="max-w-[60%] break-words text-right text-slate-900">{prediction.model_type === 'ALTERNATIVE_DATA' ? 'Alternative data' : prediction.model_type === 'TRADITIONAL_DATA' ? 'Traditional' : prediction.model_type || 'Not returned'}</strong></div>
                <div className="flex justify-between gap-3 border-b border-slate-100 pb-2"><span className="text-slate-500">Requested amount</span><strong className="text-slate-900">{money(prediction.requested_loan_amount, 2)}</strong></div>
                <div className="flex justify-between gap-3 border-b border-slate-100 pb-2"><span className="text-slate-500">Model version</span><strong className="max-w-[60%] break-all text-right font-mono text-[10px] text-slate-700">{prediction.model_version || 'Unversioned'}</strong></div>
                <div className="flex justify-between gap-3"><span className="text-slate-500">Assessment time</span><strong className="text-right text-slate-900">{timestamp(prediction.assessment_timestamp)}</strong></div>
                {reportError && <p role="alert" className="rounded-lg bg-rose-50 p-2.5 text-[11px] leading-4 text-rose-700">{reportError}</p>}
                <button type="button" onClick={downloadCurrentReport} disabled={!savedApplication || downloading} className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-700 px-3 py-2.5 text-xs font-bold text-white transition hover:bg-violet-600 disabled:cursor-not-allowed disabled:opacity-50"><Download className="h-4 w-4" />{downloading ? 'Preparing report…' : 'Download PDF report'}</button>
                {!savedApplication && !reportError && <p className="text-[10px] leading-4 text-slate-500">Loading the saved report record…</p>}
              </div>
            ) : <p className="mt-4 text-xs leading-5 text-slate-500">The summary and report download become available after your application is assessed and saved.</p>}
          </section>

          {prediction && <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4 text-slate-900 shadow-xl sm:p-5">
            <h2 className="text-sm font-bold text-slate-900">Contributing factors</h2>
            <Factors title="Risk-increasing" items={increasingFactors} positive />
            <Factors title="Risk-reducing" items={reducingFactors} positive={false} />
          </section>}

          <section className="rounded-2xl border border-slate-200 bg-white p-4 text-slate-900 shadow-xl sm:p-5">
            <div className="flex items-center justify-between gap-2"><h2 className="flex items-center gap-2 text-sm font-bold text-slate-900"><History className="h-4 w-4 text-violet-700" />Application history</h2><Link to="/history" className="text-[11px] font-semibold text-violet-700 hover:text-violet-900">View all</Link></div>
            {historyLoading ? <div className="flex items-center gap-2 py-5 text-xs text-slate-500"><LoaderCircle className="h-4 w-4 animate-spin" />Loading history…</div> : historyError ? <p role="alert" className="mt-3 flex gap-2 rounded-lg bg-rose-50 p-3 text-xs leading-5 text-rose-700"><AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />{historyError}</p> : applications.length ? (
              <div className="mt-3 divide-y divide-slate-100">
                {applications.slice(0, 4).map((application) => <Link key={application.id} to={`/history/${application.id}`} className="block py-3 first:pt-1 last:pb-0">
                  <div className="flex items-center justify-between gap-2"><span className="text-xs font-semibold text-slate-800">Application #{application.id}</span><span className="text-[10px] font-medium text-slate-500">{application.status || 'Saved'}</span></div>
                  <div className="mt-1 flex items-center justify-between gap-2 text-[11px] text-slate-500"><span className="truncate">{application.purpose || 'Loan application'} · {money(application.loanAmount)}</span><ArrowRight className="h-3.5 w-3.5 shrink-0 text-violet-600" /></div>
                </Link>)}
              </div>
            ) : <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-5 text-slate-500">No saved applications yet.</p>}
          </section>

          <p className="px-1 text-[10px] leading-4 text-slate-400">Model estimates and risk categories are not lending decisions or guarantees.</p>
        </aside>
      </div>
    </div>
  );
};

export default DashboardPage;
