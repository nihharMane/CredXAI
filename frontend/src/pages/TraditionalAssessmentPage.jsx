import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import predictionService from '../services/predictionService';
import TraditionalResultView from '../components/TraditionalResultView';
import { logger } from '../utils/logger';
import { 
  FileText, 
  User, 
  DollarSign, 
  Home, 
  Car, 
  GraduationCap, 
  Users, 
  Send, 
  AlertCircle, 
  RotateCcw,
  Sparkles,
  ArrowLeft
} from 'lucide-react';

// Exact categorical domain values verified from fitted model OneHotEncoder & preprocessing
const INCOME_TYPE_OPTIONS = [
  'Working',
  'Commercial associate',
  'Pensioner',
  'State servant',
  'Businessman',
  'Student',
  'Unemployed',
  'Maternity leave',
];

const EDUCATION_OPTIONS = [
  'Secondary / secondary special',
  'Higher education',
  'Incomplete higher',
  'Lower secondary',
  'Academic degree',
];

const HOUSING_TYPE_OPTIONS = [
  'House / apartment',
  'With parents',
  'Municipal apartment',
  'Rented apartment',
  'Office apartment',
  'Co-op apartment',
];

// Initial form values with sensible standard defaults
const INITIAL_FORM_STATE = {
  // Group 1: Personal and family information
  age: 35,
  children: 0,
  family_members: 2,
  // Group 2: Income and credit details
  income_type: 'Working',
  monthly_income: 45000,
  credit_amount: 250000,
  existing_monthly_debt: 0,
  repayment_history: 'UNKNOWN',
  purpose: 'PERSONAL',
  monthly_installment: 12500,
  goods_price: 240000,
  // Group 3: Assets and housing information
  owns_car: 'Y',
  owns_property: 'Y',
  education: 'Higher education',
  housing_type: 'House / apartment',
};

