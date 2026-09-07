import { useState, useEffect } from 'react';

const THEME_STORAGE_KEY = 'fp_theme';
const DEFAULT_THEME = 'dim';

export function useTheme() {
  const [theme, setTheme] = useState<string>(() => {
    return localStorage.getItem(THEME_STORAGE_KEY) || DEFAULT_THEME;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dim' ? 'nord' : 'dim'));
  };

  return {
    theme,
    isDark: theme === 'dim',
    toggleTheme,
    setTheme,
  };
}
