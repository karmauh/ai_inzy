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

  // Atrybut lang ustawiany od razu przy zmianie języka (nie dopiero w useEffect po renderze), bo formatowanie
  // liczb (np. w ModelBenchmark) odczytuje go podczas renderu – inaczej po przełączeniu zostałby stary format
  const changeLanguage = (next) => {
    document.documentElement.lang = next;
    setLanguage(next);
  };

  const t = (key) => translate(language, key);

  return (
    <LanguageContext.Provider value={{ language, setLanguage: changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
