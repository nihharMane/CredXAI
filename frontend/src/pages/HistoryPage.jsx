import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import predictionService from '../services/predictionService';
import { 
  History, 
  Filter, 
  RotateCcw, 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  Calendar, 
  Clock, 
  Cpu, 
  FileText, 
  Sparkles, 
  Inbox, 
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Download
} from 'lucide-react';
import { downloadAssessmentPdf } from '../utils/assessmentPdf';
import { logger } from '../utils/logger';

const HistoryPage = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reportError, setReportError] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);

  // Filters
  const [modelFilter, setModelFilter] = useState('ALL'); // ALL, TRADITIONAL_DATA, ALTERNATIVE_DATA
  const [riskFilter, setRiskFilter] = useState('ALL');   // ALL, LOW_RISK, MEDIUM_RISK, HIGH_RISK

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await predictionService.getHistory();
      const items = Array.isArray(data) ? data : [];
      setApplications(items);
      logger.info('applications.history.loaded', { count: items.length });
    } catch (err) {
      logger.errorOnce(err, 'applications.history.failed', { operation: 'load' });
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        'Unable to load credit evaluations. Please check backend connectivity.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDownloadReport = async (applicationId) => {
    setReportError('');
    setDownloadingId(applicationId);
    try {
      const record = await predictionService.getApplication(applicationId);
      downloadAssessmentPdf(record);
      logger.info('assessment.pdf.downloaded', { applicationId: record.id });
    } catch (downloadError) {
      logger.errorOnce(downloadError, 'assessment.pdf.download_failed', { applicationId });
      setReportError(downloadError.response?.data?.message || downloadError.message || 'Unable to download this assessment report.');
    } finally {
      setDownloadingId(null);
    }
  };

  // Filter application list
  const filteredApplications = applications.filter((app) => {
    if (modelFilter !== 'ALL' && app.modelType !== modelFilter) return false;
    if (riskFilter !== 'ALL' && app.riskBand !== riskFilter) return false;
    return true;
  });

  const getRiskBadge = (riskBand) => {
    switch (riskBand) {
      case 'LOW_RISK':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-brand-emerald/15 text-brand-emerald border border-brand-emerald/30">
            <ShieldCheck className="w-3.5 h-3.5" />
            Low Risk
          </span>
        );
      case 'MEDIUM_RISK':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-brand-amber/15 text-brand-amber border border-brand-amber/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Medium Risk
          </span>
        );
      case 'HIGH_RISK':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-brand-rose/15 text-brand-rose border border-brand-rose/30">
            <ShieldAlert className="w-3.5 h-3.5" />
            High Risk
          </span>
        );
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'N/A';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 font-sans">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-blue/20 border border-brand-blue/30 text-brand-cyan text-xs font-semibold mb-2">
            <History className="w-3.5 h-3.5" />
            <span>Your saved applications</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Application history
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
            View your saved applications, review their assessment results, and download a report from the saved prediction.
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-300 hover:text-white border border-navy-700 text-xs sm:text-sm font-semibold transition-all disabled:opacity-50 self-start sm:self-auto"
        >
          <RotateCcw className={`w-4 h-4 text-brand-cyan ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Records</span>
        </button>
      </div>

      {reportError && <div role="alert" className="rounded-xl border border-brand-rose/30 bg-brand-rose/10 px-4 py-3 text-sm text-brand-rose">{reportError}</div>}

      {/* Filter Toolbar */}
      <div className="bg-navy-900/80 border border-navy-800 rounded-2xl p-4 sm:p-5 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <Filter className="w-4 h-4 text-brand-cyan" />
            <span>Filters:</span>
          </div>

          {/* Model Filter */}
          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400">Model:</label>
            <select
              value={modelFilter}
              onChange={(e) => setModelFilter(e.target.value)}
              className="bg-navy-950 border border-navy-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-brand-cyan transition-all"
            >
              <option value="ALL">All Models ({applications.length})</option>
              <option value="TRADITIONAL_DATA">Traditional Bureau</option>
              <option value="ALTERNATIVE_DATA">Alternative Behavioral</option>
            </select>
          </div>

          {/* Risk Band Filter */}
          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400">Risk Band:</label>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-navy-950 border border-navy-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-brand-cyan transition-all"
            >
              <option value="ALL">All Risk Bands</option>
              <option value="LOW_RISK">Low Risk Tier</option>
              <option value="MEDIUM_RISK">Medium Risk Tier</option>
              <option value="HIGH_RISK">High Risk Tier</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-slate-500 font-mono">
          Showing <strong className="text-slate-200">{filteredApplications.length}</strong> of{' '}
          <strong className="text-slate-200">{applications.length}</strong> applications
        </div>
      </div>

      {/* Main Content Area */}
      {error ? (
        <div className="p-6 rounded-2xl bg-brand-rose/10 border border-brand-rose/30 text-brand-rose flex items-start gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="block font-semibold">Failed to Retrieve Application History</strong>
            <span className="text-xs sm:text-sm text-slate-300">{error}</span>
          </div>
        </div>
      ) : loading ? (
        <div className="py-20 text-center rounded-2xl bg-navy-900/40 border border-navy-800 space-y-3">
          <div className="w-10 h-10 border-4 border-brand-cyan/20 border-t-brand-cyan rounded-full animate-spin mx-auto"></div>
          <p className="text-xs sm:text-sm text-slate-400">Loading your saved application history…</p>
        </div>
      ) : filteredApplications.length === 0 ? (
        /* Empty State */
        <div className="py-16 px-4 text-center rounded-2xl bg-navy-900/40 border border-dashed border-navy-800 flex flex-col items-center justify-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-navy-900 border border-navy-800 flex items-center justify-center text-slate-500 mb-1">
            <Inbox className="w-7 h-7" />
          </div>
          <h3 className="text-base font-bold text-white">No Application Records Found</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            {applications.length === 0
              ? "You don't have any saved applications yet. Start a traditional or alternative application to see your assessment here."
              : 'No records match the current filter criteria. Try resetting the model or risk band filters.'}
          </p>
          {applications.length === 0 && (
            <div className="flex items-center gap-3 pt-2">
              <Link
                to="/assess/traditional"
                className="px-4 py-2 rounded-xl bg-brand-blue hover:bg-blue-600 text-white text-xs font-semibold shadow-md transition-all flex items-center gap-1.5"
              >
                <FileText className="w-3.5 h-3.5" />
                Traditional Assessment
              </Link>
              <Link
                to="/assess/alternative"
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-brand-cyan to-brand-blue text-navy-950 font-bold text-xs shadow-md transition-all flex items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Alternative Assessment
              </Link>
            </div>
          )}
        </div>
      ) : (
        /* Records Table (Desktop) & Card List (Mobile) */
        <div className="bg-navy-900/80 border border-navy-800 rounded-2xl overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-navy-950/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-navy-800">
                <tr>
                  <th className="px-6 py-4">App ID</th>
                  <th className="px-6 py-4">Assessment Model</th>
                  <th className="px-6 py-4">Requested Amount</th>
                  <th className="px-6 py-4">Existing Debt / Month</th>
                  <th className="px-6 py-4">Repayment History</th>
                  <th className="px-6 py-4">Purpose</th>
                  <th className="px-6 py-4">Risk Tier</th>
                  <th className="px-6 py-4">Adverse-Outcome Estimate</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Created Timestamp</th>
                  <th className="px-6 py-4">Assessment report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60 font-sans">
                {filteredApplications.map((app) => {
                  const probPercent = app.defaultProbability != null
                    ? (app.defaultProbability * 100).toFixed(2)
                    : 'N/A';
                  return (
                    <tr
                      key={app.id}
                      className="hover:bg-navy-850/60 transition-colors duration-150"
                    >
                      <td className="px-6 py-4 font-mono font-semibold text-white">
                        #{app.id}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {app.modelType === 'ALTERNATIVE_DATA' ? (
                            <div className="p-1.5 rounded-lg bg-brand-cyan/15 text-brand-cyan border border-brand-cyan/20">
                              <Sparkles className="w-3.5 h-3.5" />
                            </div>
                          ) : (
                            <div className="p-1.5 rounded-lg bg-brand-blue/15 text-brand-cyan border border-brand-blue/20">
                              <FileText className="w-3.5 h-3.5" />
                            </div>
                          )}
                          <div>
                            <div className="font-semibold text-white">
                              {app.modelType === 'ALTERNATIVE_DATA'
                                ? 'Alternative Data'
                                : 'Traditional Bureau'}
                            </div>
                            <div className="text-[11px] text-slate-500 font-mono">
                              {app.modelType}
                            </div>
                            <div className="text-[10px] text-slate-500 font-mono">
                              Version: {app.modelVersion || 'unversioned'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono">
                        {app.loanAmount != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(app.loanAmount)) : '—'}
                      </td>
                      <td className="px-6 py-4 font-mono">
                        {app.existingMonthlyDebt != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(app.existingMonthlyDebt)) : '—'}
                      </td>
                      <td className="px-6 py-4">{app.repaymentHistory ? app.repaymentHistory.replaceAll('_', ' ') : 'UNKNOWN'}</td>
                      <td className="px-6 py-4 max-w-xs truncate" title={app.purpose || ''}>
                        {app.purpose || '—'}
                      </td>
                      <td className="px-6 py-4">
                        {getRiskBadge(app.riskBand)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2 font-mono text-sm font-bold text-white">
                          <span>{probPercent}%</span>
                        </div>
                        <div className="w-24 bg-navy-950 h-1.5 rounded-full overflow-hidden border border-navy-800/80 mt-1">
                          <div 
                            className={`h-full ${
                              app.riskBand === 'LOW_RISK'
                                ? 'bg-brand-emerald'
                                : app.riskBand === 'MEDIUM_RISK'
                                ? 'bg-brand-amber'
                                : 'bg-brand-rose'
                            }`}
                            style={{ width: `${Math.min(Math.max(Number(probPercent) || 0, 3), 100)}%` }}
                          />
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-navy-800 text-slate-300 border border-navy-700">
                          {app.status || 'PERSISTED'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-400 font-mono text-[11px]">
                        {formatDate(app.createdAt)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col items-start gap-2">
                          <Link to={`/history/${app.id}`} className="text-brand-cyan hover:text-cyan-300 font-semibold">View assessment</Link>
                          <button type="button" onClick={() => handleDownloadReport(app.id)} disabled={downloadingId === app.id} className="inline-flex items-center gap-1 text-slate-300 hover:text-white disabled:opacity-50">
                            <Download className="w-3.5 h-3.5" />
                            {downloadingId === app.id ? 'Preparing…' : 'Download PDF'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
