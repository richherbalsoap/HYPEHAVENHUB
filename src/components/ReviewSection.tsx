import React from 'react';
import { Review } from '../types';
import { Star, MessageSquarePlus, Check, User } from 'lucide-react';

interface ReviewSectionProps {
  productId: string;
  reviews: Review[];
  onAddReview: (reviewData: { rating: number; title: string; body: string; userEmail: string }) => void;
  userEmail?: string;
}

export default function ReviewSection({
  productId,
  reviews,
  onAddReview,
  userEmail
}: ReviewSectionProps) {
  const [showForm, setShowForm] = React.useState(false);
  const [rating, setRating] = React.useState(5);
  const [hoverRating, setHoverRating] = React.useState<number | null>(null);
  const [title, setTitle] = React.useState('');
  const [body, setBody] = React.useState('');
  const [successMsg, setSuccessMsg] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !body) {
      alert("Please fill in the review title and body");
      return;
    }
    
    onAddReview({
      rating,
      title,
      body,
      userEmail: userEmail || 'anonymous@hypehaven.com'
    });

    setSuccessMsg("Thank you! Your feedback has been verified and published instantly.");
    setTitle('');
    setBody('');
    setRating(5);
    setShowForm(false);
    setTimeout(() => setSuccessMsg(''), 4000);
  };

  // Helper to draw stars
  const renderStars = (count: number, size = 14) => {
    return (
      <div className="flex gap-0.5 text-brand-gold">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star 
            key={i} 
            size={size} 
            className={i < count ? 'fill-brand-gold text-brand-gold' : 'text-gray-200'} 
          />
        ))}
      </div>
    );
  };

  const avgRating = reviews.length > 0 
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : '0.0';

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-rose-100">
        <div>
          <h3 className="text-base font-bold text-neutral-800">Verified Customer Reviews</h3>
          <div className="flex items-center gap-2 mt-1">
            {renderStars(Math.round(parseFloat(avgRating)), 16)}
            <span className="text-xs font-bold text-neutral-800">{avgRating} out of 5</span>
            <span className="text-[10px] text-gray-400 font-mono">({reviews.length} total reviews)</span>
          </div>
        </div>

        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full border border-brand-pink text-brand-pink hover:bg-brand-pink hover:text-white transition-colors"
          >
            <MessageSquarePlus size={14} /> Write Review
          </button>
        )}
      </div>

      {successMsg && (
        <div className="p-3 bg-emerald-50 text-emerald-800 rounded-xl text-xs font-semibold flex items-center gap-2">
          <Check size={14} />
          {successMsg}
        </div>
      )}

      {/* Review Submission Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="p-5 rounded-2xl bg-rose-50/10 border border-rose-100 space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-800">Review this Jhumka Set</h4>
          
          {/* Star selector */}
          <div className="space-y-1">
            <label className="block text-[11px] font-semibold text-gray-500">Your Rating *</label>
            <div className="flex gap-1.5">
              {Array.from({ length: 5 }).map((_, i) => {
                const starVal = i + 1;
                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setRating(starVal)}
                    onMouseEnter={() => setHoverRating(starVal)}
                    onMouseLeave={() => setHoverRating(null)}
                    className="text-brand-gold focus:outline-hidden transform hover:scale-110 transition-transform"
                  >
                    <Star
                      size={24}
                      className={starVal <= (hoverRating ?? rating) ? 'fill-brand-gold text-brand-gold' : 'text-gray-200'}
                    />
                  </button>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-[11px] font-semibold text-gray-500 mb-1">Headline / Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="E.g., Simply beautiful, loved the packaging!"
                className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-[11px] font-semibold text-gray-500 mb-1">Review Body *</label>
              <textarea
                required
                rows={4}
                value={body}
                onChange={e => setBody(e.target.value)}
                placeholder="Describe your styling experience. Are the designs unique? How is the weight of the earrings?"
                className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
              />
            </div>
          </div>

          <div className="flex gap-2 justify-end pt-2">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-1.5 text-xs font-semibold text-gray-500 rounded-full border border-gray-200 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-1.5 text-xs font-semibold text-white rounded-full bg-brand-pink hover:bg-brand-pink-light shadow-xs"
            >
              Submit Review
            </button>
          </div>
        </form>
      )}

      {/* Reviews List */}
      <div className="space-y-4">
        {reviews.length === 0 ? (
          <p className="text-xs text-gray-400 italic py-4">No reviews yet for this product. Be the first to share your thoughts!</p>
        ) : (
          reviews.map((rev) => (
            <div key={rev.id} className="p-4 rounded-xl border border-rose-50/50 bg-white shadow-xs space-y-2">
              <div className="flex justify-between items-start gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-rose-50 border border-rose-100 text-brand-pink flex items-center justify-center">
                    <User size={12} />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-neutral-800">{rev.userEmail}</span>
                    <span className="text-[9px] font-mono text-gray-400 block">{new Date(rev.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>
                {rev.isVerifiedPurchase && (
                  <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md flex items-center gap-1 shrink-0">
                    <Check size={10} /> Verified Buyer
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                {renderStars(rev.rating, 12)}
                <span className="text-xs font-bold text-neutral-800 font-display leading-none">{rev.title}</span>
              </div>

              <p className="text-xs text-gray-600 leading-relaxed font-sans">{rev.body}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
