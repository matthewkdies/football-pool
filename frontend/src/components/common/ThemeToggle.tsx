import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

export function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="btn btn-ghost btn-circle btn-xs sm:btn-sm"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? (
        <Sun className="h-4 w-4 sm:h-5 sm:w-5 text-warning transition-transform hover:rotate-45" />
      ) : (
        <Moon className="h-4 w-4 sm:h-5 sm:w-5 text-primary transition-transform hover:-rotate-12" />
      )}
    </button>
  );
}
