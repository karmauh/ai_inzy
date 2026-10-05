import React from 'react';
import Dashboard from './pages/Dashboard';
import { LanguageProvider } from './context/LanguageProvider';
import { useLanguage } from './context/LanguageContext';

const AppContent = () => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <div className="min-h-screen bg-neutral-900 text-neutral-100 font-inter">
       {/* Nagłówek aplikacji */}
       <header className="bg-neutral-800 border-b border-neutral-700 p-4 shadow-md flex justify-between items-center sticky top-0 z-50">
          <div className="flex items-center space-x-3">
             <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">S</span>
             </div>
             <h1 className="text-xl font-bold tracking-tight text-white">
                {t('appTitle')}
             </h1>
          </div>

          <div className="relative">
             <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="appearance-none bg-neutral-700 border border-neutral-600 text-neutral-200 py-1 pl-3 pr-8 rounded focus:outline-none focus:border-primary-400 cursor-pointer text-sm"
             >
                <option value="pl">Polski</option>
                <option value="en">English</option>
             </select>
             <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-neutral-400">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                   <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                </svg>
             </div>
          </div>
       </header>

      <div className="container mx-auto p-4 md:p-8">
        <Dashboard />
      </div>
    </div>
  );
};

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-white bg-red-900 min-h-screen">
          {/* ErrorBoundary działa poza LanguageProvider, stąd komunikat w obu językach */}
          <h1 className="text-2xl font-bold mb-4">Coś poszło nie tak / Something went wrong.</h1>
          <pre className="bg-neutral-900 p-4 rounded overflow-auto text-neutral-300">
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </ErrorBoundary>
  )
}

export default App
