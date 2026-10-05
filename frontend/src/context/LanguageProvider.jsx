import { useEffect, useState } from 'react';
import { translate, translations } from '../utils/translations';
import LanguageContext from './LanguageContext';

const STORAGE_KEY = 'stockguard.language';

const readStoredLanguage = () => {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored in translations ? stored : 'pl';
  } catch {
    return 'pl';
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(readStoredLanguage);

  useEffect(() => {
    document.documentElement.lang = language;
    try {
      window.localStorage.setItem(STORAGE_KEY, language);
    } catch {
      // Brak dostępu do localStorage (np. tryb prywatny) – język nie zostanie zapamiętany
    }
  }, [language]);

  const t = (key) => translate(language, key);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
