import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Activity, AlertCircle, ArrowLeft, ArrowRight, Check, FileText, LoaderCircle, ShieldCheck } from 'lucide-react';
import predictionService from '../services/predictionService';
import { logger } from '../utils/logger';
import { calculateBillPaymentPercentage, calculateOverdraftPercentage } from '../utils/percentageMetrics';

const initialForm = {
  loan_amount: '', purpose: '', existing_monthly_debt: '0', repayment_history: 'UNKNOWN',
  age: '', children: '0', family_members: '2', income_type: 'Working', monthly_income: '',
  monthly_installment: '', goods_price: '', owns_car: 'N', owns_property: 'N',
  education: 'Secondary / secondary special', housing_type: 'House / apartment',
  age_range: '26-35', account_tenure_months: '', monthly_spending: '', average_balance: '',
  overdraft_months_with_overdraft: '', bill_paid_on_time_count: '', bill_total_count: '', cashflow_stability_percent: '',
};
const repaymentOptions = [
  { value: 'UNKNOWN', label: 'Not provided / unknown' }, { value: 'CURRENT', label: 'Payments current' },
  { value: 'LATE_1_30', label: 'Late by 1–30 days' }, { value: 'LATE_31_90', label: 'Late by 31–90 days' },
  { value: 'LATE_OVER_90', label: 'Late by more than 90 days' },
];
const hints = {
  loan_amount: 'Enter the amount requested in Indian rupees. Example: ₹5,00,000.',
  purpose: 'Example: education, home repairs, or business (120 characters maximum).',
  existing_monthly_debt: 'Monthly payments toward other loans or credit. Enter 0 if you have none.',
  repayment_history: 'Choose the option that best matches your recent payment record.',
  age: 'Age in completed years.', children: 'Use 0 if there are no children.', family_members: 'Include yourself in the household count.',
  income_type: 'Choose the option that best describes your main source of income or work.',
  owns_car: 'Choose Yes if you own a car, otherwise choose No.', owns_property: 'Choose Yes if you or your household own property.',
  education: 'Choose the highest education level that best describes you.', housing_type: 'Choose the option that best describes where you currently live.',
  age_range: 'Choose the range that includes your current age.',
  monthly_income: 'Your usual income in one month, in ₹.', monthly_installment: 'Proposed monthly payment for this loan, in ₹.',
  goods_price: 'Price of the item or purchase being financed, in ₹.',
  account_tenure_months: 'How many months you have held this financial account.',
  monthly_spending: 'Usual monthly spending, in ₹.', average_balance: 'Average monthly account balance, in ₹. A negative amount is allowed.',
  overdraft_months_with_overdraft: 'Months out of the last 12 in which an overdraft was used. Example: 3 months becomes 25%.',
  bill_paid_on_time_count: 'Number of bills paid on or before their due dates in the last 12 months.',
  bill_total_count: 'Total bills due in the last 12 months. At least one is needed to calculate a percentage.',
  cashflow_stability_percent: 'Enter only a verified score from 0 to 100. If you do not have one, select Traditional.',
};
const ranges = {
  loan_amount: [0.01, 9999999999999.99], existing_monthly_debt: [0, 9999999999999.99], age: [18, 100], children: [0, 20],
  family_members: [1, 20], monthly_income: [0.01, 1000000000], monthly_installment: [0.01, 1000000000], goods_price: [0.01, 1000000000],
  account_tenure_months: [0, 600], monthly_spending: [0, 1000000000], average_balance: [-1000000000, 1000000000],
  overdraft_months_with_overdraft: [0, 12], bill_paid_on_time_count: [0, 1000000], bill_total_count: [0, 1000000], cashflow_stability_percent: [0, 100],
};
const whole = new Set(['age', 'children', 'family_members', 'account_tenure_months', 'overdraft_months_with_overdraft', 'bill_paid_on_time_count', 'bill_total_count']);
const money = (value) => value === '' ? '' : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(value));

