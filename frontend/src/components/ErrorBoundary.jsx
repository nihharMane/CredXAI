import React from 'react';
import { logger } from '../utils/logger';

class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    logger.error('ui.render.failed', { errorType: error?.name || 'Error' });
  }

  render() {
    if (this.state.hasError) {
      return <main role="alert" className="flex min-h-screen items-center justify-center bg-navy-950 px-5 text-center text-white"><div className="max-w-md rounded-2xl border border-navy-800 bg-navy-900 p-7"><h1 className="text-xl font-bold">This page could not be displayed</h1><p className="mt-2 text-sm text-slate-400">Reload the page to continue. No application details were included in the error message.</p><button type="button" onClick={() => window.location.reload()} className="mt-5 rounded-xl bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-600">Reload page</button></div></main>;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
