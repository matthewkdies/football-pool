import { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  Menu,
  X,
  MessageSquare,
  UserCheck,
  LogOut,
  Trophy,
  Users,
  Activity,
  BookOpen,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';
import { SeasonSelector } from './SeasonSelector';
import { ThemeToggle } from '../common/ThemeToggle';

export function Navbar() {
  const { auth, openClaimModal, unclaim } = useAuth();
  const { toggleChat, unreadCount } = useChat();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const navLinks = [
    { to: '/', label: 'Live Scores', icon: Activity },
    { to: '/results', label: 'Standings & Results', icon: Trophy },
    { to: '/assignments', label: 'Assignments', icon: Users },
    { to: '/about', label: 'About & Rules', icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-40 bg-base-100/90 backdrop-blur-md border-b border-base-content/10">
      <div className="navbar max-w-7xl mx-auto px-2 sm:px-6">
        {/* Left: Mobile hamburger & Brand */}
        <div className="navbar-start flex items-center gap-1 sm:gap-2">
          {/* Mobile hamburger */}
          <div className="relative lg:hidden">
            <button
              type="button"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="btn btn-ghost btn-circle btn-sm"
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            {isMobileMenuOpen && (
              <>
                {/* Backdrop overlay to close on tap outside */}
                <div
                  className="fixed inset-0 z-40 bg-black/20 backdrop-blur-xs"
                  onClick={() => setIsMobileMenuOpen(false)}
                  aria-hidden="true"
                />

                {/* Mobile Navigation Popover */}
                <div className="absolute left-0 top-full mt-2 z-50 p-2 shadow-2xl bg-base-200 rounded-2xl w-60 border border-base-content/10">
                  <ul className="menu menu-vertical p-0 gap-1">
                    {navLinks.map(({ to, label, icon: Icon }) => (
                      <li key={to}>
                        <NavLink
                          to={to}
                          onClick={() => setIsMobileMenuOpen(false)}
                          className={({ isActive }) =>
                            `flex items-center gap-3 py-2.5 px-3 rounded-lg text-sm font-medium ${
                              isActive ? 'active font-bold bg-primary text-primary-content' : 'hover:bg-base-300'
                            }`
                          }
                        >
                          <Icon className="h-4 w-4 shrink-0" />
                          <span>{label}</span>
                        </NavLink>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>

          {/* Brand Logo & Name */}
          <Link
            to="/"
            className="btn btn-ghost px-1 sm:px-2 normal-case flex items-center gap-2 hover:bg-transparent"
            aria-label="Home"
          >
            <div className="p-1 sm:p-1.5 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
              <Trophy className="h-5 w-5" />
            </div>
            <div className="hidden sm:flex flex-col text-left">
              <span className="font-extrabold tracking-wider text-base sm:text-lg text-primary leading-tight">
                UCMFPTDCYAMBCMYR
              </span>
              <span className="hidden md:inline-block text-[10px] opacity-60 tracking-tight font-medium truncate max-w-xs">
                Uncle Charles Memorial Football Pool
              </span>
            </div>
          </Link>
        </div>

        {/* Center: Desktop Navigation */}
        <div className="navbar-center hidden lg:flex">
          <ul className="menu menu-horizontal px-1 gap-1">
            {navLinks.map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-content font-bold shadow-xs'
                        : 'hover:bg-base-200'
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>

        {/* Right: Actions (Season, Chat, User/Claim, Theme) */}
        <div className="navbar-end flex items-center gap-1 sm:gap-2">
          {/* Season Selector */}
          <SeasonSelector />

          {/* Chat Button */}
          <button
            onClick={toggleChat}
            className="btn btn-ghost btn-circle btn-xs sm:btn-sm relative"
            aria-label="Open family chat"
            title="Family Chat"
          >
            <MessageSquare className="h-4 w-4 sm:h-5 sm:w-5" />
            {unreadCount > 0 && (
              <span className="badge badge-primary badge-xs absolute -top-0.5 -right-0.5 animate-pulse font-bold text-[10px]">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Claim or Claimed Profile Dropdown */}
          {auth?.claimed && auth.member ? (
            <div className="dropdown dropdown-end">
              <div
                tabIndex={0}
                role="button"
                className="btn btn-xs sm:btn-sm btn-ghost gap-1 sm:gap-2 p-1 sm:pl-2 sm:pr-3 bg-base-200/80 hover:bg-base-200 border border-base-content/10 rounded-full"
              >
                {auth.current_team?.logo_url ? (
                  <img
                    src={`/static/${auth.current_team.logo_url}`}
                    alt={auth.current_team.name}
                    className="w-4 h-4 sm:w-5 sm:h-5 object-contain"
                  />
                ) : (
                  <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-primary text-primary-content flex items-center justify-center text-[9px] sm:text-[10px] font-bold">
                    {auth.member.first_name[0]}
                  </div>
                )}
                <span className="text-xs font-semibold hidden sm:inline max-w-[90px] md:max-w-none truncate">
                  {auth.member.first_name}
                </span>
              </div>
              <ul
                tabIndex={0}
                className="dropdown-content menu z-50 mt-2 p-2 shadow-xl bg-base-200 rounded-box w-56 border border-base-content/10 text-xs"
              >
                <li className="menu-title px-3 py-2 border-b border-base-content/10">
                  <div className="font-bold text-sm text-base-content">
                    {auth.member.full_name}
                  </div>
                  {auth.current_team && (
                    <div className="text-primary font-medium mt-0.5">
                      Team: {auth.current_team.full_name}
                    </div>
                  )}
                </li>
                <li className="mt-1">
                  <button onClick={openClaimModal} className="py-2">
                    <UserCheck className="h-4 w-4" /> Switch Profile
                  </button>
                </li>
                <li>
                  <button onClick={() => unclaim()} className="text-error py-2">
                    <LogOut className="h-4 w-4" /> Unclaim Identity
                  </button>
                </li>
              </ul>
            </div>
          ) : (
            <button
              onClick={openClaimModal}
              className="btn btn-xs sm:btn-sm btn-primary gap-1 font-semibold px-2 sm:px-3 shadow-xs"
            >
              <UserCheck className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
              <span>Claim</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
