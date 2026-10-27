const isDevelopment = Boolean(import.meta.env?.DEV);

const write = (level, event, metadata = {}) => {
  if (level === 'debug' && !isDevelopment) return;
  const method = level === 'debug' ? 'debug' : level;
  const sink = typeof console[method] === 'function' ? console[method] : console.log;
  sink.call(console, `[CredXAI] ${event}`, metadata);
};

export const logger = {
  debug: (event, metadata) => write('debug', event, metadata),
  info: (event, metadata) => write('info', event, metadata),
  warn: (event, metadata) => write('warn', event, metadata),
  error: (event, metadata) => write('error', event, metadata),
  errorOnce: (error, event, metadata = {}) => {
    if (error?.__credxaiLogged) return;
    if (error && typeof error === 'object') error.__credxaiLogged = true;
    write('error', event, { ...metadata, errorType: error?.name || 'Error' });
  },
};

export const createCorrelationId = () => {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `cx-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
};

export default logger;