function Field({ name, label, value, onChange, errors, options, type = 'number', min, max, step = 'any', required = true }) {
  const id = `field-${name}`;
  return <label htmlFor={id} className="block text-sm font-semibold text-slate-800">
    {label}{required && <span className="ml-1 text-rose-600" aria-label="required">*</span>}
    {options ? <select id={id} value={value} onChange={e => onChange(name, e.target.value)} aria-invalid={!!errors[name]} aria-describedby={`${id}-hint ${errors[name] ? `${id}-error` : ''}`} className={`mt-2 w-full rounded-xl border bg-white px-3.5 py-3 text-sm font-normal outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-100 ${errors[name] ? 'border-rose-400' : 'border-slate-200'}`}>{options.map(o => typeof o === 'string' ? <option key={o} value={o}>{o}</option> : <option key={o.value} value={o.value}>{o.label}</option>)}</select> : <input id={id} type={type} min={min} max={max} step={step} maxLength={name === 'purpose' ? 120 : undefined} value={value} onChange={e => onChange(name, e.target.value)} aria-invalid={!!errors[name]} aria-describedby={`${id}-hint ${errors[name] ? `${id}-error` : ''}`} className={`mt-2 w-full rounded-xl border bg-white px-3.5 py-3 text-sm font-normal outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-100 ${errors[name] ? 'border-rose-400' : 'border-slate-200'}`} />}
    {hints[name] && <span id={`${id}-hint`} className="mt-1.5 block text-xs font-normal leading-5 text-slate-500">{hints[name]}</span>}
    {errors[name] && <span id={`${id}-error`} role="alert" className="mt-1 block text-xs font-medium text-rose-600">{errors[name]}</span>}
  </label>;
}

const steps = ['Loan Details', 'Financial Profile', 'Repayment History', 'Review & Submit'];
const groups = {
  loan: ['loan_amount', 'purpose', 'existing_monthly_debt'],
  traditionalLoan: ['monthly_installment', 'goods_price'],
  traditionalFinancial: ['age', 'children', 'family_members', 'income_type', 'monthly_income', 'owns_car', 'owns_property', 'education', 'housing_type'],
  alternativeFinancial: ['age_range', 'monthly_income', 'monthly_spending', 'average_balance'],
  traditionalRepayment: ['repayment_history'],
  alternativeRepayment: ['repayment_history', 'account_tenure_months', 'overdraft_months_with_overdraft', 'bill_paid_on_time_count', 'bill_total_count', 'cashflow_stability_percent'],
};

