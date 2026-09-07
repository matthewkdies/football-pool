import { useState, useEffect } from 'react';

const THEME_STORAGE_KEY = 'fp_theme';
const DEFAULT_THEME = 'dim';

export function useTheme() {
  const [theme, setTheme] = useState<string>(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'dark' || stored === 'dim') return 'dim';
    if (stored === 'light' || stored === 'nord') return 'nord';
    return DEFAULT_THEME;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dim' || prev === 'dark' ? 'nord' : 'dim'));
  };

  const isDark = theme === 'dim' || theme === 'dark';

  return {
    theme,
    isDark,
    toggleTheme,
    setTheme,
  };
}
