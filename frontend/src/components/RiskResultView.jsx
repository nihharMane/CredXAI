import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Info,
  RotateCcw,
  Sparkles
} from 'lucide-react';

/**
 * Universal XAI Risk Prediction Result Component supporting both:
 * 1. Traditional Credit Risk Model (Home Credit Logistic Regression)
 * 2. Alternative Data Risk Model (Behavioral / Thin-File Pipeline)
 *
 * Handles actual returned fields:
 * - model_type ("TRADITIONAL_DATA" | "ALTERNATIVE_DATA")
 * - risk_band ("LOW_RISK" | "MEDIUM_RISK" | "HIGH_RISK")
 * - default_probability_percent (number)
 * - default_probability (float)
 * - risk_increasing_factors (array of { feature, contribution })
 * - risk_reducing_factors (array of { feature, contribution })
 * - explanation (array of strings)
 * - disclaimer (string)
 */
const RiskResultView = ({ result, onReset, modelTitle = 'Credit Risk Assessment', showReset = true }) => {
  if (!result) return null;

  const riskBand = result.risk_band || 'UNKNOWN';
  const probabilityPercent = result.default_probability_percent ?? (
    result.default_probability != null ? Math.round(result.default_probability * 10000) / 100 : 0
  );

  const modelLabel = result.model_type === 'ALTERNATIVE_DATA'
    ? 'Alternative Banking Behavioral Model'
    : 'Home Credit Demographic & Liability Model';

  // Risk styling configurations
  const getRiskDetails = (band) => {
    switch (band) {
      case 'LOW_RISK':
        return {
          title: 'Low Risk Tier',
          color: 'text-brand-emerald',
          bgColor: 'bg-brand-emerald/10',
          borderColor: 'border-brand-emerald/30',
          badgeBg: 'bg-brand-emerald/20 text-brand-emerald border-brand-emerald/40',
          barColor: 'bg-brand-emerald',
          icon: ShieldCheck,
          summary: 'The model places this assessment in its low band. This category is a supporting signal, not a lending decision.'
        };
      case 'MEDIUM_RISK':
        return {
          title: 'Moderate Risk Tier',
          color: 'text-brand-amber',
          bgColor: 'bg-brand-amber/10',
          borderColor: 'border-brand-amber/30',
          badgeBg: 'bg-brand-amber/20 text-brand-amber border-brand-amber/40',
          barColor: 'bg-brand-amber',
          icon: AlertTriangle,
          summary: 'The model places this assessment in its moderate band. This category is a supporting signal, not a lending decision.'
        };
      case 'HIGH_RISK':
      default:
        return {
          title: 'High Risk Tier',
          color: 'text-brand-rose',
          bgColor: 'bg-brand-rose/10',
          borderColor: 'border-brand-rose/30',
          badgeBg: 'bg-brand-rose/20 text-brand-rose border-brand-rose/40',
          barColor: 'bg-brand-rose',
          icon: ShieldAlert,
          summary: 'The model places this assessment in its high band. This category is a supporting signal, not a lending decision.'
        };
    }
  };

  const riskMeta = getRiskDetails(riskBand);
  const RiskIcon = riskMeta.icon;

  const increasingFactors = Array.isArray(result.risk_increasing_factors) ? result.risk_increasing_factors : [];
  const reducingFactors = Array.isArray(result.risk_reducing_factors) ? result.risk_reducing_factors : [];
  const explanations = Array.isArray(result.explanation) ? result.explanation : (result.explanation ? [result.explanation] : []);

  // Compute maximum absolute contribution for normalized bar scaling
  const allContributions = [
    ...increasingFactors.map(f => Math.abs(f.contribution || 0)),
    ...reducingFactors.map(f => Math.abs(f.contribution || 0))
  ];
  const maxContribution = allContributions.length > 0 ? Math.max(...allContributions, 0.1) : 1;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* 1. Header & Summary Card */}
      <div className={`p-6 sm:p-8 rounded-2xl ${riskMeta.bgColor} border ${riskMeta.borderColor} relative overflow-hidden shadow-2xl`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${riskMeta.badgeBg}`}>
                {riskBand.replace('_', ' ')}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Engine: {modelLabel}
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2.5">
              <RiskIcon className={`w-8 h-8 ${riskMeta.color}`} />
              <span>{riskMeta.title}</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              {riskMeta.summary}
            </p>
          </div>

          {/* Probability Dial / Metric */}
          <div className="bg-navy-950/80 border border-navy-800 rounded-2xl p-5 text-center min-w-[200px] shadow-lg flex-shrink-0">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Estimated Adverse-Outcome Probability
            </div>
            <div className={`text-4xl font-extrabold tracking-tight ${riskMeta.color}`}>
              {probabilityPercent.toFixed(2)}%
            </div>
            <div className="w-full bg-navy-800 h-2 rounded-full mt-3 overflow-hidden">
              <div 
                className={`h-full ${riskMeta.barColor} transition-all duration-700 ease-out`}
                style={{ width: `${Math.min(Math.max(probabilityPercent, 2), 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>0% (lower score)</span>
              <span>100% (higher score)</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 rounded-xl bg-navy-900/70 border border-navy-800 p-4 text-xs">
        <div><span className="text-slate-500">Application</span><p className="mt-1 text-white font-mono">{result.application_id ? `#${result.application_id}` : 'Not available'}</p></div>
        <div><span className="text-slate-500">Requested amount</span><p className="mt-1 text-white">{result.requested_loan_amount != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(result.requested_loan_amount)) : 'Not available'}</p></div>
        <div><span className="text-slate-500">Assessment time</span><p className="mt-1 text-white">{result.assessment_timestamp ? new Date(result.assessment_timestamp).toLocaleString() : 'Not available'}</p></div>
        <div><span className="text-slate-500">Model version</span><p className="mt-1 text-white font-mono">{result.model_version || 'Unversioned'}</p></div>
        <div><span className="text-slate-500">Application status</span><p className="mt-1 text-white">{result.application_status || 'COMPLETED'}</p></div>
        <div><span className="text-slate-500">Existing monthly debt</span><p className="mt-1 text-white">{result.existing_monthly_debt != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(result.existing_monthly_debt)) : 'Not available'}</p></div>
        <div><span className="text-slate-500">Self-reported repayment history</span><p className="mt-1 text-white">{(result.repayment_history || 'UNKNOWN').replaceAll('_', ' ')}</p></div>
        {result.purpose && <div className="sm:col-span-2 lg:col-span-4"><span className="text-slate-500">Loan purpose</span><p className="mt-1 text-white break-words">{result.purpose}</p></div>}
      </div>

      {/* 2. Factor Attributions (Explainable AI Waterfall Bars) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Increasing Factors */}
        <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-navy-800">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-brand-rose" />
              <h3 className="text-sm font-bold text-white tracking-wide">
                Top Risk-Increasing Factors
              </h3>
            </div>
            <span className="text-[11px] text-brand-rose/80 font-medium">
              +{increasingFactors.length} factors
            </span>
          </div>

          {increasingFactors.length === 0 ? (
            <p className="text-xs text-slate-500 py-4 text-center">
              No significant risk-increasing factors identified.
            </p>
          ) : (
            <div className="space-y-3.5 pt-1">
              {increasingFactors.map((item, idx) => {
                const weight = Math.abs(item.contribution || 0);
                const percentWidth = Math.min(Math.round((weight / maxContribution) * 100), 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-medium">{item.feature}</span>
                      <span className="text-brand-rose font-mono font-semibold">
                        +{Number(item.contribution).toFixed(4)}
                      </span>
                    </div>
                    <div className="w-full bg-navy-950 h-2 rounded-full overflow-hidden border border-navy-800/80">
                      <div 
                        className="h-full bg-gradient-to-r from-rose-500/80 to-rose-400 rounded-full"
                        style={{ width: `${percentWidth}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Risk Reducing Factors */}
        <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-navy-800">
            <div className="flex items-center gap-2">
              <TrendingDown className="w-5 h-5 text-brand-emerald" />
              <h3 className="text-sm font-bold text-white tracking-wide">
                Top Risk-Reducing Factors
              </h3>
            </div>
            <span className="text-[11px] text-brand-emerald/80 font-medium">
              +{reducingFactors.length} factors
            </span>
          </div>

          {reducingFactors.length === 0 ? (
            <p className="text-xs text-slate-500 py-4 text-center">
              No significant risk-reducing factors identified.
            </p>
          ) : (
            <div className="space-y-3.5 pt-1">
              {reducingFactors.map((item, idx) => {
                const weight = Math.abs(item.contribution || 0);
                const percentWidth = Math.min(Math.round((weight / maxContribution) * 100), 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-medium">{item.feature}</span>
                      <span className="text-brand-emerald font-mono font-semibold">
                        {Number(item.contribution).toFixed(4)}
                      </span>
                    </div>
                    <div className="w-full bg-navy-950 h-2 rounded-full overflow-hidden border border-navy-800/80">
                      <div 
                        className="h-full bg-gradient-to-r from-emerald-500/80 to-emerald-400 rounded-full"
                        style={{ width: `${percentWidth}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
      <p className="text-[11px] text-slate-500 -mt-4">
        Signed factor values are contributions to the model’s log-odds score: positive values raise the estimated odds of the adverse target and negative values lower them. They are associations, not causes, and are not percentage-point changes.
      </p>

      {/* 3. Natural Language Explanation Card */}
      {explanations.length > 0 && (
        <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-3">
          <div className="flex items-center gap-2 text-brand-cyan text-sm font-bold">
            <Sparkles className="w-4 h-4" />
            <span>Automated Model Rationalization</span>
          </div>
          <ul className="space-y-2 text-xs sm:text-sm text-slate-300 leading-relaxed">
            {explanations.map((exp, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-brand-cyan font-bold">•</span>
                <span>{exp}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 4. Regulatory Disclaimer */}
      {result.disclaimer && (
        <div className="p-4 rounded-xl bg-navy-950/60 border border-navy-800/80 flex items-start gap-3 text-xs text-slate-400">
          <Info className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="text-slate-300">Regulatory &amp; Governance Disclaimer:</strong> {result.disclaimer}
          </p>
        </div>
      )}
      <p className="text-xs text-slate-400">
        CredXAI is a decision-support prototype. Probabilities and rule-based risk bands are not validated lending decisions or guarantees. Review the data and limitations before relying on an assessment.
      </p>

      {/* 5. Actions: Run Another Assessment */}
      {showReset && (
        <div className="pt-2 flex justify-end">
          <button
            onClick={onReset}
            className="print:hidden px-5 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-700 text-white text-xs sm:text-sm font-semibold border border-navy-700 transition-all flex items-center gap-2 shadow-md"
          >
            <RotateCcw className="w-4 h-4 text-brand-cyan" />
            <span>Start New Assessment</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default RiskResultView;
