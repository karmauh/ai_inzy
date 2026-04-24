import React, { useState } from 'react';
import { translations } from '../utils/translations';
import LanguageContext from './LanguageContext';

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('pl');

  const t = (key) => {
    if (!translations || !language) return key;
    const keys = key.split('.');
    let value = translations[language];
    if (!value) return key;
    
    for (const k of keys) {
      if (!value) break;
      value = value[k];
    }
    return value || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
