import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import predictionService from '../services/predictionService';
import RiskResultView from '../components/RiskResultView';
import { logger } from '../utils/logger';
import { 
  Sparkles, 
  User, 
  DollarSign, 
  TrendingUp, 
  Wallet, 
  Clock, 
  Percent, 
  Send, 
  AlertCircle, 
  RotateCcw,
  ArrowLeft,
  CheckCircle2,
  HelpCircle
} from 'lucide-react';

// Exact categorical age ranges verified from alternative model OneHotEncoder & preprocessing
const AGE_RANGE_OPTIONS = [
  '18-25',
  '26-35',
  '36-45',
  '46-55',
  '55+',
];

// Sensible initial form values for thin-file / alternative scoring
const INITIAL_FORM_STATE = {
  // Demographic band
  age_range: '26-35',
  // Banking behavior
  account_tenure_months: 24,
  monthly_income: 48000,
  monthly_spending: 32000,
  average_balance: 15000,
  // Stability & consistency percentages
  overdraft_frequency_percent: 5,
  bill_payment_consistency_percent: 95,
  cashflow_stability_percent: 85,
  loan_amount: 250000,
  purpose: 'PERSONAL',
  existing_monthly_debt: 0,
  repayment_history: 'UNKNOWN',
};

const AlternativeAssessmentPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState(INITIAL_FORM_STATE);
  const [fieldErrors, setFieldErrors] = useState({});
  const [apiError, setApiError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  // Field change handler
  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    if (fieldErrors[field]) {
      setFieldErrors((prev) => {
        const updated = { ...prev };
        delete updated[field];
        return updated;
      });
    }
  };

  // Validation logic matching model parameters & physical bounds
  const validateForm = () => {
    const errors = {};

    if (!formData.age_range) {
      errors.age_range = 'Age bracket is required.';
    }

    const tenureNum = Number(formData.account_tenure_months);
    if (isNaN(tenureNum) || tenureNum < 0 || tenureNum > 600) {
      errors.account_tenure_months = 'Account tenure must be between 0 and 600 months (50 years).';
    }

    const incomeNum = Number(formData.monthly_income);
    if (isNaN(incomeNum) || incomeNum <= 0) {
      errors.monthly_income = 'Monthly income must be greater than 0.';
    }

    const spendingNum = Number(formData.monthly_spending);
    if (isNaN(spendingNum) || spendingNum < 0) {
      errors.monthly_spending = 'Monthly spending cannot be negative.';
    }

    const balanceNum = Number(formData.average_balance);
    if (isNaN(balanceNum)) {
      errors.average_balance = 'Average bank balance is required.';
    }

    const overdraftValue = String(formData.overdraft_frequency_percent ?? '').trim();
    const overdraftNum = Number(overdraftValue);
    if (!overdraftValue || !Number.isFinite(overdraftNum) || overdraftNum < 0 || overdraftNum > 100) {
      errors.overdraft_frequency_percent = 'Enter overdraft frequency from 0% to 100%.';
    } else if (Math.abs(Math.round(overdraftNum * 100) - overdraftNum * 100) > 1e-7) {
      errors.overdraft_frequency_percent = 'Use no more than two decimal places.';
    }

    const billValue = String(formData.bill_payment_consistency_percent ?? '').trim();
    const billNum = Number(billValue);
    if (!billValue || !Number.isFinite(billNum) || billNum < 0 || billNum > 100) {
      errors.bill_payment_consistency_percent = 'Enter bill payment consistency from 0% to 100%.';
    } else if (Math.abs(Math.round(billNum * 100) - billNum * 100) > 1e-7) {
      errors.bill_payment_consistency_percent = 'Use no more than two decimal places.';
    }

    const cashflowNum = Number(formData.cashflow_stability_percent);
    if (isNaN(cashflowNum) || cashflowNum < 0 || cashflowNum > 100) {
      errors.cashflow_stability_percent = 'Cashflow stability must be between 0% and 100%.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Form submit handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError(null);

    if (submitting) return;

    if (!validateForm()) {
      return;
    }

    if (!user?.id) {
      setApiError('Authenticated user identity not found. Please log in again.');
      return;
    }

    setSubmitting(true);
    logger.info('assessment.submission.started', { model: 'alternative' });

    // Prepare exact DTO payload matching AlternativePredictionRequest.java:
    // public String age_range;
    // public int account_tenure_months;
    // public double monthly_income;
    // public double monthly_spending;
    // public double average_balance;
    // public double overdraft_frequency_percent;
    // public double bill_payment_consistency_percent;
    // public double cashflow_stability_percent;
    const payload = {
      age_range: formData.age_range,
      account_tenure_months: parseInt(formData.account_tenure_months, 10),
      monthly_income: parseFloat(formData.monthly_income),
      monthly_spending: parseFloat(formData.monthly_spending),
      average_balance: parseFloat(formData.average_balance),
      overdraft_frequency_percent: parseFloat(formData.overdraft_frequency_percent),
      bill_payment_consistency_percent: parseFloat(formData.bill_payment_consistency_percent),
      cashflow_stability_percent: parseFloat(formData.cashflow_stability_percent),
      loan_amount: parseFloat(formData.loan_amount),
      purpose: formData.purpose,
      existing_monthly_debt: parseFloat(formData.existing_monthly_debt),
      repayment_history: formData.repayment_history,
    };

    try {
      const responseData = await predictionService.predictAlternative(payload);
      setPredictionResult(responseData);
      logger.info('assessment.submission.succeeded', { model: 'alternative', applicationId: responseData.application_id });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      logger.errorOnce(err, 'assessment.submission.failed', { model: 'alternative' });
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        'Failed to process alternative credit assessment. Check backend and ML service status.';
      setApiError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setPredictionResult(null);
    setApiError(null);
    setFieldErrors({});
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 font-sans">
      {/* Top Breadcrumb & Controls */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Underwriting Console</span>
        </button>

        {predictionResult && (
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-navy-850 hover:bg-navy-800 text-xs font-medium text-brand-cyan border border-brand-cyan/30 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Assessment</span>
          </button>
        )}
      </div>

      {/* Page Title & Subtitle */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-cyan/15 border border-brand-cyan/30 text-brand-cyan text-xs font-semibold mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Behavioral Banking &amp; Thin-File Model</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Alternative Data Credit Risk Assessment
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl leading-relaxed">
          Scores credit-invisible and gig-economy applicants using 8 behavioral transaction parameters. Provides transparent coefficient attributions to evaluate cashflow stability and repayment habits without conventional bureau records.
        </p>
      </div>

      {/* If Prediction Result Exists: Show Results View */}
      {predictionResult ? (
        <RiskResultView 
          result={predictionResult} 
          onReset={handleReset} 
          modelTitle="Alternative Behavioral Credit Risk Assessment"
        />
      ) : (
        /* Form View */
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Global API Error Alert */}
          {apiError && (
            <div className="p-4 rounded-xl bg-brand-rose/15 border border-brand-rose/30 text-brand-rose flex items-start gap-3 text-xs sm:text-sm animate-shake">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="block font-semibold">Underwriting Submission Failed</strong>
                <span>{apiError}</span>
              </div>
            </div>
          )}

          {/* Section 1: Demographics & Account History */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-navy-800 text-slate-200">
              <User className="w-4 h-4 text-brand-cyan" />
              <h2 className="text-sm font-bold tracking-wide">1. Applicant Profile &amp; Banking Tenure</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Age Range */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Age Range (Bracket) <span className="text-brand-rose">*</span>
                </label>
                <select
                  value={formData.age_range}
                  onChange={(e) => handleInputChange('age_range', e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                  required
                >
                  {AGE_RANGE_OPTIONS.map((range) => (
                    <option key={range} value={range} className="bg-navy-900 text-white">
                      {range} Years
                    </option>
                  ))}
                </select>
                <p className="text-[11px] text-slate-500 mt-1">Applicant age demographic group.</p>
              </div>

              {/* Account Tenure Months */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Account Tenure (Months) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="600"
                  value={formData.account_tenure_months}
                  onChange={(e) => handleInputChange('account_tenure_months', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.account_tenure_months 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="24"
                  required
                />
                {fieldErrors.account_tenure_months && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.account_tenure_months}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Total months of active banking relationship.</p>
              </div>
            </div>
          </div>

          {/* Section 2: Cashflow & Financial Volume */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-navy-800 text-slate-200">
              <DollarSign className="w-4 h-4 text-brand-cyan" />
              <h2 className="text-sm font-bold tracking-wide">2. Monthly Financial Activity &amp; Liquidity</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              {/* Monthly Income */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Monthly Inflow / Income <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  step="any"
                  value={formData.monthly_income}
                  onChange={(e) => handleInputChange('monthly_income', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.monthly_income 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="48000"
                  required
                />
                {fieldErrors.monthly_income && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.monthly_income}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Average monthly deposits / wages.</p>
              </div>

              {/* Monthly Spending */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Monthly Outflow / Spending <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={formData.monthly_spending}
                  onChange={(e) => handleInputChange('monthly_spending', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.monthly_spending 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="32000"
                  required
                />
                {fieldErrors.monthly_spending && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.monthly_spending}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Total debits, utility bills, living costs.</p>
              </div>

              {/* Average Balance */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Average Monthly Balance <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.average_balance}
                  onChange={(e) => handleInputChange('average_balance', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.average_balance 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="15000"
                  required
                />
                {fieldErrors.average_balance && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.average_balance}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Mean account balance held over 30 days.</p>
              </div>
            </div>
          </div>

          {/* Section 3: Behavioral Risk & Stability Metrics */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-navy-800 text-slate-200">
              <TrendingUp className="w-4 h-4 text-brand-cyan" />
              <h2 className="text-sm font-bold tracking-wide">3. Behavioral Ratios &amp; Stability Metrics</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              {/* Overdraft Frequency Percent */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Overdraft Frequency (%) <span className="text-brand-rose">*</span>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    value={formData.overdraft_frequency_percent}
                    onChange={(e) => handleInputChange('overdraft_frequency_percent', e.target.value)}
                    className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all pr-8 ${
                      fieldErrors.overdraft_frequency_percent 
                        ? 'border-brand-rose focus:border-brand-rose' 
                        : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                    }`}
                    placeholder="5.0"
                    required
                  />
                  <Percent className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2" />
                </div>
                {fieldErrors.overdraft_frequency_percent && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.overdraft_frequency_percent}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Percentage of observed months with overdraft (0–100%, up to two decimal places).</p>
              </div>

              {/* Bill Payment Consistency Percent */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Bill Payment Consistency (%) <span className="text-brand-rose">*</span>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.bill_payment_consistency_percent}
                    onChange={(e) => handleInputChange('bill_payment_consistency_percent', e.target.value)}
                    className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all pr-8 ${
                      fieldErrors.bill_payment_consistency_percent 
                        ? 'border-brand-rose focus:border-brand-rose' 
                        : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                    }`}
                    placeholder="95.0"
                    required
                  />
                  <Percent className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2" />
                </div>
                {fieldErrors.bill_payment_consistency_percent && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.bill_payment_consistency_percent}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Percentage of on-time utility or recurring bill payments (0–100%, up to two decimal places).</p>
              </div>

              {/* Cashflow Stability Percent */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Cashflow Stability Score (%) <span className="text-brand-rose">*</span>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.cashflow_stability_percent}
                    onChange={(e) => handleInputChange('cashflow_stability_percent', e.target.value)}
                    className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all pr-8 ${
                      fieldErrors.cashflow_stability_percent 
                        ? 'border-brand-rose focus:border-brand-rose' 
                        : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                    }`}
                    placeholder="85.0"
                    required
                  />
                  <Percent className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2" />
                </div>
                {fieldErrors.cashflow_stability_percent && (
                  <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.cashflow_stability_percent}</p>
                )}
                <p className="text-[11px] text-slate-500 mt-1">Variance regularity of monthly incoming deposits.</p>
              </div>
            </div>
          </div>

          {/* Submission Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-xl bg-navy-900/50 border border-navy-800">
            <label className="block text-xs font-semibold text-slate-300">Requested amount (INR)
              <input type="number" min="0.01" step="0.01" required value={formData.loan_amount} onChange={(e) => handleInputChange('loan_amount', e.target.value)} className="mt-1 w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white" />
            </label>
            <label className="block text-xs font-semibold text-slate-300">Loan purpose
              <input type="text" maxLength="120" required value={formData.purpose} onChange={(e) => handleInputChange('purpose', e.target.value)} className="mt-1 w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white" />
            </label>
            <label className="block text-xs font-semibold text-slate-300">Existing monthly debt obligations (INR)
              <input type="number" min="0" step="0.01" required value={formData.existing_monthly_debt} onChange={(e) => handleInputChange('existing_monthly_debt', e.target.value)} className="mt-1 w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white" />
            </label>
            <label className="block text-xs font-semibold text-slate-300">Self-reported repayment history
              <select value={formData.repayment_history} onChange={(e) => handleInputChange('repayment_history', e.target.value)} className="mt-1 w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white">
                <option value="UNKNOWN">Not provided / unknown</option><option value="CURRENT">Payments current</option><option value="LATE_1_30">Late by 1–30 days</option><option value="LATE_31_90">Late by 31–90 days</option><option value="LATE_OVER_90">Late by more than 90 days</option>
              </select>
            </label>
          </div>
          {/* Submission Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-5 rounded-2xl bg-navy-900/60 border border-navy-800">
            <div className="text-xs text-slate-400">
              Evaluated with <strong className="text-slate-200">Behavioral Alternative Logistic Pipeline</strong> via authenticated gateway.
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <button
                type="button"
                onClick={() => setFormData(INITIAL_FORM_STATE)}
                disabled={submitting}
                className="px-4 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-700 text-slate-300 text-xs font-semibold border border-navy-700 transition-colors"
              >
                Reset Defaults
              </button>

              <button
                type="submit"
                disabled={submitting}
                className="flex-1 sm:flex-initial px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-cyan to-brand-blue hover:from-cyan-400 hover:to-blue-600 text-navy-950 hover:text-white font-bold text-xs sm:text-sm shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-navy-950/20 border-t-navy-950 rounded-full animate-spin"></div>
                    <span>Scoring Behavioral Risk...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Run Alternative Assessment</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

export default AlternativeAssessmentPage;
