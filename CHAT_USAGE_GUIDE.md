# Chat Feature - Usage Guide

## Overview

The Chat feature allows users to contact property admins. Messages are stored and can be viewed by both the user and the assigned admin.

---

## 🧑‍💼 For Admin Users (Django Admin Panel)

### Step 1: Access Admin Panel
1. Go to: `https://broker-backend.onrender.com/admin/` (or your backend URL)
2. Log in with admin credentials
3. Navigate to **Chat** section (under Properties app)

### Step 2: Assign Yourself to a Chat
1. Click on a chat from the list
2. In the **"Admin"** field, select yourself
3. Click **Save**

This marks you as the owner of that chat - now you'll receive messages from the user.

### Step 3: View & Reply to Messages
1. Click on a chat to view all messages
2. Go to **Chat Messages** section to see message thread
3. **Note:** You can only VIEW messages from the admin panel currently
4. **To reply:** Click "Messages" link in the chat or use the API endpoint

---

## 👤 For Regular Users (Frontend)

### Step 1: Browse Properties
1. Go to frontend: `https://broker-frontend.onrender.com/`
2. Create/find a **Locality** and view **Properties**

### Step 2: Start a Chat
1. Click **"Contact Admin"** button on any property card
2. A modal will appear asking you to:
   - Write an initial message (optional)
   - Click **"Start Chat"**

### Step 3: View Chat History
1. Your chat will open showing:
   - All messages from your conversation
   - Real-time updates every 3 seconds
2. Type new messages and hit **Send**

---

## 📋 Chat Model Structure

```
Chat
├── user: The customer asking about property
├── property: The property being discussed
├── admin: The admin responding (set in admin panel)
├── is_active: Whether chat is still open
└── messages: Related ChatMessage objects
    ├── sender: User or Admin
    ├── message: Text content
    ├── is_read: Marked true when admin views
    └── created_at: Timestamp
```

---

## 🔗 API Endpoints

### For Customers

**Create Chat** (auto-creates for a property)
```
POST /api/chats/
Body: { "property": 5 }
```

**Send Message**
```
POST /api/chats/{chat_id}/send_message/
Body: { "message": "Your message text" }
```

**Get Chat History**
```
GET /api/chats/{chat_id}/messages/
Returns: Array of all messages with sender info
```

**List My Chats**
```
GET /api/chats/
Returns: All chats where user is participant or admin
```

---

## 🐛 Troubleshooting

### Chat Not Showing on Frontend
- **Issue:** Frontend trying to connect to `localhost:8000`
- **Solution:** Make sure `VITE_API_URL` environment variable is set on Render frontend service
  - Value: `https://broker-backend.onrender.com/api` (replace with your backend URL)

### Messages Not Fetching
- **Issue:** `Error fetching messages: AxiosError: Network Error`
- **Solution:** 
  1. Verify you're logged in (token in localStorage)
  2. Check backend is running and accessible
  3. Verify Chat ID is correct

### Can't Assign Admin
- **Issue:** Admin field is empty when trying to assign
- **Solution:** 
  1. Make sure you're logged in as superuser/staff
  2. Only superusers can edit Chat admin field
  3. Go to **Users** section in admin and make yourself staff if not already

### No "Contact Admin" Button on Frontend
- **Issue:** Chat features not showing
- **Solution:**
  1. Refresh frontend
  2. Check browser console for errors
  3. Verify property has an ID (new properties may need page reload)

---

## 🚀 Future Enhancements

- [ ] Real-time WebSocket updates (instead of 3-second polling)
- [ ] Reply button in admin panel
- [ ] Email notifications for new messages
- [ ] Message search and filtering
- [ ] Chat archive functionality
- [ ] File/image sharing in chat
- [ ] Chat typing indicators

---

## ✅ Current Status

- ✅ Chat creation working
- ✅ Message sending/fetching working
- ✅ Admin panel chat management
- ✅ Message history persistence
- ✅ Admin assignment
- ⏳ Real-time updates (polling every 3 seconds)
- ⏳ Email notifications (not yet implemented)
