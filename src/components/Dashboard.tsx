import React from 'react';
import { Address, Order, Complaint, Notification } from '../types';
import { ShoppingBag, MapPin, MessageSquare, Bell, Plus, Trash2, Check, Clock, ShieldAlert, ArrowRight, Eye } from 'lucide-react';

interface DashboardProps {
  sessionId: string;
  userEmail: string;
  userPhone?: string;
  addresses: Address[];
  onSaveAddress: (address: Partial<Address>) => void;
  onDeleteAddress: (addressId: string) => void;
}

export default function Dashboard({
  sessionId,
  userEmail,
  userPhone,
  addresses,
  onSaveAddress,
  onDeleteAddress
}: DashboardProps) {
  const [activeTab, setActiveTab] = React.useState<'orders' | 'addresses' | 'complaints' | 'notifications'>('orders');
  const [orders, setOrders] = React.useState<Order[]>([]);
  const [complaints, setComplaints] = React.useState<Complaint[]>([]);
  const [notifications, setNotifications] = React.useState<Notification[]>([
    {
      id: 'notif-1',
      type: 'general',
      title: 'Welcome to Hype Haven Hub! 🎉',
      message: 'Explore our newest Jhumka Box Sets with our exclusive pink theme. Use code JHUMKA10 for 10% off on your checkout.',
      is_read: false,
      created_at: new Date(Date.now() - 1 * 3600 * 1000).toISOString()
    }
  ]);
  
  // Selected order for the live tracking view
  const [selectedOrder, setSelectedOrder] = React.useState<Order | null>(null);

  // Address Form States
  const [isAddingAddress, setIsAddingAddress] = React.useState(false);
  const [editingAddress, setEditingAddress] = React.useState<Address | null>(null);
  const [addressForm, setAddressForm] = React.useState({
    type: 'home' as 'home' | 'work' | 'other',
    full_name: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    pincode: '',
    is_default: false
  });

  // Complaint Form States
  const [complaintType, setComplaintType] = React.useState<'product_quality' | 'delivery' | 'payment' | 'account' | 'website' | 'other'>('product_quality');
  const [complaintSubject, setComplaintSubject] = React.useState('');
  const [complaintDesc, setComplaintDesc] = React.useState('');
  const [complaintPriority, setComplaintPriority] = React.useState<'low' | 'medium' | 'high'>('medium');
  const [complaintStatusMsg, setComplaintStatusMsg] = React.useState('');

  // Load user data on mount
  const fetchOrdersAndComplaints = async () => {
    try {
      // Fetch Orders
      const orderRes = await fetch('/api/orders/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId })
      });
      if (orderRes.ok) {
        const data = await orderRes.json();
        setOrders(data);
        if (data.length > 0 && !selectedOrder) {
          setSelectedOrder(data[0]); // Default to show first order tracking
        }
      }

      // Fetch Complaints
      const compRes = await fetch('/api/complaints/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId })
      });
      if (compRes.ok) {
        const data = await compRes.json();
        setComplaints(data);
      }
    } catch (e) {
      console.error("Error loading dashboard details:", e);
    }
  };

  React.useEffect(() => {
    fetchOrdersAndComplaints();
    // Poll complaints for live simulation updates
    const pollInterval = setInterval(() => {
      fetchOrdersAndComplaints();
    }, 4000);
    return () => clearInterval(pollInterval);
  }, [sessionId]);

  // Handle address submit
  const handleAddressSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!addressForm.full_name || !addressForm.phone || !addressForm.address_line1 || !addressForm.city || !addressForm.state || !addressForm.pincode) {
      alert("Please fill all required address fields");
      return;
    }
    onSaveAddress({
      id: editingAddress?.id,
      ...addressForm
    });
    setIsAddingAddress(false);
    setEditingAddress(null);
    setAddressForm({
      type: 'home',
      full_name: '',
      phone: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      pincode: '',
      is_default: false
    });
  };

  // Start editing address
  const startEditAddress = (addr: Address) => {
    setEditingAddress(addr);
    setAddressForm({
      type: addr.type,
      full_name: addr.full_name,
      phone: addr.phone,
      address_line1: addr.address_line1,
      address_line2: addr.address_line2 || '',
      city: addr.city,
      state: addr.state,
      pincode: addr.pincode,
      is_default: addr.is_default
    });
    setIsAddingAddress(true);
  };

  // Handle Complaint Submission
  const handleComplaintSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintSubject || !complaintDesc) {
      alert("Please provide subject and description of your complaint");
      return;
    }
    try {
      const res = await fetch('/api/complaints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          complaint_type: complaintType,
          subject: complaintSubject,
          description: complaintDesc,
          priority: complaintPriority
        })
      });
      if (res.ok) {
        setComplaintStatusMsg("Your complaint has been submitted successfully! Check list below for updates.");
        setComplaintSubject('');
        setComplaintDesc('');
        fetchOrdersAndComplaints();
        setTimeout(() => setComplaintStatusMsg(''), 5000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-[60vh] font-sans">
      <div className="flex flex-col lg:flex-row gap-8">
        
        {/* Left Sidebar Menu */}
        <div className="w-full lg:w-64 shrink-0 space-y-4">
          <div className="bg-white rounded-2xl border border-rose-100 p-6 shadow-sm">
            <div className="flex items-center gap-3 pb-4 mb-4 border-b border-rose-50">
              <div className="w-12 h-12 rounded-full bg-brand-pink-light/20 text-brand-pink flex items-center justify-center font-bold text-lg">
                {userEmail.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs text-gray-400 font-mono">User Session</span>
                <span className="text-sm font-semibold truncate text-brand-dark">{userEmail}</span>
                {userPhone && <span className="text-[10px] text-gray-500 font-mono">{userPhone}</span>}
              </div>
            </div>

            {/* Nav Menu */}
            <nav className="flex flex-col gap-1">
              <button
                onClick={() => { setActiveTab('orders'); setSelectedOrder(orders[0] || null); }}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  activeTab === 'orders' ? 'bg-brand-pink text-white shadow-xs' : 'text-gray-600 hover:bg-rose-50/50 hover:text-brand-pink'
                }`}
              >
                <ShoppingBag size={16} />
                My Orders & Tracking
              </button>
              <button
                onClick={() => setActiveTab('addresses')}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  activeTab === 'addresses' ? 'bg-brand-pink text-white shadow-xs' : 'text-gray-600 hover:bg-rose-50/50 hover:text-brand-pink'
                }`}
              >
                <MapPin size={16} />
                My Delivery Addresses
              </button>
              <button
                onClick={() => setActiveTab('complaints')}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  activeTab === 'complaints' ? 'bg-brand-pink text-white shadow-xs' : 'text-gray-600 hover:bg-rose-50/50 hover:text-brand-pink'
                }`}
              >
                <MessageSquare size={16} />
                Support & Complaints
              </button>
              <button
                onClick={() => setActiveTab('notifications')}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  activeTab === 'notifications' ? 'bg-brand-pink text-white shadow-xs' : 'text-gray-600 hover:bg-rose-50/50 hover:text-brand-pink'
                }`}
              >
                <Bell size={16} />
                Notifications
              </button>
            </nav>
          </div>
        </div>

        {/* Right Active Tab Content */}
        <div className="flex-1 min-w-0">
          <div className="bg-white rounded-2xl border border-rose-100 p-6 md:p-8 shadow-xs min-h-full">
            
            {/* ORDERS TAB */}
            {activeTab === 'orders' && (
              <div className="space-y-8">
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-brand-pink">My Order History</h2>
                  <p className="text-xs text-gray-500 font-sans mt-1">
                    Manage your orders, view receipts, and monitor real-time shipment dispatch details.
                  </p>
                </div>

                {orders.length === 0 ? (
                  <div className="text-center py-12 border-2 border-dashed border-rose-100 rounded-2xl">
                    <ShoppingBag className="mx-auto text-gray-300 mb-3" size={40} />
                    <p className="text-sm font-semibold text-gray-600">No Orders Placed Yet</p>
                    <p className="text-xs text-gray-400 mt-1">Browse our catalog and buy your first Jhumka Box Set today!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 xl:grid-cols-5 gap-8">
                    
                    {/* Orders List */}
                    <div className="xl:col-span-2 space-y-3">
                      <span className="text-[10px] font-bold font-mono text-gray-400 uppercase tracking-widest block">Select Order to Track</span>
                      {orders.map((order) => (
                        <div
                          key={order.id}
                          onClick={() => setSelectedOrder(order)}
                          className={`p-4 rounded-xl border cursor-pointer transition-all ${
                            selectedOrder?.id === order.id
                              ? 'border-brand-pink bg-rose-50/30 ring-1 ring-brand-pink-light'
                              : 'border-rose-100 hover:bg-rose-50/10'
                          }`}
                        >
                          <div className="flex justify-between items-start gap-2">
                            <span className="font-mono text-xs font-bold text-neutral-800">{order.order_id}</span>
                            <span className={`text-[9px] uppercase font-bold font-mono px-2 py-0.5 rounded-sm ${
                              order.status === 'delivered' ? 'bg-green-100 text-green-700' :
                              order.status === 'pending' ? 'bg-amber-100 text-amber-700' :
                              order.status === 'cancelled' ? 'bg-red-100 text-red-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {order.status}
                            </span>
                          </div>
                          
                          <div className="mt-2 text-xs text-gray-500 font-sans flex justify-between">
                            <span>{new Date(order.created_at).toLocaleDateString()}</span>
                            <span className="font-semibold text-brand-pink">INR {order.grand_total.toFixed(2)}</span>
                          </div>
                          <div className="text-[10px] text-gray-400 truncate mt-2 font-sans">
                            {order.items.map(i => `${i.productName} x${i.quantity}`).join(', ')}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Detailed Order Tracker (BlueDart style) */}
                    <div className="xl:col-span-3 bg-rose-50/10 rounded-2xl border border-rose-100/50 p-5 space-y-6">
                      {selectedOrder ? (
                        <>
                          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 pb-4 border-b border-rose-100">
                            <div>
                              <span className="text-[10px] font-bold text-gray-400 font-mono block">LIVE TRACKING STATUS</span>
                              <span className="font-mono text-sm font-bold text-brand-pink">{selectedOrder.order_id}</span>
                            </div>
                            <div className="text-right">
                              <span className="text-[10px] font-mono text-gray-400 block">Total Paid</span>
                              <span className="text-xs font-bold text-neutral-800 font-sans">INR {selectedOrder.grand_total.toFixed(2)}</span>
                            </div>
                          </div>

                          {/* Shipment details */}
                          <div className="space-y-4 font-sans">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-800 flex items-center gap-1.5">
                              <Clock size={14} className="text-brand-pink" />
                              BlueDart Shipping Progress
                            </h4>
                            
                            <div className="relative pl-6 border-l-2 border-rose-100 space-y-6 ml-2 pt-1 pb-1">
                              {selectedOrder.tracking.map((track, tIdx) => (
                                <div key={tIdx} className="relative">
                                  {/* Milestone Ring indicator */}
                                  <div className={`absolute -left-[31px] top-1 w-4.5 h-4.5 rounded-full flex items-center justify-center border-2 ${
                                    tIdx === 0 
                                      ? 'bg-brand-pink border-brand-pink text-white animate-pulse'
                                      : 'bg-white border-brand-pink text-brand-pink'
                                  }`}>
                                    <div className="w-1.5 h-1.5 rounded-full bg-current" />
                                  </div>
                                  
                                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1">
                                    <span className="text-xs font-bold text-neutral-800 capitalize font-mono">
                                      {track.status.replace(/_/g, ' ')}
                                    </span>
                                    <span className="text-[10px] text-gray-400 font-mono">
                                      {new Date(track.created_at).toLocaleString()}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                                    {track.description}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Delivery Address Receipt */}
                          <div className="p-4 rounded-xl bg-white border border-rose-100/50 space-y-2">
                            <span className="text-[10px] font-bold font-mono text-gray-400 uppercase tracking-widest block">DELIVERY DETAILS</span>
                            <div className="text-xs text-gray-600 space-y-1">
                              <p className="font-bold text-brand-dark">{selectedOrder.address.full_name} ({selectedOrder.address.phone})</p>
                              <p>{selectedOrder.address.address_line1}, {selectedOrder.address.address_line2}</p>
                              <p>{selectedOrder.address.city}, {selectedOrder.address.state} - {selectedOrder.address.pincode}</p>
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="text-center py-16 text-gray-400">
                          <Eye size={36} className="mx-auto text-gray-200 mb-2" />
                          <p className="text-xs">Select an order on the left to see live delivery tracking status.</p>
                        </div>
                      )}
                    </div>

                  </div>
                )}
              </div>
            )}

            {/* ADDRESSES TAB */}
            {activeTab === 'addresses' && (
              <div className="space-y-8">
                <div className="flex justify-between items-center gap-4">
                  <div>
                    <h2 className="text-xl font-bold tracking-tight text-brand-pink">Delivery Addresses</h2>
                    <p className="text-xs text-gray-500 font-sans mt-1">
                      Manage your shipping locations for effortless, fast checkout.
                    </p>
                  </div>
                  {!isAddingAddress && (
                    <button
                      onClick={() => {
                        setEditingAddress(null);
                        setAddressForm({
                          type: 'home',
                          full_name: '',
                          phone: '',
                          address_line1: '',
                          address_line2: '',
                          city: '',
                          state: '',
                          pincode: '',
                          is_default: false
                        });
                        setIsAddingAddress(true);
                      }}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full bg-brand-pink text-white hover:bg-brand-pink-light shadow-xs transition-colors"
                    >
                      <Plus size={14} /> Add Address
                    </button>
                  )}
                </div>

                {isAddingAddress && (
                  <form onSubmit={handleAddressSubmit} className="bg-rose-50/10 rounded-2xl border border-rose-100 p-6 space-y-4">
                    <h3 className="text-sm font-bold text-neutral-800 border-b border-rose-50 pb-2">
                      {editingAddress ? "Modify Address" : "New Shipping Address"}
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 mb-1">Full Name *</label>
                        <input
                          type="text"
                          required
                          value={addressForm.full_name}
                          onChange={e => setAddressForm({...addressForm, full_name: e.target.value})}
                          placeholder="Receiver's name"
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 mb-1">Phone Number *</label>
                        <input
                          type="tel"
                          required
                          value={addressForm.phone}
                          onChange={e => setAddressForm({...addressForm, phone: e.target.value})}
                          placeholder="10-digit number"
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-semibold text-gray-600 mb-1">Address Line 1 *</label>
                        <input
                          type="text"
                          required
                          value={addressForm.address_line1}
                          onChange={e => setAddressForm({...addressForm, address_line1: e.target.value})}
                          placeholder="Flat/House No, Area, Street name"
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-semibold text-gray-600 mb-1">Address Line 2 (Optional)</label>
                        <input
                          type="text"
                          value={addressForm.address_line2}
                          onChange={e => setAddressForm({...addressForm, address_line2: e.target.value})}
                          placeholder="Landmark, apartment complex, etc."
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 mb-1">City *</label>
                        <input
                          type="text"
                          required
                          value={addressForm.city}
                          onChange={e => setAddressForm({...addressForm, city: e.target.value})}
                          placeholder="City"
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 mb-1">State *</label>
                        <input
                          type="text"
                          required
                          value={addressForm.state}
                          onChange={e => setAddressForm({...addressForm, state: e.target.value})}
                          placeholder="State"
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 mb-1">Pincode *</label>
                        <input
                          type="text"
                          required
                          value={addressForm.pincode}
                          onChange={e => setAddressForm({...addressForm, pincode: e.target.value})}
                          placeholder="6-digit ZIP"
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden focus:ring-1 focus:ring-brand-pink"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-600 mb-1">Address Tag</label>
                        <select
                          value={addressForm.type}
                          onChange={e => setAddressForm({...addressForm, type: e.target.value as any})}
                          className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden"
                        >
                          <option value="home">Home (Family/Residental)</option>
                          <option value="work">Work (Office hours)</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 pt-2">
                      <input
                        type="checkbox"
                        id="is_default"
                        checked={addressForm.is_default}
                        onChange={e => setAddressForm({...addressForm, is_default: e.target.checked})}
                        className="rounded-sm text-brand-pink focus:ring-brand-pink"
                      />
                      <label htmlFor="is_default" className="text-xs text-gray-600 select-none cursor-pointer">
                        Set as primary default delivery address
                      </label>
                    </div>

                    <div className="flex gap-2 justify-end pt-4 border-t border-rose-100">
                      <button
                        type="button"
                        onClick={() => { setIsAddingAddress(false); setEditingAddress(null); }}
                        className="px-4 py-2 text-xs font-semibold text-gray-500 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-5 py-2 text-xs font-semibold rounded-full bg-brand-pink text-white hover:bg-brand-pink-light shadow-xs transition-colors"
                      >
                        {editingAddress ? "Update" : "Save Address"}
                      </button>
                    </div>
                  </form>
                )}

                {addresses.length === 0 ? (
                  <div className="text-center py-12 border border-rose-100 rounded-2xl bg-rose-50/5">
                    <MapPin className="mx-auto text-gray-300 mb-2" size={32} />
                    <p className="text-xs text-gray-500">No shipping addresses added yet. Add your address to proceed.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {addresses.map((addr) => (
                      <div
                        key={addr.id}
                        className={`p-5 rounded-2xl border transition-all ${
                          addr.is_default 
                            ? 'border-brand-pink bg-rose-50/5 ring-1 ring-brand-pink-light/30' 
                            : 'border-rose-100 bg-white'
                        }`}
                      >
                        <div className="flex justify-between items-start gap-4">
                          <span className="text-[10px] font-bold font-mono tracking-wider uppercase px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-600">
                            {addr.type}
                          </span>
                          {addr.is_default && (
                            <span className="text-[9px] font-bold font-mono tracking-wider uppercase px-2 py-0.5 rounded-md bg-brand-pink-light/20 text-brand-pink flex items-center gap-1">
                              <Check size={10} /> Default Shipping
                            </span>
                          )}
                        </div>

                        <div className="mt-4 space-y-1.5 text-xs text-gray-600">
                          <p className="font-bold text-neutral-800">{addr.full_name}</p>
                          <p className="font-medium">{addr.phone}</p>
                          <p>{addr.address_line1}</p>
                          {addr.address_line2 && <p>{addr.address_line2}</p>}
                          <p>{addr.city}, {addr.state} - {addr.pincode}</p>
                        </div>

                        <div className="flex gap-2 justify-end mt-4 pt-4 border-t border-rose-50">
                          <button
                            onClick={() => startEditAddress(addr)}
                            className="text-xs text-gray-500 hover:text-brand-pink transition-colors font-semibold"
                          >
                            Edit
                          </button>
                          <span className="text-gray-200">|</span>
                          <button
                            onClick={() => onDeleteAddress(addr.id)}
                            className="text-xs text-red-500 hover:text-red-700 transition-colors flex items-center gap-1"
                          >
                            <Trash2 size={12} /> Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* COMPLAINTS TAB */}
            {activeTab === 'complaints' && (
              <div className="space-y-8">
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-brand-pink">Customer Help & Support</h2>
                  <p className="text-xs text-gray-500 font-sans mt-1">
                    Replicating HYPEHAVENHUB's support module. Report shipping, payment, or jewel quality issues directly.
                  </p>
                </div>

                {complaintStatusMsg && (
                  <div className="p-3.5 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-semibold flex items-center gap-2">
                    <Check size={16} />
                    {complaintStatusMsg}
                  </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                  
                  {/* File a Complaint form */}
                  <form onSubmit={handleComplaintSubmit} className="lg:col-span-2 bg-rose-50/10 rounded-2xl border border-rose-100 p-5 space-y-4">
                    <h3 className="text-sm font-bold text-neutral-800 border-b border-rose-50 pb-2 flex items-center gap-1.5">
                      <ShieldAlert size={16} className="text-brand-pink" />
                      File Support Ticket
                    </h3>

                    <div>
                      <label className="block text-xs font-semibold text-gray-600 mb-1">Issue Category</label>
                      <select
                        value={complaintType}
                        onChange={e => setComplaintType(e.target.value as any)}
                        className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white"
                      >
                        <option value="product_quality">Product Quality (Broken Hook / Loops)</option>
                        <option value="delivery">Delivery Status Delay</option>
                        <option value="payment">Failed Payment verification</option>
                        <option value="account">Account display setting</option>
                        <option value="website">Website Layout/Bugs</option>
                        <option value="other">Other issue</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-600 mb-1">Priority</label>
                      <div className="flex gap-2">
                        {['low', 'medium', 'high'].map(p => (
                          <button
                            key={p}
                            type="button"
                            onClick={() => setComplaintPriority(p as any)}
                            className={`flex-1 py-1.5 px-3 rounded-lg text-xs capitalize font-medium border transition-all ${
                              complaintPriority === p 
                                ? 'bg-rose-500 text-white border-rose-500 font-bold' 
                                : 'bg-white border-rose-100 text-gray-500 hover:bg-rose-50/50'
                            }`}
                          >
                            {p}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-600 mb-1">Subject</label>
                      <input
                        type="text"
                        required
                        value={complaintSubject}
                        onChange={e => setComplaintSubject(e.target.value)}
                        placeholder="E.g., Jhumka hook slightly loose"
                        className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-600 mb-1">Detailed Description</label>
                      <textarea
                        required
                        rows={4}
                        value={complaintDesc}
                        onChange={e => setComplaintDesc(e.target.value)}
                        placeholder="Provide tracking codes or describe what piece is loose/broken so we can prepare replacement dispatch."
                        className="w-full text-xs p-2.5 rounded-lg border border-rose-100 bg-white focus:outline-hidden"
                      />
                    </div>

                    <button
                      type="submit"
                      className="w-full py-2.5 rounded-lg bg-brand-pink text-white font-bold text-xs hover:bg-brand-pink-light tracking-wider uppercase shadow-sm transition-colors"
                    >
                      Submit Ticket
                    </button>
                  </form>

                  {/* Complaint list panel */}
                  <div className="lg:col-span-3 space-y-4">
                    <h3 className="text-xs font-bold text-gray-400 font-mono tracking-wider uppercase">Active & Past Tickets</h3>
                    
                    {complaints.length === 0 ? (
                      <div className="text-center py-12 border border-dashed border-rose-100 rounded-xl text-gray-400 text-xs">
                        No support tickets filed.
                      </div>
                    ) : (
                      <div className="space-y-4 overflow-y-auto max-h-[450px] pr-2">
                        {complaints.map((comp) => (
                          <div key={comp.id} className="p-4 rounded-xl border border-rose-100/60 bg-white space-y-3">
                            <div className="flex justify-between items-start gap-2">
                              <div>
                                <span className="text-[10px] font-mono text-gray-400 block">{comp.complaint_id}</span>
                                <span className="text-xs font-bold text-brand-dark leading-tight">{comp.subject}</span>
                              </div>
                              <div className="flex gap-1.5 items-center">
                                <span className={`text-[9px] font-bold font-mono uppercase px-2 py-0.5 rounded-sm ${
                                  comp.priority === 'high' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                                }`}>
                                  {comp.priority} priority
                                </span>
                                <span className={`text-[9px] font-bold font-mono uppercase px-2 py-0.5 rounded-sm ${
                                  comp.status === 'resolved' ? 'bg-green-100 text-green-700' :
                                  comp.status === 'open' ? 'bg-amber-100 text-amber-700' :
                                  'bg-blue-100 text-blue-700'
                                }`}>
                                  {comp.status}
                                </span>
                              </div>
                            </div>

                            <p className="text-xs text-gray-500 font-sans italic pl-2 border-l border-rose-200">
                              "{comp.description}"
                            </p>

                            {comp.admin_response ? (
                              <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-100 space-y-1">
                                <span className="text-[9px] font-bold font-mono text-brand-pink block">OFFICIAL SUPPORT RESPONSE</span>
                                <p className="text-xs text-neutral-600 leading-relaxed font-sans">{comp.admin_response}</p>
                              </div>
                            ) : (
                              <div className="text-[10px] text-amber-500 font-semibold font-sans flex items-center gap-1">
                                <Clock size={12} /> Awaiting smart technician analysis...
                              </div>
                            )}

                            <span className="text-[9px] font-mono text-gray-400 block text-right">
                              Filed: {new Date(comp.created_at).toLocaleString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                </div>
              </div>
            )}

            {/* NOTIFICATIONS TAB */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-brand-pink">Account Alerts</h2>
                  <p className="text-xs text-gray-500 font-sans mt-1">
                    Stay updated with promotional codes, dispatch details, and boutique updates.
                  </p>
                </div>

                <div className="space-y-3">
                  {notifications.map((notif) => (
                    <div key={notif.id} className="p-4 rounded-xl border border-rose-50 bg-rose-50/10 flex gap-3.5 items-start">
                      <div className="w-8 h-8 rounded-full bg-brand-pink-light/20 flex items-center justify-center text-brand-pink shrink-0">
                        <Bell size={16} />
                      </div>
                      <div className="space-y-1">
                        <h4 className="text-xs font-bold text-neutral-800">{notif.title}</h4>
                        <p className="text-xs text-neutral-600 leading-relaxed">{notif.message}</p>
                        <span className="text-[9px] font-mono text-gray-400 block pt-1">
                          {new Date(notif.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
}
