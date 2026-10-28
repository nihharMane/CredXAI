import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Shield, Mail, Hash, CheckCircle2, ArrowUpRight, FileText } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import predictionService from '../services/predictionService';

const money = value => value == null ? '—' : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(value));
const riskLabel = value => String(value || 'Not recorded').replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
const savedResult = record => {
  try { return record.predictionDetails ? JSON.parse(record.predictionDetails) : null; } catch { return null; }
};

function FactorChart({ record }) {
  const result = savedResult(record);
  const factors = [
    ...(Array.isArray(result?.risk_increasing_factors) ? result.risk_increasing_factors.map(item => ({ ...item, increasing: true })) : []),
    ...(Array.isArray(result?.risk_reducing_factors) ? result.risk_reducing_factors.map(item => ({ ...item, increasing: false })) : []),
  ].filter(item => Number.isFinite(Number(item.contribution)))
    .sort((a, b) => Math.abs(Number(b.contribution)) - Math.abs(Number(a.contribution))).slice(0, 6);
  if (!factors.length) return <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs text-slate-600">No saved factor explanation is available for this assessment.</p>;
  const max = Math.max(...factors.map(factor => Math.abs(Number(factor.contribution))), 0.0001);
  return <div className="mt-3 space-y-2" aria-label="Saved factors contributing to this assessment">
    {factors.map((factor, index) => {
      const width = Math.max(2, (Math.abs(Number(factor.contribution)) / max) * 46);
      return <div key={`${factor.feature}-${index}`} className="grid grid-cols-[minmax(100px,1fr)_minmax(100px,1.4fr)_auto] items-center gap-2 text-xs">
        <span className="truncate text-slate-700" title={factor.feature}>{factor.feature || 'Unlabeled feature'}</span>
        <div className="relative h-5 rounded bg-slate-50" aria-hidden="true"><div className="absolute inset-y-0 left-1/2 w-px bg-slate-300"/><div className={`absolute inset-y-1 rounded-sm ${factor.increasing ? 'bg-red-500' : 'bg-teal-600'}`} style={factor.increasing ? { left: '50%', width: `${width}%` } : { right: '50%', width: `${width}%` }}/></div>
        <span className={`whitespace-nowrap font-medium tabular-nums ${factor.increasing ? 'text-red-700' : 'text-teal-800'}`} title="Saved signed model contribution">{Number(factor.contribution) > 0 ? '+' : ''}{Number(factor.contribution).toFixed(3)}</span>
      </div>;
    })}
    <div className="flex justify-between pt-1 text-[11px] text-slate-500"><span>← Lowers predicted risk</span><span>Raises predicted risk →</span></div>
  </div>;
}

export default function ProfilePage() {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    predictionService.getHistory().then(async rows => {
      if (!Array.isArray(rows) || !active) return;
      const recent = await Promise.all(rows.slice(0, 5).map(record => predictionService.getApplication(record.id)));
      if (active) setApplications(recent);
    })
      .catch(() => { if (active) setError('Your recent assessment results could not be loaded.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return <div className="mx-auto max-w-5xl space-y-6">
    <header><p className="text-sm font-semibold text-teal-700">Account overview</p><h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">Your profile</h1><p className="mt-2 text-sm text-slate-600">Account details and your latest saved assessment results.</p></header>
    <section className="space-y-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7" aria-label="Account information">
      <div className="flex items-center gap-4 border-b border-slate-200 pb-5"><div className="flex h-14 w-14 items-center justify-center rounded-xl bg-blue-50 text-blue-700"><User className="h-6 w-6" aria-hidden="true"/></div><div className="min-w-0"><h2 className="text-lg font-semibold text-slate-900">{user?.fullName || 'Account holder'}</h2><p className="mt-1 flex items-center gap-2 text-sm text-slate-600"><Mail className="h-4 w-4" aria-hidden="true"/>{user?.email || 'Email unavailable'}</p></div></div>
      <div className="grid gap-4 sm:grid-cols-2"><div className="rounded-lg border border-slate-200 bg-slate-50 p-4"><div className="flex items-center gap-2 text-xs font-medium text-slate-600"><Hash className="h-4 w-4 text-teal-700"/>Account reference</div><p className="mt-2 text-sm font-semibold text-slate-900">{user?.id ? `#${user.id}` : 'Unavailable'}</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-4"><div className="flex items-center gap-2 text-xs font-medium text-slate-600"><CheckCircle2 className="h-4 w-4 text-green-700"/>Session</div><p className="mt-2 text-sm font-semibold text-slate-900">Signed in</p><p className="mt-1 text-xs text-slate-600">Your session is used to retrieve only your saved applications.</p></div></div>
      <div className="rounded-lg border border-blue-100 bg-blue-50/60 p-4"><div className="flex items-center gap-2 text-sm font-semibold text-[#16324F]"><Shield className="h-4 w-4 text-blue-700"/>About your assessment data</div><p className="mt-2 text-sm leading-6 text-slate-700">Saved predictions and their explanations come from the model response recorded at assessment time. Factor contributions describe how model inputs affected that saved score; they are not causal explanations or lending decisions.</p></div>
    </section>
    <section aria-label="Recent assessment results" className="space-y-4"><div><h2 className="text-xl font-bold text-slate-900">Recent assessment results</h2><p className="mt-1 text-sm text-slate-600">Your five most recent saved results and their recorded risk factors.</p></div>
      {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>}
      {loading ? <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-600">Loading your saved results…</div> : !error && applications.length === 0 ? <div className="rounded-xl border border-slate-200 bg-white p-8 text-center"><FileText className="mx-auto h-8 w-8 text-slate-400"/><h3 className="mt-3 font-semibold text-slate-900">No saved assessments yet</h3><p className="mt-1 text-sm text-slate-600">Your results and model factor charts will appear here after an assessment.</p><Link to="/assessment/new" className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white">Start an assessment <ArrowUpRight size={16}/></Link></div> : <div className="space-y-4">{applications.map(record => {
        const result = savedResult(record);
        const probability = result?.default_probability_percent ?? (record.defaultProbability == null ? null : Number(record.defaultProbability) * 100);
        return <article key={record.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"><header className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="font-semibold text-slate-900">Application #{record.id} · {riskLabel(record.modelType)}</h3><p className="mt-1 text-xs text-slate-600">{record.createdAt ? new Date(record.createdAt).toLocaleString() : 'Date not recorded'} · {money(record.loanAmount)}</p></div><div className="text-right"><p className="text-xs text-slate-600">Saved model risk</p><p className="mt-1 text-sm font-bold text-slate-900">{riskLabel(record.riskBand)}{probability == null ? '' : ` · ${Number(probability).toFixed(2)}%`}</p></div></header><div className="mt-4 border-t border-slate-100 pt-3"><h4 className="text-xs font-semibold uppercase tracking-wide text-slate-600">Saved feature contributions <span className="normal-case font-normal">(signed model values; relative bar scale per assessment)</span></h4><FactorChart record={record}/></div><Link to={`/applications/${record.id}`} className="mt-4 inline-flex text-sm font-semibold text-blue-700 hover:underline">View saved assessment <ArrowUpRight size={15} className="ml-1"/></Link></article>;
      })}</div>}
    </section>
  </div>;
}
