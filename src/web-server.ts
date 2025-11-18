/**
 * Simple Web Server for Mock Interview
 * Serves the instant interview system via HTTP
 */

import express from 'express';
import cors from 'cors';
import { instantInterviewHandler } from './instant-interview-handler.js';
import { getCategories, HARDCODED_INTERVIEW_DATABASE } from './interview-database.js';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// API Routes
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', message: 'Interview API is running' });
});

app.get('/api/stats', (_req, res) => {
  const categories = getCategories();
  res.json({
    totalQuestions: HARDCODED_INTERVIEW_DATABASE.length,
    totalCategories: categories.length,
    categories: categories.map(cat => ({
      name: cat,
      questionCount: HARDCODED_INTERVIEW_DATABASE.filter(q => q.category === cat).length
    }))
  });
});

app.get('/api/categories', (_req, res) => {
  res.json({ categories: getCategories() });
});

app.get('/api/categories/:category/questions', (req, res) => {
  const { category } = req.params;
  const questions = HARDCODED_INTERVIEW_DATABASE.filter(
    q => q.category.toLowerCase() === category.toLowerCase()
  );

  if (questions.length === 0) {
    res.status(404).json({
      error: 'Category not found',
      availableCategories: getCategories()
    });
    return;
  }

  res.json({
    category,
    questionCount: questions.length,
    questions: questions.map(q => ({ question: q.question, category: q.category }))
  });
});

app.get('/api/random', (_req, res) => {
  const result = instantInterviewHandler.getPracticeQuestion();
  res.json({ question: result });
});

app.post('/api/ask', (req, res) => {
  const { question } = req.body;

  if (!question || typeof question !== 'string') {
    res.status(400).json({ error: 'Question is required' });
    return;
  }

  const answer = instantInterviewHandler.getInstantAnswer(question);
  res.json({ question, answer });
});

// Root endpoint
app.get('/', (_req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instant Mock Interview</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }

    .container {
      max-width: 900px;
      margin: 0 auto;
      background: white;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }

    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }

    .header h1 {
      font-size: 2.5em;
      margin-bottom: 10px;
    }

    .header p {
      font-size: 1.2em;
      opacity: 0.9;
    }

    .content {
      padding: 30px;
    }

    .input-section {
      margin-bottom: 30px;
    }

    .input-group {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
    }

    input[type="text"] {
      flex: 1;
      padding: 15px;
      border: 2px solid #e0e0e0;
      border-radius: 10px;
      font-size: 16px;
      transition: border-color 0.3s;
    }

    input[type="text"]:focus {
      outline: none;
      border-color: #667eea;
    }

    button {
      padding: 15px 30px;
      border: none;
      border-radius: 10px;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s;
      color: white;
    }

    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .btn-secondary {
      background: #6c757d;
    }

    .btn-secondary:hover {
      background: #5a6268;
    }

    .quick-actions {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
      margin-bottom: 20px;
    }

    .quick-actions button {
      width: 100%;
    }

    .answer-section {
      background: #f8f9fa;
      border-radius: 10px;
      padding: 20px;
      min-height: 200px;
      max-height: 600px;
      overflow-y: auto;
      white-space: pre-wrap;
      font-family: 'Monaco', 'Courier New', monospace;
      font-size: 14px;
      line-height: 1.6;
      display: none;
    }

    .answer-section.show {
      display: block;
    }

    .stats {
      background: #e8f5e9;
      border-left: 4px solid #4caf50;
      padding: 15px;
      margin-bottom: 20px;
      border-radius: 5px;
    }

    .loading {
      text-align: center;
      padding: 20px;
      color: #667eea;
      font-size: 18px;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .loading::after {
      content: '...';
      animation: pulse 1.5s infinite;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎯 Instant Mock Interview</h1>
      <p>⚡ All Answers Hardcoded for Instant Responses ⚡</p>
    </div>

    <div class="content">
      <div class="stats" id="stats">
        <strong>Loading stats...</strong>
      </div>

      <div class="input-section">
        <div class="input-group">
          <input
            type="text"
            id="questionInput"
            placeholder="Ask any interview question..."
            onkeypress="if(event.key==='Enter') askQuestion()"
          />
          <button class="btn-primary" onclick="askQuestion()">Ask</button>
        </div>

        <div class="quick-actions">
          <button class="btn-secondary" onclick="getRandomQuestion()">🎲 Random Question</button>
          <button class="btn-secondary" onclick="showCategories()">📚 Categories</button>
          <button class="btn-secondary" onclick="clearAnswer()">🗑️ Clear</button>
        </div>
      </div>

      <div class="answer-section" id="answerSection"></div>
    </div>
  </div>

  <script>
    // Load stats on page load
    fetch('/api/stats')
      .then(r => r.json())
      .then(data => {
        const statsHtml = \`
          <strong>📊 Database Stats:</strong> \${data.totalQuestions} questions across \${data.totalCategories} categories | ⚡ All answers are INSTANT!
        \`;
        document.getElementById('stats').innerHTML = statsHtml;
      });

    function showAnswer(text) {
      const section = document.getElementById('answerSection');
      section.textContent = text;
      section.classList.add('show');
    }

    function showLoading() {
      const section = document.getElementById('answerSection');
      section.innerHTML = '<div class="loading">Loading</div>';
      section.classList.add('show');
    }

    function clearAnswer() {
      document.getElementById('answerSection').classList.remove('show');
      document.getElementById('questionInput').value = '';
    }

    async function askQuestion() {
      const input = document.getElementById('questionInput');
      const question = input.value.trim();

      if (!question) {
        alert('Please enter a question');
        return;
      }

      showLoading();

      try {
        const response = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        });

        const data = await response.json();
        showAnswer(data.answer);
      } catch (error) {
        showAnswer('Error: ' + error.message);
      }
    }

    async function getRandomQuestion() {
      showLoading();
      try {
        const response = await fetch('/api/random');
        const data = await response.json();
        showAnswer(data.question);
      } catch (error) {
        showAnswer('Error: ' + error.message);
      }
    }

    async function showCategories() {
      showLoading();
      try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        const text = '📚 AVAILABLE CATEGORIES:\\n\\n' + data.categories.join('\\n');
        showAnswer(text);
      } catch (error) {
        showAnswer('Error: ' + error.message);
      }
    }
  </script>
</body>
</html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║         🎯 INSTANT MOCK INTERVIEW SERVER 🎯                    ║
║                                                                 ║
║            ⚡ ALL ANSWERS ARE HARDCODED ⚡                      ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝

Server running at: http://localhost:${PORT}

API Endpoints:
  GET  /api/stats              - Get database statistics
  GET  /api/categories         - Get all categories
  GET  /api/random             - Get random question
  POST /api/ask                - Ask a question

Open http://localhost:${PORT} in your browser to use the web interface!
  `);
});

export default app;
