import { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  Menu,
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

  const navLinks = [
    { to: '/', label: 'Live Scores', icon: Activity },
    { to: '/results', label: 'Standings & Results', icon: Trophy },
    { to: '/assignments', label: 'Assignments', icon: Users },
    { to: '/about', label: 'About & Rules', icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-40 bg-base-100/90 backdrop-blur-md border-b border-base-content/10">
      <div className="navbar max-w-7xl mx-auto px-4 sm:px-6">
        {/* Left: Mobile hamburger & Brand */}
        <div className="navbar-start flex items-center gap-2">
          {/* Mobile hamburger */}
          <div className="dropdown lg:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="btn btn-ghost btn-circle btn-sm"
              aria-label="Toggle menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            {isMobileMenuOpen && (
              <ul
                tabIndex={0}
                className="menu dropdown-content mt-3 z-50 p-2 shadow-xl bg-base-200 rounded-box w-60 border border-base-content/10"
              >
                {navLinks.map(({ to, label, icon: Icon }) => (
                  <li key={to}>
                    <NavLink
                      to={to}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center gap-3 py-2.5 ${
                          isActive ? 'active font-bold bg-primary text-primary-content' : ''
                        }`
                      }
                    >
                      <Icon className="h-4 w-4" />
                      {label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Brand Logo & Name */}
          <Link
            to="/"
            className="btn btn-ghost px-2 normal-case flex items-center gap-2 hover:bg-transparent"
          >
            <div className="flex flex-col text-left">
              <span className="font-extrabold tracking-wider text-base sm:text-lg text-primary">
                UCMFPTDCYAMBCMYR
              </span>
              <span className="hidden sm:inline-block text-[10px] opacity-60 tracking-tight -mt-1 font-medium truncate max-w-xs">
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
        <div className="navbar-end flex items-center gap-1.5 sm:gap-2.5">
          {/* Season Selector */}
          <SeasonSelector />

          {/* Chat Button */}
          <button
            onClick={toggleChat}
            className="btn btn-ghost btn-circle btn-sm md:btn-md relative"
            aria-label="Open family chat"
            title="Family Chat"
          >
            <MessageSquare className="h-5 w-5" />
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
                className="btn btn-sm btn-ghost gap-2 pl-2 pr-3 bg-base-200/80 hover:bg-base-200 border border-base-content/10 rounded-full"
              >
                {auth.current_team?.logo_url ? (
                  <img
                    src={`/static/${auth.current_team.logo_url}`}
                    alt={auth.current_team.name}
                    className="w-5 h-5 object-contain"
                  />
                ) : (
                  <div className="w-5 h-5 rounded-full bg-primary text-primary-content flex items-center justify-center text-[10px] font-bold">
                    {auth.member.first_name[0]}
                  </div>
                )}
                <span className="text-xs font-semibold max-w-[90px] sm:max-w-none truncate">
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
              className="btn btn-xs sm:btn-sm btn-primary gap-1 font-semibold shadow-xs"
            >
              <UserCheck className="h-3.5 w-3.5" />
              <span>Claim</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
