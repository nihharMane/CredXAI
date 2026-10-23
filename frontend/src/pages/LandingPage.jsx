import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Sparkles, FileText } from 'lucide-react';

const LandingPage = () => (
  <main className="min-h-screen bg-navy-950 text-white px-5 py-8 sm:px-10 lg:px-16">
    <nav className="max-w-7xl mx-auto flex items-center justify-between">
      <span className="text-xl font-extrabold tracking-tight">CredX<span className="text-brand-cyan">AI</span></span>
      <div className="flex items-center gap-3">
        <Link to="/login" className="px-4 py-2 text-sm text-slate-300 hover:text-white">Sign in</Link>
        <Link to="/register" className="px-4 py-2 rounded-xl bg-brand-blue text-sm font-semibold hover:bg-blue-600">Create account</Link>
      </div>
    </nav>

    <section className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center py-20 lg:py-28">
      <div>
        <span className="inline-flex items-center gap-2 rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-3 py-1.5 text-xs font-medium text-brand-cyan">
          <ShieldCheck className="w-4 h-4" /> Local decision-support prototype
        </span>
        <h1 className="mt-6 text-4xl sm:text-5xl font-extrabold leading-tight">Credit risk scores with visible model signals.</h1>
        <p className="mt-5 max-w-xl text-base leading-7 text-slate-400">
          Explore a traditional Home Credit Logistic Regression baseline and an experimental behavioral-data model. Each assessment shows its score, stored application context, and signed feature contributions.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/register" className="inline-flex items-center gap-2 rounded-xl bg-brand-blue px-5 py-3 text-sm font-semibold hover:bg-blue-600">Get started <ArrowRight className="w-4 h-4" /></Link>
          <Link to="/login" className="rounded-xl border border-navy-700 px-5 py-3 text-sm font-semibold text-slate-200 hover:border-brand-cyan">Sign in</Link>
        </div>
      </div>

      <div className="grid gap-4">
        <article className="rounded-2xl border border-navy-800 bg-navy-900/80 p-6">
          <FileText className="w-5 h-5 text-brand-cyan" />
          <h2 className="mt-4 font-bold">Traditional features</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">A 12-input model trained on Home Credit data, including income, requested credit, proposed installment, and selected applicant attributes.</p>
        </article>
        <article className="rounded-2xl border border-navy-800 bg-navy-900/80 p-6">
          <Sparkles className="w-5 h-5 text-brand-cyan" />
          <h2 className="mt-4 font-bold">Alternative-data exploration</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">An eight-input behavioral model with only 27 labeled training profiles. Its results are preliminary and not evidence of real-world performance.</p>
        </article>
      </div>
    </section>

    <aside className="max-w-7xl mx-auto rounded-2xl border border-brand-amber/30 bg-brand-amber/5 p-5 text-sm leading-6 text-slate-300">
      CredXAI is not a lender or an automated approval system. Its model estimates and heuristic risk bands are not calibrated or validated for lending decisions. Use synthetic or authorized data only.
    </aside>
  </main>
);

export default LandingPage;
