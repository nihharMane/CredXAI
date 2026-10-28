import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, Mail, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!email.trim() || !password) {
      setFormError('Please enter both your email and password.');
      return;
    }

    const result = await login(email, password);
    if (result.success) {
      navigate(result.user?.role === 'ADMIN' ? '/admin' : '/dashboard');
    } else {
      setFormError(result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-navy-950 p-4 sm:p-6 lg:p-8 font-sans">
      <div className="w-full max-w-md">
        {/* Logo Card */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-blue to-brand-cyan shadow-xl shadow-cyan-500/20 mb-4">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            CredX<span className="text-brand-cyan">AI</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Explainable AI Credit Risk Assessment System
          </p>
        </div>

        {/* Login Box */}
        <div className="bg-navy-900/80 backdrop-blur-xl border border-navy-800 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-blue via-brand-cyan to-brand-emerald"></div>

          <h2 className="text-xl font-bold text-white mb-2">Welcome Back</h2>
          <p className="text-xs text-slate-400 mb-6">
            Authenticate to access credit risk modeling and explainable AI insights.
          </p>

          {formError && (
            <div className="mb-5 p-3.5 rounded-xl bg-brand-rose/10 border border-brand-rose/30 text-brand-rose flex items-start gap-2.5 text-xs animate-shake">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{formError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@credxai.internal"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-navy-950/80 border border-navy-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-cyan focus:ring-1 focus:ring-brand-cyan transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 rounded-xl bg-gradient-to-r from-brand-blue to-cyan-500 hover:from-blue-600 hover:to-cyan-400 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-navy-800 text-center">
            <p className="text-xs text-slate-400">
              Don't have an analyst account?{' '}
              <Link to="/register" className="text-brand-cyan font-semibold hover:underline">
                Register here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
