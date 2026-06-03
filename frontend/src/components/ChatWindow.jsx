import React, { useState, useEffect, useRef } from 'react';
import apiClient from '../utils/api';

export default function ChatWindow({ chat, onClose }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchMessages();
    // Refresh messages every 3 seconds
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, [chat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessages = async () => {
    try {
      const res = await apiClient.get(`chats/${chat.id}/messages/`);
      setMessages(res.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching messages:", err);
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await apiClient.post(
        `chats/${chat.id}/send_message/`,
        { message: newMessage }
      );
      setNewMessage('');
      fetchMessages();
    } catch (err) {
      console.error("Error sending message:", err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white/95 backdrop-blur rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-96 flex flex-col border-2 border-peacock-300">
        {/* Header */}
        <div className="bg-gradient-divine px-6 py-4 rounded-t-xl flex justify-between items-center">
          <div>
            <h2 className="text-white font-bold text-lg">{chat.property_title}</h2>
            <p className="text-krishna-100 text-sm">💬 Chat with {chat.admin_name || 'Admin'}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-saffron-200 text-2xl font-light transition"
          >
            ✕
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gradient-to-br from-krishna-50 to-peacock-50">
          {loading ? (
            <div className="flex justify-center items-center h-full">
              <p className="text-krishna-500">Loading messages...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex justify-center items-center h-full">
              <p className="text-krishna-400 text-sm">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.sender === chat.user ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`px-4 py-2 rounded-lg max-w-xs border-2 ${
                    msg.sender === chat.user
                      ? 'bg-gradient-krishna text-white border-krishna-400 rounded-br-none'
                      : 'bg-white/80 text-krishna-900 border-peacock-300 rounded-bl-none'
                  }`}
                >
                  <p className="text-xs font-semibold mb-1 opacity-75">
                    {msg.sender_name}
                  </p>
                  <p className="text-sm">{msg.message}</p>
                  <p className="text-xs mt-1 opacity-50">
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <form onSubmit={handleSendMessage} className="border-t-2 border-peacock-200 bg-white/80 p-4 rounded-b-xl">
          <div className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border-2 border-krishna-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-peacock-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={!newMessage.trim()}
              className="btn-krishna disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium text-sm"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
