import React from 'react';

export default function AnnouncementBar() {
  const announcements = [
    "WILL YOU BE MY CUSTOMER 😍 IF YES THEN SCROLL DOWN AND BUY MY PRODUCT 🛍️",
    "✨ 100% Authentic Handcrafted Indian Jhumkas ✨",
    "🎁 Free Premium Gifting Box with Every Order! 🎁"
  ];

  const [activeIdx, setActiveIdx] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setActiveIdx((prev) => (prev + 1) % announcements.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-brand-pink text-white font-medium text-xs md:text-sm py-2 px-4 shadow-sm select-none">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-2">
        <div className="flex-1 text-center font-display tracking-wide animate-fade-in transition-opacity duration-500">
          {announcements[activeIdx]}
        </div>
        
        {/* Secondary Marquee row */}
        <div className="w-full bg-[#da3b7b] py-1 px-2 rounded-md overflow-hidden relative max-w-lg hidden md:block">
          <div className="animate-marquee whitespace-nowrap flex gap-8 text-xs font-mono tracking-wider">
            <span>FREE Shipping on orders above ₹499 ✦ Use Code <b>JHUMKA10</b> for 10% OFF ✦ Traditional Oxidized Silver ✦ Royal Gold Collections ✦ </span>
            <span>FREE Shipping on orders above ₹499 ✦ Use Code <b>JHUMKA10</b> for 10% OFF ✦ Traditional Oxidized Silver ✦ Royal Gold Collections ✦ </span>
          </div>
        </div>
      </div>
    </div>
  );
}
