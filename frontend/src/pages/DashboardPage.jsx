import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, FileText, Plus, UserRound } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  return <div className="mx-auto max-w-7xl space-y-6">
    <header className="flex flex-col gap-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:p-8">
      <div><p className="text-sm font-semibold text-teal-700">Applicant workspace</p><h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">Welcome{user?.fullName ? `, ${user.fullName.split(' ')[0]}` : ''}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">Run a credit readiness assessment and review its saved model factors in your profile.</p></div>
      <Link to="/assessment/new" className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-[#24364B] px-5 py-3 text-sm font-semibold text-white hover:bg-[#18283A] focus:outline-none focus:ring-2 focus:ring-[#24364B] focus:ring-offset-2"><Plus className="h-4 w-4"/>Start new assessment</Link>
    </header>
    <section className="grid gap-4 md:grid-cols-2">
      <Link to="/assessment/new" className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-blue-200 hover:shadow-md"><span className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-700"><FileText className="h-5 w-5"/></span><h2 className="mt-4 font-semibold text-slate-900">New risk assessment</h2><p className="mt-1 text-sm leading-6 text-slate-600">Enter application details to receive a saved model estimate with its feature contribution explanation.</p><span className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-blue-700">Start assessment <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1"/></span></Link>
      <Link to="/profile" className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-teal-200 hover:shadow-md"><span className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700"><UserRound className="h-5 w-5"/></span><h2 className="mt-4 font-semibold text-slate-900">Profile &amp; recent results</h2><p className="mt-1 text-sm leading-6 text-slate-600">See your latest saved assessments, risk estimates, and the factors that contributed to each result.</p><span className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-teal-700">View profile <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1"/></span></Link>
    </section>
    <p className="text-xs leading-5 text-slate-500">CredXAI provides informational model estimates. They are not lending decisions or a guarantee of approval.</p>
  </div>;
}
