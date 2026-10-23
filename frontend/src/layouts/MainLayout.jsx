import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  FileText, 
  History, 
  ShieldCheck, 
  LogOut, 
  User as UserIcon, 
  Menu, 
  X, 
  Cpu
} from 'lucide-react';

const MainLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'New application', path: '/dashboard', icon: FileText },
    { name: 'My Applications', path: '/history', icon: History },
    { name: 'Account Profile', path: '/profile', icon: UserIcon },
  ];

  const getPageTitle = (pathname) => {
    if (pathname.includes('/assess/traditional')) return 'Traditional Credit Risk Assessment';
    if (pathname.includes('/assess/alternative')) return 'Alternative Data Risk Assessment';
    if (pathname.includes('/history')) return 'My Applications';
    if (pathname.includes('/profile')) return 'Account & Security Profile';
    return 'Applicant Dashboard';
  };

  return (
    <div className="flex h-screen bg-navy-950 text-slate-100 overflow-hidden font-sans">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-72 bg-navy-900 border-r border-navy-800/80 p-5 select-none shadow-xl">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-3 mb-6">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-blue to-brand-cyan shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-brand-cyan">
              CredX<span className="text-brand-cyan">AI</span>
            </div>
            <div className="text-[11px] font-medium text-slate-400 tracking-wider uppercase">
              Explainable Risk Engine
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
              Applicant Portal
        </div>
        <nav className="flex-1 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`group flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-brand-blue/30 to-brand-cyan/10 text-white border border-brand-cyan/30 shadow-md shadow-brand-blue/10'
                    : 'text-slate-400 hover:text-white hover:bg-navy-850/80 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-brand-cyan' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                    isActive 
                      ? 'bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/30' 
                      : 'bg-navy-800 text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User Card & Logout */}
        <div className="pt-4 border-t border-navy-800/80 flex items-center justify-between">
          <NavLink 
            to="/profile"
            className="flex items-center gap-3 overflow-hidden group hover:opacity-90 transition-opacity"
            title="View Account Profile"
          >
            <div className="w-9 h-9 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center text-brand-cyan font-bold text-sm group-hover:border-brand-cyan/50">
              {user?.fullName ? user.fullName.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="overflow-hidden">
              <div className="text-sm font-semibold text-white truncate group-hover:text-brand-cyan transition-colors">
                {user?.fullName || 'Risk Analyst'}
              </div>
              <div className="text-xs text-slate-400 truncate">
                {user?.email || 'applicant@example.com'}
              </div>
            </div>
          </NavLink>
          <button
            onClick={handleLogout}
            title="Log Out"
            className="p-2 text-slate-400 hover:text-brand-rose hover:bg-navy-800 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-navy-950">
        {/* Top Header */}
        <header className="h-16 flex items-center justify-between px-6 bg-navy-900/60 backdrop-blur-md border-b border-navy-800/80 z-20">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-navy-800"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <span className="font-semibold text-white tracking-tight">
                {getPageTitle(location.pathname)}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-navy-850 border border-navy-800 text-xs text-slate-300">
              <ShieldCheck className="w-4 h-4 text-brand-cyan" />
              <span>Signed in as <strong className="text-white">{user?.fullName || 'Risk Analyst'}</strong></span>
              <span className="text-slate-600">|</span>
              <span className="text-slate-400 font-mono text-[11px]">UID: #{user?.id}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-navy-850 hover:bg-brand-rose/20 text-slate-300 hover:text-brand-rose border border-navy-800 hover:border-brand-rose/30 text-xs font-medium transition-all"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-0 top-16 bg-navy-950/95 backdrop-blur-xl z-50 p-6 flex flex-col justify-between border-t border-navy-800">
            <div className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center justify-between px-4 py-3 rounded-xl text-base font-medium ${
                      isActive
                        ? 'bg-brand-blue/20 text-white border border-brand-cyan/40'
                        : 'text-slate-300 hover:bg-navy-900'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="w-5 h-5 text-brand-cyan" />
                      <span>{item.name}</span>
                    </div>
                  </NavLink>
                );
              })}
            </div>
            <div className="pt-6 border-t border-navy-800 flex items-center justify-between">
              <div className="text-sm">
                <div className="font-semibold text-white">{user?.fullName}</div>
                <div className="text-xs text-slate-400">{user?.email}</div>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-xl bg-brand-rose/20 text-brand-rose border border-brand-rose/30 text-sm font-medium flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        )}

        {/* Page Content Body */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-navy-900/40 via-navy-950 to-navy-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
