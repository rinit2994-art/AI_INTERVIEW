# 🚀 QUICK START GUIDE

## Instant Setup (3 steps!)

### 1. Install Dependencies

```bash
npm install
```

### 2. Build the Project

```bash
npm run build
```

### 3. Choose Your Interface

#### Option A: Web Interface (Recommended)

```bash
npm start
```

Then open **http://localhost:3000** in your browser

**Features:**
- Beautiful UI
- Type questions and get instant answers
- Random question generator
- Category browser
- Stats dashboard

#### Option B: CLI Interface

```bash
npm run cli
```

**Features:**
- Terminal-based interface
- Type questions directly
- Commands: `random`, `categories`, `stats`, `exit`

## ⚡ Try These Questions

Copy and paste these into the web interface or CLI:

```
What is closure in JavaScript?
Explain event loop in JavaScript
What are React hooks?
What is the difference between props and state?
Explain quicksort algorithm
What is REST API?
What is the difference between let, const, and var?
What is promise in JavaScript?
What is Virtual DOM?
What is JWT and how does it work?
```

## 🎯 Quick Commands (CLI Only)

- `random` - Get a random practice question
- `categories` - See all available topics
- `questions JavaScript` - See all JavaScript questions
- `stats` - View database statistics
- `exit` - Quit the CLI

## 📊 What's Inside?

- **50+ Questions** across 15 categories
- **Instant Answers** - all hardcoded, no API calls
- **Zero Latency** - responses in milliseconds
- **100% Offline** - works without internet

## 🔥 Development Mode

Want to modify the code?

```bash
# Run web server with hot reload
npm run dev

# Run CLI with hot reload
npm run dev:cli
```

## 📝 Add Your Own Questions

Edit `src/interview-database.ts` and add:

```typescript
{
  question: "Your question?",
  answer: `Your detailed answer...`,
  category: "YourCategory",
  keywords: ["keyword1", "keyword2"]
}
```

Then rebuild:

```bash
npm run build
```

## 🌐 API Usage

If you want to integrate the API into your own app:

```javascript
// Ask a question
fetch('http://localhost:3000/api/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is closure?' })
})
.then(r => r.json())
.then(data => console.log(data.answer));

// Get random question
fetch('http://localhost:3000/api/random')
.then(r => r.json())
.then(data => console.log(data));

// Get stats
fetch('http://localhost:3000/api/stats')
.then(r => r.json())
.then(data => console.log(data));
```

## 🎓 Pro Tips

1. **Practice Mode**: Use the random question feature to quiz yourself
2. **Category Focus**: Browse questions by category to focus on weak areas
3. **Offline First**: All answers are hardcoded - no internet needed
4. **Copy Answers**: All answers are formatted with code examples
5. **Extend It**: Add more questions to customize for your interview

## 🆘 Troubleshooting

**Port 3000 already in use?**
```bash
PORT=4000 npm start
```

**TypeScript errors?**
```bash
npm install
npm run build
```

**Need to reinstall?**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

**🎯 You're ready! Start practicing for your interview now!**