const TraditionalAssessmentPage = () => {
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

  // Validation logic matching model parameters
  const validateForm = () => {
    const errors = {};

    const ageNum = Number(formData.age);
    if (isNaN(ageNum) || ageNum < 18 || ageNum > 100) {
      errors.age = 'Age must be between 18 and 100 years.';
    }

    const childrenNum = Number(formData.children);
    if (isNaN(childrenNum) || childrenNum < 0 || childrenNum > 20) {
      errors.children = 'Children count must be between 0 and 20.';
    }

    const familyNum = Number(formData.family_members);
    if (isNaN(familyNum) || familyNum < 1 || familyNum > 20) {
      errors.family_members = 'Family members must be between 1 and 20.';
    }

    const incomeNum = Number(formData.monthly_income);
    if (isNaN(incomeNum) || incomeNum <= 0 || incomeNum > 1000000000) {
      errors.monthly_income = 'Monthly income must be greater than 0 and within the supported range.';
    }

    const creditNum = Number(formData.credit_amount);
    if (isNaN(creditNum) || creditNum <= 0 || creditNum > 9999999999999.99) {
      errors.credit_amount = 'Credit amount must be greater than 0.';
    } else if (Math.abs(Math.round(creditNum * 100) - creditNum * 100) > 1e-7) {
      errors.credit_amount = 'Credit amount can have at most two decimal places.';
    }

    const existingDebtNum = Number(formData.existing_monthly_debt);
    if (!Number.isFinite(existingDebtNum) || existingDebtNum < 0 || existingDebtNum > 9999999999999.99) {
      errors.existing_monthly_debt = 'Existing monthly obligations must be 0 or more and within the supported range.';
    } else if (Math.abs(Math.round(existingDebtNum * 100) - existingDebtNum * 100) > 1e-7) {
      errors.existing_monthly_debt = 'Existing monthly obligations can have at most two decimal places.';
    }

    if (!formData.purpose.trim()) {
      errors.purpose = 'Loan purpose is required.';
    } else if (formData.purpose.trim().length > 120) {
      errors.purpose = 'Loan purpose must be 120 characters or fewer.';
    }

    const installmentNum = Number(formData.monthly_installment);
    if (isNaN(installmentNum) || installmentNum <= 0 || installmentNum > 1000000000) {
      errors.monthly_installment = 'Monthly installment must be greater than 0 and within the supported range.';
    }

    const goodsNum = Number(formData.goods_price);
    if (isNaN(goodsNum) || goodsNum <= 0 || goodsNum > 1000000000) {
      errors.goods_price = 'Goods price must be greater than 0 and within the supported range.';
    }

    if (!formData.income_type) {
      errors.income_type = 'Income type is required.';
    }
    if (!formData.education) {
      errors.education = 'Education level is required.';
    }
    if (!formData.housing_type) {
      errors.housing_type = 'Housing type is required.';
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

    if (!user) {
      setApiError('Your session could not be verified. Please log in again.');
      return;
    }

    setSubmitting(true);
    logger.info('assessment.submission.started', { model: 'traditional' });

    // Prepare exact DTO payload matching TraditionalPredictionRequest.java
    const payload = {
      age: parseInt(formData.age, 10),
      children: parseInt(formData.children, 10),
      family_members: parseInt(formData.family_members, 10),
      income_type: formData.income_type,
      monthly_income: parseFloat(formData.monthly_income),
      credit_amount: parseFloat(formData.credit_amount),
      existing_monthly_debt: parseFloat(formData.existing_monthly_debt),
      repayment_history: formData.repayment_history,
      purpose: formData.purpose.trim(),
      monthly_installment: parseFloat(formData.monthly_installment),
      goods_price: parseFloat(formData.goods_price),
      owns_car: formData.owns_car,
      owns_property: formData.owns_property,
      education: formData.education,
      housing_type: formData.housing_type,
    };

    try {
      const responseData = await predictionService.predictTraditional(payload);
      setPredictionResult(responseData);
      logger.info('assessment.submission.succeeded', { model: 'traditional', applicationId: responseData.application_id });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      logger.errorOnce(err, 'assessment.submission.failed', { model: 'traditional' });
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        'Failed to process traditional credit assessment. Check backend and ML service status.';
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
    <div className="max-w-5xl mx-auto space-y-6">
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-blue/20 border border-brand-blue/30 text-brand-cyan text-xs font-semibold mb-2">
          <FileText className="w-3.5 h-3.5" />
          <span>Bureau Demographic &amp; Liability Model</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Traditional Credit Risk Assessment
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl leading-relaxed">
          Enter monthly income, proposed credit, obligations, and profile attributes. The current model returns an uncalibrated estimate and coefficient-based factors for review; it is not a lending decision.
        </p>
      </div>

      {/* If Prediction Result Exists: Show Results View */}
      {predictionResult ? (
        <TraditionalResultView result={predictionResult} onReset={handleReset} />
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

          {/* Section 1: Personal & Family Information */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-navy-800 text-slate-200">
              <User className="w-4 h-4 text-brand-cyan" />
              <h2 className="text-sm font-bold tracking-wide">1. Personal &amp; Family Information</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              {/* Age */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Age (Years) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="18"
                  max="100"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.age 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="35"
                  required
                />
                {fieldErrors.age && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.age}</p>}
              </div>

              {/* Number of Children */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Number of Children <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  value={formData.children}
                  onChange={(e) => handleInputChange('children', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.children 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="0"
                  required
                />
                {fieldErrors.children && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.children}</p>}
              </div>

              {/* Family Members Count */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Total Family Members <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={formData.family_members}
                  onChange={(e) => handleInputChange('family_members', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.family_members 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="2"
                  required
                />
                {fieldErrors.family_members && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.family_members}</p>}
              </div>
            </div>
          </div>

          {/* Section 2: Income & Credit Details */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-navy-800 text-slate-200">
              <DollarSign className="w-4 h-4 text-brand-cyan" />
              <h2 className="text-sm font-bold tracking-wide">2. Income &amp; Credit Obligations</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {/* Income Type Dropdown */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Income Classification <span className="text-brand-rose">*</span>
                </label>
                <select
                  value={formData.income_type}
                  onChange={(e) => handleInputChange('income_type', e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                  required
                >
                  {INCOME_TYPE_OPTIONS.map((opt) => (
                    <option key={opt} value={opt} className="bg-navy-900 text-white">
                      {opt}
                    </option>
                  ))}
                </select>
              </div>

              {/* Monthly Income */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Monthly Income (INR / month) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000000000"
                  step="0.01"
                  value={formData.monthly_income}
                  onChange={(e) => handleInputChange('monthly_income', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.monthly_income 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="45000"
                  required
                />
                {fieldErrors.monthly_income && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.monthly_income}</p>}
              </div>

              {/* Requested Credit Amount */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Requested Credit Amount (INR) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="9999999999999.99"
                  step="0.01"
                  value={formData.credit_amount}
                  onChange={(e) => handleInputChange('credit_amount', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.credit_amount 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="250000"
                  required
                />
                {fieldErrors.credit_amount && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.credit_amount}</p>}
              </div>

              {/* Monthly Installment (Annuity) */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Monthly Installment / EMI (INR / month) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000000000"
                  step="any"
                  value={formData.monthly_installment}
                  onChange={(e) => handleInputChange('monthly_installment', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.monthly_installment 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="12500"
                  required
                />
                {fieldErrors.monthly_installment && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.monthly_installment}</p>}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Existing Monthly Debt Obligations (INR / month) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="9999999999999.99"
                  step="0.01"
                  value={formData.existing_monthly_debt}
                  onChange={(e) => handleInputChange('existing_monthly_debt', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${fieldErrors.existing_monthly_debt ? 'border-brand-rose' : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'}`}
                  required
                />
                {fieldErrors.existing_monthly_debt && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.existing_monthly_debt}</p>}
                <p className="text-[11px] text-slate-500 mt-1">Recorded for application context; the current traditional score does not use this separate field.</p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Self-reported repayment history</label>
                <select value={formData.repayment_history} onChange={(e) => handleInputChange('repayment_history', e.target.value)} className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white">
                  <option value="UNKNOWN">Not provided / unknown</option>
                  <option value="CURRENT">Payments current</option>
                  <option value="LATE_1_30">Late by 1–30 days</option>
                  <option value="LATE_31_90">Late by 31–90 days</option>
                  <option value="LATE_OVER_90">Late by more than 90 days</option>
                </select>
                <p className="text-[11px] text-slate-500 mt-1">Saved as self-reported context; not used by the current model.</p>
              </div>

              {/* Goods Price */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Purchased Goods Price (INR) <span className="text-brand-rose">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000000000"
                  step="any"
                  value={formData.goods_price}
                  onChange={(e) => handleInputChange('goods_price', e.target.value)}
                  className={`w-full px-3.5 py-2.5 bg-navy-950/80 border rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
                    fieldErrors.goods_price 
                      ? 'border-brand-rose focus:border-brand-rose' 
                      : 'border-navy-700 focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan'
                  }`}
                  placeholder="240000"
                  required
                />
                {fieldErrors.goods_price && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.goods_price}</p>}
              </div>
            </div>
          </div>

          {/* Section 3: Assets, Education & Housing */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-navy-800 text-slate-200">
              <Home className="w-4 h-4 text-brand-cyan" />
              <h2 className="text-sm font-bold tracking-wide">3. Assets &amp; Living Accommodations</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {/* Owns Car */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Owns Vehicle / Car <span className="text-brand-rose">*</span>
                </label>
                <select
                  value={formData.owns_car}
                  onChange={(e) => handleInputChange('owns_car', e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                  required
                >
                  <option value="Y" className="bg-navy-900 text-white">Yes (Y)</option>
                  <option value="N" className="bg-navy-900 text-white">No (N)</option>
                </select>
              </div>

              {/* Owns Property */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Owns Real Estate / Property <span className="text-brand-rose">*</span>
                </label>
                <select
                  value={formData.owns_property}
                  onChange={(e) => handleInputChange('owns_property', e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                  required
                >
                  <option value="Y" className="bg-navy-900 text-white">Yes (Y)</option>
                  <option value="N" className="bg-navy-900 text-white">No (N)</option>
                </select>
              </div>

              {/* Education Level */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Highest Education <span className="text-brand-rose">*</span>
                </label>
                <select
                  value={formData.education}
                  onChange={(e) => handleInputChange('education', e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                  required
                >
                  {EDUCATION_OPTIONS.map((opt) => (
                    <option key={opt} value={opt} className="bg-navy-900 text-white">
                      {opt}
                    </option>
                  ))}
                </select>
              </div>

              {/* Housing Type */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Housing Type <span className="text-brand-rose">*</span>
                </label>
                <select
                  value={formData.housing_type}
                  onChange={(e) => handleInputChange('housing_type', e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                  required
                >
                  {HOUSING_TYPE_OPTIONS.map((opt) => (
                    <option key={opt} value={opt} className="bg-navy-900 text-white">
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 p-4 rounded-xl bg-navy-900/50 border border-navy-800">
            <label className="block text-xs font-semibold text-slate-300">Loan purpose
              <input type="text" maxLength="120" required value={formData.purpose} onChange={(e) => handleInputChange('purpose', e.target.value)} className="mt-1 w-full px-3.5 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white" placeholder="Personal, home, education, business..." />
              {fieldErrors.purpose && <p className="text-[11px] text-brand-rose mt-1">{fieldErrors.purpose}</p>}
            </label>
          </div>

          {/* Submission Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-5 rounded-2xl bg-navy-900/60 border border-navy-800">
            <div className="text-xs text-slate-400">
              Evaluated with <strong className="text-slate-200">Home Credit Logistic Regressor</strong> via authenticated gateway.
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
                className="flex-1 sm:flex-initial px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-blue to-cyan-500 hover:from-blue-600 hover:to-cyan-400 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                    <span>Computing Prediction...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Run Assessment</span>
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

export default TraditionalAssessmentPage;