export default function DashboardPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [model, setModel] = useState(searchParams.get('model') === 'alternative' ? 'alternative' : 'traditional');
  const [form, setForm] = useState(initialForm);
  const [step, setStep] = useState(0);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [lastSavedId, setLastSavedId] = useState(null);
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => { const requested = searchParams.get('model'); if (requested === 'traditional' || requested === 'alternative') setModel(requested); }, [searchParams]);
  const setValue = (name, value) => { setForm(old => ({ ...old, [name]: value })); setErrors(old => ({ ...old, [name]: '' })); setFormError(''); };
  const fieldsForStep = (s) =>
    s === 0 ? [...groups.loan, ...(model === 'traditional' ? groups.traditionalLoan : [])]
    : s === 1 ? (model === 'traditional' ? groups.traditionalFinancial : groups.alternativeFinancial)
    : (model === 'traditional' ? groups.traditionalRepayment : groups.alternativeRepayment);
  // Returns an errors object for one step without touching React state.
  const collectErrors = (s) => {
    const fields = fieldsForStep(s);
    const next = {};
    fields.forEach(name => {
      const raw = String(form[name] ?? '').trim();
      if (!raw) { next[name] = 'This field is required.'; return; }
      if (name in ranges) {
        const value = Number(raw), [min, max] = ranges[name];
        if (!Number.isFinite(value) || value < min || value > max) next[name] = `Enter a value from ${min} to ${max}.`;
        else if (whole.has(name) && !Number.isInteger(value)) next[name] = 'Enter a whole number.';
        else if (['loan_amount', 'existing_monthly_debt'].includes(name) && Math.abs(Math.round(value * 100) - value * 100) > 1e-7) next[name] = 'Use no more than two decimal places.';
      }
    });
    if (fields.includes('purpose') && form.purpose.trim().length > 120) next.purpose = 'Use 120 characters or fewer.';
    if (model === 'alternative' && s === 2) {
      const paid = Number(form.bill_paid_on_time_count), total = Number(form.bill_total_count);
      if (Number.isFinite(total) && total === 0) next.bill_total_count = 'At least one bill is required to calculate a percentage.';
      if (Number.isFinite(paid) && Number.isFinite(total) && paid > total) next.bill_paid_on_time_count = 'This cannot be greater than the total number of bills.';
    }
    return next;
  };
  // Used by Continue: checks only the current step.
  const validateStep = () => {
    const next = collectErrors(step);
    setErrors(next);
    return Object.keys(next).length === 0;
  };
  // Used by Submit: checks all data steps and jumps to the first one with errors.
  const validateAll = () => {
    for (const s of [0, 1, 2]) {
      const next = collectErrors(s);
      if (Object.keys(next).length > 0) {
        setErrors(next);
        setStep(s);
        setFormError('Please fix the highlighted fields before submitting.');
        return false;
      }
    }
    setErrors({});
    return true;
  };
  const advance = () => { setFormError(''); if (validateStep()) setStep(s => Math.min(s + 1, 3)); };

  const submit = async () => {
    if (submitting || !validateAll()) return;
    if (!confirmed) { setFormError('Please confirm that the details are accurate.'); return; }
    setSubmitting(true); setFormError(''); setLastSavedId(null);
    const n = key => Number(form[key]);
    const common = { existing_monthly_debt: n('existing_monthly_debt'), repayment_history: form.repayment_history, purpose: form.purpose.trim() };
    const payload = model === 'traditional' ? {
      ...common, age: Math.trunc(n('age')), children: Math.trunc(n('children')), family_members: Math.trunc(n('family_members')),
      income_type: form.income_type, monthly_income: n('monthly_income'), credit_amount: n('loan_amount'),
      monthly_installment: n('monthly_installment'), goods_price: n('goods_price'), owns_car: form.owns_car,
      owns_property: form.owns_property, education: form.education, housing_type: form.housing_type,
    } : {
      ...common, age_range: form.age_range, account_tenure_months: Math.trunc(n('account_tenure_months')),
      monthly_income: n('monthly_income'), monthly_spending: n('monthly_spending'), average_balance: n('average_balance'),
      overdraft_frequency_percent: calculateOverdraftPercentage(form.overdraft_months_with_overdraft),
      bill_payment_consistency_percent: calculateBillPaymentPercentage(form.bill_paid_on_time_count, form.bill_total_count),
      cashflow_stability_percent: n('cashflow_stability_percent'), loan_amount: n('loan_amount'),
    };
    try {
      logger.info('assessment.submission.started', { model });
      const result = model === 'traditional' ? await predictionService.predictTraditional(payload) : await predictionService.predictAlternative(payload);
      if (!result?.application_id) throw new Error('The assessment response did not include a saved application ID. Check My Applications before retrying to avoid submitting twice.');
      setLastSavedId(result.application_id);
      logger.info('assessment.submission.succeeded', { model, applicationId: result.application_id });
      navigate(`/history/${result.application_id}`, { replace: true });
    } catch (error) {
      logger.errorOnce(error, 'assessment.submission.failed', { model });
      setFormError(error.response?.data?.message || error.response?.data?.error || error.message || 'The assessment could not be completed. Please try again.');
      if (lastSavedId) setFormError(`Application #${lastSavedId} was saved, but its result could not be opened. View it in My Applications.`);
    } finally { setSubmitting(false); }
  };

  const input = (name, label, min, max, options, type = 'number', stepSize = 'any') => <Field key={name} name={name} label={label} value={form[name]} onChange={setValue} errors={errors} min={min} max={max} options={options} type={type} step={stepSize} />;
  const reviewValue = key => {
    const labels = { loan_amount: 'Requested loan amount', purpose: 'Purpose of loan', existing_monthly_debt: 'Existing monthly debt', repayment_history: 'Repayment history', age: 'Age', children: 'Children', family_members: 'Family members', income_type: 'Income type', monthly_income: 'Monthly income', monthly_installment: 'Proposed installment', goods_price: 'Purchase price', owns_car: 'Owns a car', owns_property: 'Owns property', education: 'Education', housing_type: 'Housing type', age_range: 'Age range', monthly_spending: 'Monthly spending', average_balance: 'Average balance', account_tenure_months: 'Account tenure', overdraft_months_with_overdraft: 'Months with overdraft', bill_paid_on_time_count: 'Bills paid on time', bill_total_count: 'Total bills', cashflow_stability_percent: 'Cashflow stability score' };
    const val = key === 'loan_amount' || key === 'existing_monthly_debt' || ['monthly_income','monthly_installment','goods_price','monthly_spending','average_balance'].includes(key) ? money(form[key]) : key === 'repayment_history' ? repaymentOptions.find(o => o.value === form[key])?.label : form[key];
    return <div key={key} className="flex flex-col gap-1 border-b border-slate-100 py-2 last:border-0 sm:flex-row sm:justify-between"><span className="text-xs text-slate-500">{labels[key]}</span><span className="break-words text-sm font-medium text-slate-800 sm:max-w-[65%] sm:text-right">{val || '—'}</span></div>;
  };
  const section = (title, fields, targetStep) => <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6"><div className="mb-3 flex items-center justify-between"><h3 className="font-bold text-slate-900">{title}</h3><button type="button" onClick={() => setStep(targetStep)} className="rounded-lg px-3 py-1.5 text-xs font-semibold text-violet-700 hover:bg-violet-50">Edit</button></div>{fields.map(reviewValue)}</section>;

  return <div className="mx-auto max-w-6xl space-y-6">
    <header className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-violet-300">Applicant workspace</p><h1 className="mt-1 text-2xl font-extrabold text-white sm:text-3xl">Credit Risk Assessment</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Share a few details about your loan and finances. We’ll use your selected model to prepare an assessment.</p></div><Link to="/history" className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-slate-200 hover:border-violet-400"><FileText className="h-4 w-4"/>My Applications</Link></header>
    <section className="rounded-2xl border border-slate-700/80 bg-slate-900/70 p-4 sm:p-5"><div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300"><Activity className="h-4 w-4 text-violet-300"/>Choose an assessment model</div><div className="grid gap-3 md:grid-cols-2">
      {[['traditional','Traditional model','Uses established applicant, income, household, and loan details.'],['alternative','Alternative data model','Uses account cashflow, balances, bill payment, and overdraft patterns.']].map(([value,title,description])=><button type="button" key={value} aria-pressed={model===value} onClick={()=>{if(!submitting && model!==value){setModel(value);setStep(0);setErrors({});setFormError('');setConfirmed(false);}}} className={`rounded-xl border p-4 text-left transition focus:outline-none focus:ring-2 focus:ring-violet-400 ${model===value?'border-violet-400 bg-violet-500/10':'border-slate-700 bg-slate-950/40 hover:border-slate-500'}`}><span className="flex items-center justify-between font-semibold text-white">{title}{model===value&&<Check className="h-4 w-4 text-violet-300"/>}</span><span className="mt-1 block text-xs leading-5 text-slate-400">{description}</span></button>)}
    </div></section>
    <div aria-label={`Step ${step+1} of 4`} className="rounded-2xl border border-slate-700/80 bg-slate-900/70 p-4 sm:p-5"><div className="mb-3 flex items-center justify-between text-xs"><span className="font-semibold text-slate-200">Step {step+1} of 4 · {steps[step]}</span><span className="text-slate-400">{Math.round((step+1)/4*100)}% complete</span></div><div className="mb-4 h-1.5 overflow-hidden rounded-full bg-slate-700"><div className="h-full rounded-full bg-violet-500 transition-all" style={{width:`${(step+1)*25}%`}}/></div><ol className="grid grid-cols-4 gap-2">{steps.map((title,index)=><li key={title} className={`min-w-0 text-center text-[10px] sm:text-xs ${index===step?'font-bold text-violet-200':index<step?'text-slate-300':'text-slate-500'}`}><span className={`mx-auto mb-1 flex h-7 w-7 items-center justify-center rounded-full border ${index===step?'border-violet-300 bg-violet-500/20':index<step?'border-emerald-400/60 bg-emerald-500/10':'border-slate-600'}`}>{index<step?<Check className="h-3.5 w-3.5"/>:index+1}</span><span className="block truncate">{title}</span></li>)}</ol></div>
    <form className="overflow-hidden rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-xl" onSubmit={e=>e.preventDefault()} noValidate>
      <div className="border-b border-slate-100 px-5 py-5 sm:px-8"><h2 className="text-xl font-bold text-slate-900">{steps[step]}</h2><p className="mt-1 text-sm text-slate-500">{step===3?'Review the details below before sending your application.':'Fields marked with * are required.'}</p></div>
      <div className="space-y-5 px-5 py-6 sm:px-8 sm:py-8">
        {formError&&<div role="alert" className="flex gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm leading-5 text-rose-700"><AlertCircle className="mt-0.5 h-4 w-4 shrink-0"/>{formError}{lastSavedId&&<Link className="underline" to={`/history/${lastSavedId}`}>Open saved application #{lastSavedId}</Link>}</div>}
        {step===0&&<div className="grid gap-5 md:grid-cols-2">{input('loan_amount','Requested loan amount (₹)','0.01','9999999999999.99',null,'number','0.01')}{input('existing_monthly_debt','Existing monthly debt (₹ per month)','0','9999999999999.99',null,'number','0.01')}<div className="md:col-span-2">{input('purpose','Purpose of loan',null,null,null,'text')}</div>{model==='traditional'&&<>{input('monthly_installment','Proposed monthly installment (₹)','0.01','1000000000',null,'number','0.01')}{input('goods_price','Purchase or goods price (₹)','0.01','1000000000',null,'number','0.01')}</>}</div>}
        {step===1&&<div className="grid gap-5 md:grid-cols-2">{model==='traditional'?<>{input('age','Age (years)','18','100',null,'number','1')}{input('children','Children','0','20',null,'number','1')}{input('family_members','Family members','1','20',null,'number','1')}{input('income_type','Main source of income or work',null,null,['Working','Commercial associate','Pensioner','State servant','Businessman','Student','Unemployed','Maternity leave'],'text')}{input('monthly_income','Monthly income (₹)','0.01','1000000000',null,'number','0.01')}{input('owns_car','Owns a car',null,null,[{value:'N',label:'No'},{value:'Y',label:'Yes'}],'text')}{input('owns_property','Owns property',null,null,[{value:'N',label:'No'},{value:'Y',label:'Yes'}],'text')}{input('education','Education',null,null,['Secondary / secondary special','Higher education','Incomplete higher','Lower secondary','Academic degree'],'text')}{input('housing_type','Housing type',null,null,['House / apartment','With parents','Municipal apartment','Rented apartment','Office apartment','Co-op apartment'],'text')}</>:<>{input('age_range','Age range',null,null,['18-25','26-35','36-45','46-55','55+'],'text')}{input('monthly_income','Monthly income (₹)','0.01','1000000000',null,'number','0.01')}{input('monthly_spending','Monthly spending (₹)','0','1000000000',null,'number','0.01')}{input('average_balance','Average monthly balance (₹)','-1000000000','1000000000',null,'number','0.01')}</>}</div>}
        {step===2&&<div className="grid gap-5 md:grid-cols-2">{input('repayment_history','Self-reported repayment history',null,null,repaymentOptions,'text')}{model==='alternative'&&<>{input('account_tenure_months','Account tenure (months)','0','600',null,'number','1')}{input('overdraft_months_with_overdraft','Months with overdraft (out of 12)','0','12',null,'number','1')}<p className="rounded-xl bg-violet-50 p-3 text-sm text-violet-800 md:col-span-2">Calculated overdraft frequency (0–100%): <strong>{calculateOverdraftPercentage(form.overdraft_months_with_overdraft)?.toFixed(2)??'—'}%</strong></p>{input('bill_paid_on_time_count','Bills paid on time (last 12 months)','0','1000000',null,'number','1')}{input('bill_total_count','Total bills due (last 12 months)','0','1000000',null,'number','1')}<p className="rounded-xl bg-violet-50 p-3 text-sm text-violet-800 md:col-span-2">Calculated bill payment consistency (0–100%): <strong>{calculateBillPaymentPercentage(form.bill_paid_on_time_count,form.bill_total_count)?.toFixed(2)??'—'}%</strong></p>{input('cashflow_stability_percent','Verified cashflow stability score (%)','0','100',null,'number','0.01')}<p className="text-xs leading-5 text-slate-500">This percentage must come from a verified profile score. Enter a value from 0 to 100; for example, enter 90 for a verified score of 90%. Do not estimate it.</p></>}</div>}
        {step===3&&<div className="space-y-4">{section('Loan Details',model==='traditional'?[...groups.loan,...groups.traditionalLoan]:groups.loan,0)}{section('Financial Profile',model==='traditional'?groups.traditionalFinancial:groups.alternativeFinancial,1)}{section('Repayment Information',model==='traditional'?groups.traditionalRepayment:groups.alternativeRepayment,2)}<p className="flex gap-2 rounded-xl bg-slate-50 p-4 text-xs leading-5 text-slate-600"><ShieldCheck className="h-4 w-4 shrink-0 text-violet-600"/>Your details are sent securely for the selected model. CredXAI provides model-based risk estimates, not a guaranteed lending decision.</p>{model==='alternative'&&<p className="rounded-xl bg-violet-50 p-3 text-sm text-violet-800">Values sent to the model: overdraft frequency <strong>{calculateOverdraftPercentage(form.overdraft_months_with_overdraft)?.toFixed(2)??'—'}%</strong> · bill payment consistency <strong>{calculateBillPaymentPercentage(form.bill_paid_on_time_count,form.bill_total_count)?.toFixed(2)??'—'}%</strong></p>}<label className="flex items-start gap-2 text-sm text-slate-700"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)} className="mt-1"/>I confirm that the details above are accurate to the best of my knowledge.</label><p className="text-sm text-slate-600">This application will be assessed using the <strong>{model==='traditional'?'Traditional':'Alternative Data'}</strong> model.</p></div>}
      </div>
      <div className="sticky bottom-0 flex items-center justify-between gap-3 border-t border-slate-100 bg-white/95 px-5 py-4 backdrop-blur sm:px-8"><button type="button" onClick={()=>step===0?null:setStep(s=>s-1)} disabled={step===0||submitting} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"><ArrowLeft className="h-4 w-4"/>Back</button>{step<3?<button type="button" onClick={advance} disabled={submitting} className="inline-flex items-center gap-2 rounded-xl bg-violet-700 px-5 py-2.5 text-sm font-bold text-white hover:bg-violet-600 disabled:opacity-60">Continue<ArrowRight className="h-4 w-4"/></button>:<button type="button" onClick={submit} disabled={submitting||!confirmed} className="inline-flex items-center gap-2 rounded-xl bg-violet-700 px-5 py-2.5 text-sm font-bold text-white hover:bg-violet-600 disabled:cursor-not-allowed disabled:opacity-60">{submitting?<><LoaderCircle className="h-4 w-4 animate-spin"/>Assessing application…</>:<><Activity className="h-4 w-4"/>Submit Application</>}</button>}</div>
    </form>
  </div>;
}
