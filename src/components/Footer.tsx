import React from 'react';
import { Mail, Phone, MapPin, Sparkles, ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-neutral-900 text-neutral-300 pt-16 pb-8 border-t border-rose-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          
          {/* Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-brand-pink flex items-center justify-center text-white font-bold text-base">H</div>
              <span className="font-display font-bold text-lg text-white">
                HYPEHAVEN<span className="text-brand-gold">HUB</span>
              </span>
            </div>
            <p className="text-xs text-neutral-400 leading-relaxed font-sans">
              E-Commerce boutique specialized exclusively in curated, handcrafted 12 and 16-piece Jhumka box sets. Designed for resellers, boutique stores, gifting, and festive styling.
            </p>
            <div className="flex items-center gap-2 text-xs text-brand-pink font-semibold">
              <Sparkles size={14} />
              <span>Only Jhumka Box Sets</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-display font-semibold text-white tracking-wider uppercase mb-4">Shopping & Support</h4>
            <ul className="space-y-2 text-xs text-neutral-400">
              <li><a href="#" className="hover:text-brand-pink transition-colors">All Jhumka Box Sets</a></li>
              <li><a href="#" className="hover:text-brand-pink transition-colors">12 Piece Collection</a></li>
              <li><a href="#" className="hover:text-brand-pink transition-colors">16 Piece Premium Set</a></li>
              <li><a href="#" className="hover:text-brand-pink transition-colors">Return Policy & Exchange</a></li>
              <li><a href="#" className="hover:text-brand-pink transition-colors">Merchant Reseller Program</a></li>
            </ul>
          </div>

          {/* Contact Details */}
          <div className="space-y-3">
            <h4 className="text-sm font-display font-semibold text-white tracking-wider uppercase mb-4">Contact Details</h4>
            <div className="flex items-start gap-3 text-xs text-neutral-400 leading-relaxed">
              <MapPin size={16} className="text-brand-pink shrink-0 mt-0.5" />
              <span>Glamour Jewels Corp, Hype Haven Hub, Sector 62, Noida, Uttar Pradesh, India - 201301</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-neutral-400">
              <Phone size={16} className="text-brand-pink shrink-0" />
              <span>+91 98765 43210 (Mon - Sat, 10 AM - 7 PM)</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-neutral-400">
              <Mail size={16} className="text-brand-pink shrink-0" />
              <span>support@hypehaven.com</span>
            </div>
          </div>

          {/* Security & Badges */}
          <div className="space-y-4">
            <h4 className="text-sm font-display font-semibold text-white tracking-wider uppercase mb-4">Trust & Safety</h4>
            <div className="p-4 rounded-xl bg-neutral-800 border border-neutral-700 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-white">
                <ShieldCheck className="text-brand-gold shrink-0" size={16} />
                <span>100% Safe Payments</span>
              </div>
              <p className="text-[10px] text-neutral-400 leading-relaxed">
                Every transaction is encrypted and secured. We accept UPI, NetBanking, Visa, Mastercard, Wallets, and cash on delivery.
              </p>
              {/* Payment Methods Graphic */}
              <div className="flex gap-2 flex-wrap pt-1 opacity-70">
                <span className="bg-neutral-700 text-white font-mono text-[9px] px-2 py-0.5 rounded-sm">UPI</span>
                <span className="bg-neutral-700 text-white font-mono text-[9px] px-2 py-0.5 rounded-sm">CARD</span>
                <span className="bg-neutral-700 text-white font-mono text-[9px] px-2 py-0.5 rounded-sm">COD</span>
                <span className="bg-neutral-700 text-white font-mono text-[9px] px-2 py-0.5 rounded-sm">NETBANK</span>
              </div>
            </div>
          </div>

        </div>

        <div className="border-t border-neutral-800 pt-8 mt-12 flex flex-col sm:flex-row justify-between items-center gap-4 text-center">
          <p className="text-xs text-neutral-500">
            &copy; 2026 HYPEHAVENHUB Inc. Handcrafted with traditional pride. All rights reserved.
          </p>
          <div className="flex gap-4 text-xs text-neutral-500">
            <a href="#" className="hover:text-neutral-400">Terms of Use</a>
            <a href="#" className="hover:text-neutral-400">Privacy Policy</a>
            <a href="#" className="hover:text-neutral-400">Reseller License</a>
          </div>
        </div>

      </div>
    </footer>
  );
}
