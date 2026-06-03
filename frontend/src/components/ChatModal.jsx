import React, { useState } from 'react';
import apiClient from '../utils/api';

export default function ChatModal({ property, onClose, onChatCreated }) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStartChat = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Please log in to contact the admin');
        setLoading(false);
        return;
      }

      // Create chat
      const chatRes = await apiClient.post('chats/', { property: property.id });
      const chat = chatRes.data;

      // Send initial message if provided
      if (message.trim()) {
        await apiClient.post(
          `chats/${chat.id}/send_message/`,
          { message }
        );
      }

      onChatCreated(chat);
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start chat');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white/95 backdrop-blur rounded-xl shadow-2xl max-w-md w-full mx-4 border-2 border-peacock-300">
        {/* Header */}
        <div className="bg-gradient-divine px-6 py-4 rounded-t-xl flex justify-between items-center">
          <div>
            <h2 className="text-white font-bold text-lg">💌 Contact Admin</h2>
            <p className="text-krishna-100 text-sm">{property.title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-saffron-200 text-2xl font-light transition"
          >
            ✕
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleStartChat} className="p-6 space-y-4 bg-gradient-to-br from-krishna-50 to-peacock-50">
          {error && (
            <div className="bg-red-50 border-2 border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm font-medium">
              ⚠️ {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-bold text-krishna-700 mb-2">
              💰 Price: <span className="text-saffron-600">${property.price?.toLocaleString() || 'N/A'}</span>
            </label>
            <p className="text-xs text-krishna-600 bg-white/60 p-2 rounded border-l-4 border-saffron-400">{property.description}</p>
          </div>

          <div>
            <label className="block text-sm font-bold text-krishna-700 mb-2">
              ✉️ Your Message
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Tell us about your interest in this property..."
              rows="4"
              className="w-full px-3 py-2 border-2 border-krishna-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-peacock-500 focus:border-transparent bg-white/80"
            />
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border-2 border-krishna-300 rounded-lg text-krishna-700 font-medium hover:bg-krishna-100 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 btn-krishna disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium"
            >
              {loading ? '⏳ Starting Chat...' : '💬 Start Chat'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
