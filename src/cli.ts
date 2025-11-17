#!/usr/bin/env node
/**
 * INSTANT MOCK INTERVIEW CLI
 * All answers are hardcoded for immediate responses
 */

import * as readline from 'readline';
import { instantInterviewHandler } from './instant-interview-handler.js';
import { getCategories } from './interview-database.js';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function showWelcome() {
  console.clear();
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║           🎯 INSTANT MOCK INTERVIEW SYSTEM 🎯                  ║
║                                                                 ║
║              ⚡ ALL ANSWERS ARE HARDCODED ⚡                    ║
║                  📚 INSTANT RESPONSES 📚                        ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝

Welcome to the Instant Mock Interview System!

COMMANDS:
  📝 Ask any interview question to get instant answer
  🎲 Type 'random' to get a random practice question
  📚 Type 'categories' to see all available topics
  📊 Type 'stats' to see database statistics
  🚪 Type 'exit' or 'quit' to leave

Available Categories: ${getCategories().join(', ')}

Type your question or command below:
─────────────────────────────────────────────────────────────────
`);
}

function processInput(input: string) {
  const trimmed = input.trim().toLowerCase();

  if (trimmed === 'exit' || trimmed === 'quit') {
    console.log('\n👋 Thanks for practicing! Good luck with your interview!\n');
    rl.close();
    process.exit(0);
  }

  if (trimmed === 'random' || trimmed === 'practice') {
    console.log('\n' + instantInterviewHandler.getPracticeQuestion() + '\n');
    return;
  }

  if (trimmed === 'categories') {
    const categories = getCategories();
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║ 📚 AVAILABLE CATEGORIES
╚═══════════════════════════════════════════════════════════════╝

${categories.map((c, i) => `${i + 1}. ${c}`).join('\n')}

To see questions in a category, type: questions <category>
Example: questions JavaScript
`);
    return;
  }

  if (trimmed === 'stats') {
    console.log('\n' + instantInterviewHandler.getStats() + '\n');
    return;
  }

  if (trimmed.startsWith('questions ')) {
    const category = input.substring('questions '.length).trim();
    console.log('\n' + instantInterviewHandler.getCategoryQuestions(category) + '\n');
    return;
  }

  if (trimmed === 'help') {
    showWelcome();
    return;
  }

  if (trimmed === '' || trimmed === 'clear') {
    console.clear();
    return;
  }

  // Treat as interview question
  const answer = instantInterviewHandler.getInstantAnswer(input);
  console.log('\n' + answer + '\n');
}

function startCLI() {
  showWelcome();

  rl.on('line', (input) => {
    processInput(input);
    rl.prompt();
  });

  rl.on('close', () => {
    console.log('\n👋 Goodbye!\n');
    process.exit(0);
  });

  rl.setPrompt('💬 You: ');
  rl.prompt();
}

// Start the CLI
startCLI();
