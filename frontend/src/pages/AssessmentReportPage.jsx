import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Download, AlertCircle, FilePlus2, UserRound } from 'lucide-react';
import predictionService from '../services/predictionService';
import RiskResultView from '../components/RiskResultView';
import { downloadAssessmentPdf } from '../utils/assessmentPdf';
import { logger } from '../utils/logger';

const AssessmentReportPage = () => {
  const { applicationId } = useParams();
  const [application, setApplication] = useState(null);
  const [reportResult, setReportResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadError, setDownloadError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let active = true;
    predictionService.getApplication(applicationId)
      .then((record) => {
        if (!active) return;
        setApplication(record);
        if (!record.predictionDetails) {
          throw new Error('This older record does not contain a saved explanation, so a complete report is unavailable.');
        }
        let storedPrediction = {};
        try {
          storedPrediction = JSON.parse(record.predictionDetails);
        } catch {
          throw new Error('The saved explanation could not be read.');
        }
        setReportResult({
          ...storedPrediction,
          application_id: record.id,
          requested_loan_amount: record.loanAmount,
          tenure_months: record.tenureMonths,
          existing_monthly_debt: record.existingMonthlyDebt,
          repayment_history: record.repaymentHistory,
          purpose: record.purpose,
          assessment_timestamp: record.createdAt,
          model_version: record.modelVersion,
        });
      })
      .catch((loadError) => {
        logger.errorOnce(loadError, 'assessment.detail.load_failed', { applicationId });
        if (active) setError(loadError.response?.status === 404
          ? 'This application was not found for your account.'
          : loadError.message || 'Unable to load the saved assessment.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [applicationId]);

  const handleDownload = () => {
    setDownloadError('');
    setDownloading(true);
    try {
      downloadAssessmentPdf(application);
      logger.info('assessment.pdf.downloaded', { applicationId: application?.id });
    } catch (downloadError) {
      logger.errorOnce(downloadError, 'assessment.pdf.download_failed', { applicationId: application?.id });
      setDownloadError(downloadError.message || 'Unable to generate the assessment report.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) return <div className="py-16 text-center text-sm text-slate-400">Loading saved assessment…</div>;
  if (error) return <div className="max-w-3xl mx-auto rounded-2xl border border-brand-rose/30 bg-brand-rose/10 p-5 text-sm text-brand-rose"><AlertCircle className="inline w-4 h-4 mr-2" />{error}<p className="mt-4"><Link to="/profile" className="underline">Return to profile</Link></p></div>;
  if (!application || !reportResult) return null;

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      <div className="no-print flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-4">
          <Link to="/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white"><ArrowLeft className="w-4 h-4" />Dashboard</Link>
          <Link to="/profile" className="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white"><UserRound className="w-4 h-4" />Profile &amp; results</Link>
          <Link to="/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white"><FilePlus2 className="w-4 h-4" />New application</Link>
        </div>
        <button onClick={handleDownload} disabled={downloading} className="inline-flex items-center gap-2 rounded-xl bg-brand-blue px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-600 disabled:opacity-60"><Download className="w-4 h-4" />{downloading ? 'Preparing PDF…' : 'Download PDF'}</button>
      </div>
      {downloadError && <div role="alert" className="rounded-xl border border-brand-rose/30 bg-brand-rose/10 px-4 py-3 text-sm text-brand-rose">{downloadError}</div>}
      <article className="assessment-report report-card space-y-5 rounded-xl border border-slate-200 bg-white p-5 sm:p-8">
        <header className="border-b border-navy-700 pb-5">
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-brand-cyan">CredXAI · Assessment report</div>
          <h1 className="mt-2 text-2xl font-extrabold text-white">Application #{application.id}</h1>
          <p className="mt-1 text-sm text-slate-400">Saved assessment · {new Date(application.createdAt).toLocaleString()}</p>
        </header>
        {reportResult.model_version === 'unversioned' && <p className="text-xs text-slate-400">This historical record predates model artifact fingerprinting.</p>}
        <RiskResultView result={reportResult} showReset={false} />
      </article>
    </div>
  );
};

export default AssessmentReportPage;
