import React from 'react';
import { ShoppingBag, Heart, User, Search, Menu, X, Tag } from 'lucide-react';

interface HeaderProps {
  cartCount: number;
  wishlistCount: number;
  currentCategory: string;
  setCategory: (cat: string) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onNavigate: (view: string) => void;
  isLoggedIn: boolean;
  userEmail?: string;
  onLogout: () => void;
}

export default function Header({
  cartCount,
  wishlistCount,
  currentCategory,
  setCategory,
  searchQuery,
  setSearchQuery,
  onNavigate,
  isLoggedIn,
  userEmail,
  onLogout
}: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-rose-100 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo & Mobile Menu Toggle */}
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 -ml-2 text-brand-dark hover:text-brand-pink lg:hidden focus:outline-hidden"
              aria-label="Toggle Menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            
            <div 
              onClick={() => {
                setCategory('All');
                onNavigate('home');
              }}
              className="flex items-center gap-2 cursor-pointer select-none"
            >
              <div className="w-10 h-10 rounded-full bg-brand-pink flex items-center justify-center text-white shadow-md transform hover:scale-105 transition-transform">
                <span className="font-display font-bold text-xl">H</span>
              </div>
              <div className="flex flex-col">
                <span className="font-display font-bold text-lg leading-tight tracking-tight text-brand-pink">
                  HYPEHAVEN<span className="text-brand-gold">HUB</span>
                </span>
                <span className="text-[9px] font-mono tracking-widest text-gray-400 uppercase leading-none">
                  Only Jhumka Box Sets
                </span>
              </div>
            </div>
          </div>

          {/* Desktop Navigation Category Links */}
          <nav className="hidden lg:flex space-x-8">
            <button
              onClick={() => {
                setCategory('All');
                onNavigate('home');
              }}
              className={`font-display text-sm font-semibold tracking-wide transition-colors ${
                currentCategory === 'All' ? 'text-brand-pink border-b-2 border-brand-pink pb-1' : 'text-gray-600 hover:text-brand-pink'
              }`}
            >
              All Box Sets
            </button>
            <button
              onClick={() => {
                setCategory('12 Piece Jhumka Box Set');
                onNavigate('home');
              }}
              className={`font-display text-sm font-semibold tracking-wide transition-colors ${
                currentCategory === '12 Piece Jhumka Box Set' ? 'text-brand-pink border-b-2 border-brand-pink pb-1' : 'text-gray-600 hover:text-brand-pink'
              }`}
            >
              12 Piece Box Set
            </button>
            <button
              onClick={() => {
                setCategory('16 Piece Jhumka Box Set');
                onNavigate('home');
              }}
              className={`font-display text-sm font-semibold tracking-wide transition-colors ${
                currentCategory === '16 Piece Jhumka Box Set' ? 'text-brand-pink border-b-2 border-brand-pink pb-1' : 'text-gray-600 hover:text-brand-pink'
              }`}
            >
              16 Piece Box Set
            </button>
            <button
              onClick={() => {
                setCategory('Offers');
                onNavigate('home');
              }}
              className={`font-display text-sm font-semibold tracking-wide flex items-center gap-1 transition-colors ${
                currentCategory === 'Offers' ? 'text-brand-pink border-b-2 border-brand-pink pb-1' : 'text-rose-500 hover:text-brand-pink'
              }`}
            >
              <Tag size={14} />
              Offers
            </button>
          </nav>

          {/* Right Icons with Search Bar */}
          <div className="flex items-center gap-4">
            
            {/* Live Search */}
            <div className="relative hidden md:block max-w-xs">
              <input
                type="text"
                placeholder="Search Jhumka Boxes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-48 lg:w-60 pl-9 pr-4 py-2 text-xs rounded-full bg-rose-50 border border-rose-100 text-brand-dark placeholder-gray-400 focus:outline-hidden focus:ring-2 focus:ring-brand-pink-light focus:bg-white transition-all"
              />
              <Search className="absolute left-3 top-2.5 text-gray-400" size={14} />
            </div>

            {/* Wishlist Icon */}
            <button 
              onClick={() => onNavigate('wishlist')}
              className="p-2 text-gray-600 hover:text-brand-pink relative rounded-full hover:bg-rose-50 transition-colors"
              aria-label="Wishlist"
            >
              <Heart size={20} className={wishlistCount > 0 ? 'fill-brand-pink text-brand-pink' : ''} />
              {wishlistCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-brand-pink text-[10px] font-bold text-white shadow-xs">
                  {wishlistCount}
                </span>
              )}
            </button>

            {/* Shopping Bag Icon */}
            <button 
              onClick={() => onNavigate('cart')}
              className="p-2 text-gray-600 hover:text-brand-pink relative rounded-full hover:bg-rose-50 transition-colors"
              aria-label="Shopping Cart"
            >
              <ShoppingBag size={20} />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-brand-pink text-[10px] font-bold text-white shadow-xs">
                  {cartCount}
                </span>
              )}
            </button>

            {/* Account Icon / Active User Indicator */}
            <div className="h-6 w-px bg-rose-100"></div>
            {isLoggedIn ? (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onNavigate('dashboard')}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-full bg-rose-50 border border-rose-100 text-brand-pink hover:bg-brand-pink hover:text-white transition-all"
                >
                  <User size={14} />
                  <span className="max-w-[100px] truncate hidden sm:inline">{userEmail}</span>
                </button>
                <button
                  onClick={onLogout}
                  className="text-xs text-gray-400 hover:text-red-500 transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={() => onNavigate('login')}
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-full bg-brand-pink text-white hover:bg-brand-pink-light shadow-sm transition-all"
              >
                <User size={14} />
                Login
              </button>
            )}

          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-rose-100 bg-white shadow-md animate-slide-down">
          <div className="px-4 pt-3 pb-6 space-y-3">
            {/* Mobile Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search jhumka sets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs rounded-full bg-rose-50 border border-rose-100 text-brand-dark placeholder-gray-400 focus:outline-hidden"
              />
              <Search className="absolute left-3 top-2.5 text-gray-400" size={14} />
            </div>

            <div className="h-px bg-rose-100 my-2"></div>

            <button
              onClick={() => {
                setCategory('All');
                onNavigate('home');
                setMobileMenuOpen(false);
              }}
              className={`block w-full text-left px-3 py-2 text-sm font-semibold rounded-lg ${
                currentCategory === 'All' ? 'bg-rose-50 text-brand-pink' : 'text-gray-700 hover:bg-rose-50 hover:text-brand-pink'
              }`}
            >
              All Box Sets
            </button>
            <button
              onClick={() => {
                setCategory('12 Piece Jhumka Box Set');
                onNavigate('home');
                setMobileMenuOpen(false);
              }}
              className={`block w-full text-left px-3 py-2 text-sm font-semibold rounded-lg ${
                currentCategory === '12 Piece Jhumka Box Set' ? 'bg-rose-50 text-brand-pink' : 'text-gray-700 hover:bg-rose-50 hover:text-brand-pink'
              }`}
            >
              12 Piece Box Set
            </button>
            <button
              onClick={() => {
                setCategory('16 Piece Jhumka Box Set');
                onNavigate('home');
                setMobileMenuOpen(false);
              }}
              className={`block w-full text-left px-3 py-2 text-sm font-semibold rounded-lg ${
                currentCategory === '16 Piece Jhumka Box Set' ? 'bg-rose-50 text-brand-pink' : 'text-gray-700 hover:bg-rose-50 hover:text-brand-pink'
              }`}
            >
              16 Piece Box Set
            </button>
            <button
              onClick={() => {
                setCategory('Offers');
                onNavigate('home');
                setMobileMenuOpen(false);
              }}
              className={`block w-full text-left px-3 py-2 text-sm font-semibold rounded-lg text-rose-500 ${
                currentCategory === 'Offers' ? 'bg-rose-50 text-brand-pink font-bold' : 'hover:bg-rose-50 hover:text-brand-pink'
              }`}
            >
              Offers & Promotions
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
