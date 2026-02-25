# StudyBot AI - Your Intelligent Learning Companion 🤖📚

StudyBot AI is a modern, responsive AI chatbot designed specifically for students. It provides instant answers to study questions with a beautiful, user-friendly interface that works perfectly on all devices.

Powered by **Hugging Face Gradio Spaces** for intelligent RAG-based document search and answering.

<div align="center">

![StudyBot AI](./public/icon-512.png)

**The Ultimate AI Learning Assistant with HF Space Integration**

[Quick Start](#quick-start) • [Features](#features) • [Setup Guide](#setup-guide) • [API Integration](#api-integration) • [Deployment](#deployment)

</div>

---

## 🌟 Features

### 💬 Intelligent Chat Interface
- Real-time AI-powered conversation
- Beautiful message bubbles with timestamps
- Loading animations and status indicators
- Smooth auto-scrolling to latest messages

### 📱 Fully Responsive Design
- **Mobile First**: Optimized for smartphones and tablets
- **Desktop Ready**: Beautiful layout on large screens
- **Tablet Optimized**: Perfect for all screen sizes
- **Touch Friendly**: Large touch targets (44px+ minimum)

### 🎨 Modern UI/UX
- Clean, professional interface inspired by modern chat apps
- Dark and Light theme with automatic detection
- Smooth animations and transitions
- Accessible design with ARIA labels

### 💾 Persistent Storage
- Chat history saved locally
- Automatic session recovery
- Export chat functionality
- Clear chat history option

### 📦 Progressive Web App (PWA)
- **Installable**: Add to home screen on any device
- **Offline Support**: Works with limited connectivity
- **App-like Experience**: Runs in standalone mode
- **Fast Loading**: Service worker caching

### 🎯 Student-Focused Features
- Friendly, approachable design
- Quick action buttons for common tasks
- Helpful tips and suggestions
- Learning-optimized layout

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (or pnpm, npm, yarn)
- A Gradio API endpoint or backend service

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/studybot-ai.git
cd studybot-ai

# Install dependencies
npm install
# or
pnpm install
```

### Running Locally

```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Building for Production

```bash
# Build optimized version
npm run build

# Start production server
npm start
```

---

## 📚 API Setup

### Option 1: Use Your Existing Gradio API

Update the API endpoint in `components/ChatInterface.tsx`:

```typescript
const response = await fetch('YOUR_API_URL/api/call/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: [userMessage] }),
});
```

### Option 2: Create a Simple Gradio Backend

```python
import gradio as gr

def answer_question(question):
    # Your AI logic here
    answer = process_with_ai(question)
    source = "Your Knowledge Base"
    return answer, source

interface = gr.Interface(
    fn=answer_question,
    inputs="text",
    outputs=["text", "text"],
)

interface.launch(share=False)
```

For detailed API setup, see [API_INTEGRATION.md](./API_INTEGRATION.md)

---

## 🛠️ Configuration

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:7860
NEXT_PUBLIC_DEFAULT_THEME=system
```

See `.env.example` for all available options.

### Customization

#### Change Primary Color

Edit `app/globals.css`:

```css
:root {
  --primary: #3b82f6;  /* Change this to your color */
  --accent: #0ea5e9;
}
```

#### Update App Name and Logo

Edit `app/layout.tsx` and `public/manifest.json`

#### Customize API Endpoint

Edit `components/ChatInterface.tsx`:

```typescript
const API_URL = 'YOUR_API_ENDPOINT';
```

---

## 📱 Installation as PWA

### On Mobile
1. Open app in browser
2. Tap share/menu button
3. Select "Add to Home Screen"
4. App appears as native app

### On Desktop (Chrome/Edge)
1. Open app in browser
2. Click install button in address bar
3. App launches in separate window

---

## 📦 Deployment

### Deploy to Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Deploy to Other Platforms

The app is a standard Next.js 16 application:

- **Netlify**: Connect GitHub repo, auto-deploys
- **GitHub Pages**: Use `next export` and GitHub Actions
- **AWS/GCP/Azure**: Standard Node.js deployment
- **Docker**: Create containerized deployment

### Important: CORS Configuration

For production, ensure your API has CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

---

## 🎨 Design System

### Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Primary | `#3b82f6` (Blue) | Buttons, links, user messages |
| Accent | `#0ea5e9` (Cyan) | Highlights, AI messages |
| Background | `#f8f9fa` (Light) | Main background (light mode) |
| Background | `#0f172a` (Dark) | Main background (dark mode) |

### Typography

- **Headers**: Geist (sans-serif)
- **Body**: Geist (sans-serif)
- **Monospace**: Geist Mono

---

## 📱 Responsive Breakpoints

- **Mobile**: < 640px (full width)
- **Tablet**: 640px - 1024px (2 columns where applicable)
- **Desktop**: > 1024px (3+ columns)

---

## 🔧 Project Structure

```
studybot-ai/
├── app/
│   ├── layout.tsx              # Root layout with PWA config
│   ├── page.tsx                # Main chat page
│   ├── globals.css             # Global styles and theme
│   └── favicon.ico
├── components/
│   ├── ChatInterface.tsx       # Main chat container
│   ├── ChatMessage.tsx         # Message display
│   ├── ChatInput.tsx           # Message input form
│   ├── Sidebar.tsx             # Navigation sidebar
│   ├── ThemeToggle.tsx         # Theme switcher
│   └── ui/                     # shadcn/ui components
├── hooks/
│   ├── use-toast.ts            # Toast notifications
│   └── use-mobile.tsx          # Mobile detection
├── lib/
│   └── utils.ts                # Utility functions
├── public/
│   ├── sw.js                   # Service worker
│   ├── manifest.json           # PWA manifest
│   ├── icon-192.png            # App icon
│   ├── icon-512.png            # App icon
│   ├── apple-icon.png          # iOS icon
│   └── screenshot-*.png        # PWA screenshots
├── SETUP.md                    # Setup guide
├── API_INTEGRATION.md          # API integration guide
├── .env.example                # Environment variables example
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.mjs
```

---

## 🚀 Features in Detail

### Chat Management
- ✅ Real-time message streaming
- ✅ Message history with timestamps
- ✅ Persistent storage
- ✅ Export chat as file
- ✅ Clear conversation option

### User Experience
- ✅ Auto-scrolling to latest message
- ✅ Loading state animations
- ✅ Error handling with toasts
- ✅ Keyboard shortcuts (Shift+Enter for new line)
- ✅ Mobile menu button

### Performance
- ✅ Code splitting
- ✅ Service worker caching
- ✅ Lazy loading images
- ✅ Optimized bundle size

### Accessibility
- ✅ Semantic HTML
- ✅ ARIA labels
- ✅ Keyboard navigation
- ✅ Screen reader support

---

## 🐛 Troubleshooting

### Service Worker Not Working
```bash
# Clear cache
1. Open DevTools (F12)
2. Application > Clear Storage
3. Reload page
```

### API Connection Failed
```bash
# Check your API is running
# Update API URL in ChatInterface.tsx
# Verify CORS is enabled on API
```

### Chat Not Saving
```bash
# Check localStorage is enabled
# Clear browser cache
# Check browser console for errors
```

### PWA Not Installing
```bash
# Ensure using HTTPS (or localhost for dev)
# Check manifest.json exists
# Verify app icons are in public/
```

---

## 💡 Tips for Development

### Adding Features

1. Create new component in `components/`
2. Import in `ChatInterface.tsx`
3. Test on mobile and desktop
4. Update service worker if needed

### Testing Locally

```bash
# Desktop
npm run dev

# Mobile: Use your phone to visit http://[YOUR_IP]:3000
# Tablet: Use tablet in responsive mode (DevTools)
```

### Production Checklist

- [ ] Update API endpoint
- [ ] Test on multiple devices
- [ ] Check PWA installation works
- [ ] Test offline functionality
- [ ] Update app icons if needed
- [ ] Configure CORS on API
- [ ] Enable HTTPS on deployed app
- [ ] Test theme switching

---

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup instructions
- [API Integration](./API_INTEGRATION.md) - How to connect your backend
- [Next.js Docs](https://nextjs.org/docs) - Framework documentation
- [Tailwind CSS](https://tailwindcss.com) - Styling framework
- [shadcn/ui](https://ui.shadcn.com) - Component library

---

## 🌐 Browser Support

| Browser | Support | PWA |
|---------|---------|-----|
| Chrome 90+ | ✅ Full | ✅ Yes |
| Firefox 88+ | ✅ Full | ✅ Yes |
| Safari 14+ | ✅ Full | ✅ Yes |
| Edge 90+ | ✅ Full | ✅ Yes |
| Mobile Chrome | ✅ Full | ✅ Yes |
| Mobile Safari | ✅ Full | ✅ Yes |

---

## 📄 License

MIT License - Feel free to use this project for personal or commercial purposes.

---

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 💬 Support

- 📖 Check [SETUP.md](./SETUP.md) for setup issues
- 🔗 Read [API_INTEGRATION.md](./API_INTEGRATION.md) for API problems
- 🐛 Open an issue on GitHub for bugs
- 💡 Share ideas in Discussions

---

## 🎓 Made for Students, by Developers

StudyBot AI is built with students in mind. Our mission is to make learning more accessible and enjoyable through AI-powered assistance.

**Start learning smarter today!** 🚀

---

<div align="center">

**[⬆ Back to Top](#studybot-ai---your-intelligent-learning-companion-)**

Made with ❤️ for student success

</div>
