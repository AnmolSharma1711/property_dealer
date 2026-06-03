import React, { useState } from 'react';
import ChatModal from './ChatModal';
import ChatWindow from './ChatWindow';

export default function PropertyCard({ property, locality }) {
  const [showChatModal, setShowChatModal] = useState(false);
  const [activeChat, setActiveChat] = useState(null);

  const handleChatCreated = (chat) => {
    setActiveChat(chat);
  };

  return (
    <>
      <div className="bg-white/80 backdrop-blur rounded-lg border-2 border-krishna-200 shadow-md hover:shadow-xl transition card-divine overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-divine px-4 py-3 border-b-2 border-saffron-300">
          <h3 className="font-bold text-white text-base">{property.title}</h3>
          <p className="text-xs text-krishna-100 mt-1">{locality?.name}, {locality?.city}</p>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Price */}
          <div className="flex items-center justify-between bg-gradient-to-r from-saffron-50 to-saffron-100 p-3 rounded-lg border-2 border-saffron-200">
            <span className="text-sm font-semibold text-saffron-700">💰 Price:</span>
            <span className="font-bold text-lg text-saffron-900">
              ${property.price?.toLocaleString()}
            </span>
          </div>

          {/* Description */}
          <div>
            <p className="text-sm text-krishna-700 line-clamp-2">
              {property.description || 'No description available'}
            </p>
          </div>

          {/* Locality Info */}
          {locality?.profile && (
            <div className="bg-gradient-to-br from-peacock-50 to-peacock-100 p-3 rounded-lg border-2 border-peacock-200">
              <p className="text-xs text-peacock-700 mb-1">
                <strong>👥 Tourist Rating:</strong> {locality.profile.tourist_rating || 'N/A'}/5 ⭐
              </p>
              <p className="text-xs text-peacock-700">
                <strong>🏪 Commercial Rating:</strong> {locality.profile.commercial_rating || 'N/A'}/5 ⭐
              </p>
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-krishna-500 pt-2 border-t-2 border-krishna-100">
            📅 Listed on {new Date(property.created_at).toLocaleDateString()}
          </div>
        </div>

        {/* Actions */}
        <div className="bg-gradient-to-r from-krishna-50 to-peacock-50 px-4 py-3 border-t-2 border-krishna-200 flex gap-2">
          <button
            onClick={() => setShowChatModal(true)}
            className="flex-1 btn-krishna text-white px-3 py-2 rounded-lg font-medium text-sm"
          >
            <span>💬</span> Contact Admin
          </button>
          <button
            onClick={() => alert('View details feature coming soon!')}
            className="flex-1 bg-peacock-100 hover:bg-peacock-200 text-peacock-800 px-3 py-2 rounded-lg font-medium text-sm transition border-2 border-peacock-300"
          >
            Details
          </button>
        </div>
      </div>

      {/* Chat Modal */}
      {showChatModal && (
        <ChatModal
          property={property}
          onClose={() => setShowChatModal(false)}
          onChatCreated={handleChatCreated}
        />
      )}

      {/* Chat Window */}
      {activeChat && (
        <ChatWindow
          chat={activeChat}
          onClose={() => setActiveChat(null)}
        />
      )}
    </>
  );
}
