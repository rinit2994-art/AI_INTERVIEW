/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {Transport} from '@modelcontextprotocol/sdk/shared/transport.js';
import {z} from 'zod';
import { findBestMatch, getCategories, getQuestionsByCategory, getRandomQuestion } from './interview-database.js';

// Cache for frequently accessed queries
const queryCache = new Map<string, { result: string; timestamp: number }>();
const CACHE_TTL = 60000; // 1 minute cache TTL

export async function startMcpFastInfoServer(
  transport: Transport,
  fastInfoHandler?: (query: string) => string | Promise<string>,
) {
  const server = new McpServer({
    name: 'AI Studio Fast Info - Mock Interview',
    version: '1.0.0',
  });

  // Main interview Q&A tool - INSTANT RESPONSES
  server.tool(
    'fast_info_retrieval',
    'Quickly retrieve concise information on a given query from a specialized, fast knowledge source. Instant answers for mock interview questions.',
    {
      query: z.string().min(1).max(500).describe('The specific query for which to retrieve fast information.')
    },
    async ({query}) => {
      // Check cache first
      const cached = queryCache.get(query);
      if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return {
          content: [{type: 'text', text: cached.result}],
        };
      }

      // Try to find match in hardcoded database FIRST (instant)
      const match = findBestMatch(query);
      let result: string;

      if (match) {
        result = `**Question:** ${match.question}\n\n**Answer:**\n${match.answer}\n\n**Category:** ${match.category}`;
      } else if (fastInfoHandler) {
        // Fallback to custom handler if provided
        result = await Promise.resolve(fastInfoHandler(query));
      } else {
        result = `No exact match found for "${query}". Try asking:\n\n` +
                 `- Common interview questions about JavaScript, React, Node.js\n` +
                 `- Data structures (arrays, linked lists, trees, hash tables)\n` +
                 `- Algorithms (sorting, searching, dynamic programming)\n` +
                 `- System design (REST APIs, caching, microservices)\n` +
                 `- Database concepts (SQL vs NoSQL, indexing)\n\n` +
                 `Or use the 'get_random_question' tool to practice!`;
      }

      // Update cache
      queryCache.set(query, { result, timestamp: Date.now() });

      // Clean old cache entries
      if (queryCache.size > 100) {
        const sortedEntries = Array.from(queryCache.entries())
          .sort((a, b) => b[1].timestamp - a[1].timestamp);
        queryCache.clear();
        sortedEntries.slice(0, 50).forEach(([k, v]) => queryCache.set(k, v));
      }

      return {
        content: [{type: 'text', text: result}],
      };
    },
  );

  // Get all available categories
  server.tool(
    'get_categories',
    'Get all available interview question categories',
    {},
    async () => {
      const categories = getCategories();
      const result = `**Available Categories:**\n\n${categories.map(c => `- ${c}`).join('\n')}\n\nUse 'get_questions_by_category' to see questions in a specific category.`;
      return {
        content: [{type: 'text', text: result}],
      };
    },
  );

  // Get questions by category
  server.tool(
    'get_questions_by_category',
    'Get all interview questions in a specific category',
    {
      category: z.string().describe('The category name (e.g., "JavaScript", "React", "Algorithms")')
    },
    async ({category}) => {
      const questions = getQuestionsByCategory(category);
      if (questions.length === 0) {
        return {
          content: [{type: 'text', text: `No questions found in category "${category}". Use 'get_categories' to see available categories.`}],
        };
      }

      const result = `**${category} Questions (${questions.length}):**\n\n` +
                     questions.map((q, i) => `${i + 1}. ${q.question}`).join('\n');
      return {
        content: [{type: 'text', text: result}],
      };
    },
  );

  // Get random question for practice
  server.tool(
    'get_random_question',
    'Get a random interview question to practice',
    {},
    async () => {
      const question = getRandomQuestion();
      const result = `**Random Interview Question:**\n\n${question.question}\n\n**Category:** ${question.category}\n\n*Think about your answer, then ask me the same question to see the answer!*`;
      return {
        content: [{type: 'text', text: result}],
      };
    },
  );

  await server.connect(transport);
  console.log('🚀 MCP Fast Info Server running with HARDCODED interview database');
  console.log('✨ Instant answers for mock interview questions!');
  console.log(`📚 ${getCategories().length} categories with instant responses`);
}
