# 🎯 Instant Mock Interview System

> ⚡ **ALL ANSWERS ARE HARDCODED** - No API calls, no delays, just instant responses!

A complete mock interview system with **hardcoded answers** for instant responses. Perfect for practicing technical interviews without internet connectivity or API limitations.

## ✨ Features

- **⚡ Instant Responses**: All answers are hardcoded in the database
- **📚 Comprehensive Coverage**: 50+ common interview questions
- **🎲 Practice Mode**: Get random questions to test yourself
- **📊 Multiple Categories**: JavaScript, React, Node.js, Data Structures, Algorithms, System Design, and more
- **🌐 Multiple Interfaces**: CLI, Web UI, and MCP Server
- **🔥 Firebase Integration**: Optional persistence with Firebase
- **💾 Zero External Dependencies**: Works completely offline

## 🚀 Quick Start

### Installation

```bash
npm install
npm run build
```

### Run Web Interface

```bash
npm start
```

Then open http://localhost:3000 in your browser

### Run CLI Interface

```bash
npm run cli
```

## 📚 Available Topics

The database includes hardcoded answers for:

- **JavaScript**: Closures, Event Loop, Promises, async/await, this keyword, var/let/const
- **React**: Hooks, Virtual DOM, Props vs State, useEffect, Component Lifecycle
- **Node.js**: Event Loop, Express.js, Async I/O
- **Data Structures**: Arrays, Linked Lists, Hash Tables, Binary Search Trees
- **Algorithms**: Sorting (QuickSort), BFS, DFS, Dynamic Programming
- **System Design**: REST APIs, Caching, Microservices, Database Indexing
- **Database**: SQL vs NoSQL, Normalization, Indexing
- **Security**: JWT, CORS
- **Testing**: Unit vs Integration Testing
- **Git**: Merge vs Rebase
- **Performance**: Web Optimization Techniques
- **TypeScript**: Type System Benefits
- **CSS**: Flexbox

## 🎮 Usage

### Web Interface

1. Start the server: `npm start`
2. Open http://localhost:3000
3. Type any interview question
4. Get instant answer!

### CLI Interface

```bash
npm run cli
```

Commands:
- Type any question to get an answer
- `random` - Get a random practice question
- `categories` - See all available categories
- `questions <category>` - List all questions in a category
- `stats` - See database statistics
- `exit` - Quit

### MCP Server

The system includes an MCP (Model Context Protocol) server that can be integrated with AI assistants:

```typescript
import { startMcpFastInfoServer } from './src/mcp-server.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const transport = new StdioServerTransport();
await startMcpFastInfoServer(transport);
```

## 🔧 API Endpoints

### GET /api/stats
Get database statistics

```json
{
  "totalQuestions": 50,
  "totalCategories": 15,
  "categories": [...]
}
```

### GET /api/categories
Get all available categories

```json
{
  "categories": ["JavaScript", "React", "Node.js", ...]
}
```

### GET /api/random
Get a random practice question

### POST /api/ask
Ask a question and get instant answer

```json
{
  "question": "What is closure in JavaScript?"
}
```

Response:
```json
{
  "question": "What is closure in JavaScript?",
  "answer": "..."
}
```

## 📖 Example Questions

Try asking:
- "What is closure in JavaScript?"
- "Explain event loop in JavaScript"
- "What are React hooks?"
- "What is the difference between props and state?"
- "Explain quicksort algorithm"
- "What is REST API?"
- "What is database indexing?"

## 🎯 Perfect For

✅ Interview preparation
✅ Quick reference during coding
✅ Offline practice
✅ Teaching and learning
✅ Technical screening prep

## 🔥 Why Hardcoded?

1. **⚡ Instant**: No network latency or API delays
2. **💰 Free**: No API costs or rate limits
3. **🔒 Private**: All data stays local
4. **📴 Offline**: Works without internet
5. **🎯 Consistent**: Same quality answers every time
6. **⚙️ Reliable**: No API downtime or errors

## 🛠️ Technology Stack

- **TypeScript**: Type-safe code
- **Express**: Web server
- **Node.js**: Runtime environment
- **MCP SDK**: Model Context Protocol integration
- **Firebase**: Optional persistence
- **Zod**: Schema validation

## 📁 Project Structure

```
AI_INTERVIEW/
├── src/
│   ├── interview-database.ts       # Hardcoded Q&A database
│   ├── instant-interview-handler.ts # Answer matching logic
│   ├── mcp-server.ts               # MCP server implementation
│   ├── web-server.ts               # Express web server
│   ├── cli.ts                      # CLI interface
│   └── firebase.ts                 # Firebase config
├── package.json
├── tsconfig.json
└── README.md
```

## 🚀 Extending the Database

Add more questions in `src/interview-database.ts`:

```typescript
{
  question: "Your question here?",
  answer: `Your detailed answer here...`,
  category: "Category Name",
  keywords: ["keyword1", "keyword2", "keyword3"]
}
```

## 📝 License

Apache-2.0

## 🤝 Contributing

Feel free to add more hardcoded questions and answers!

---

**⚡ Built for instant interview prep - no waiting, no API calls, just pure hardcoded knowledge! ⚡**
