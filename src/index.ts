/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * INSTANT MOCK INTERVIEW SYSTEM
 * Main entry point
 */

export {
  HARDCODED_INTERVIEW_DATABASE,
  findBestMatch,
  getCategories,
  getQuestionsByCategory,
  getRandomQuestion,
  type InterviewQA
} from './interview-database.js';

export {
  InstantInterviewHandler,
  instantInterviewHandler
} from './instant-interview-handler.js';

export {
  startMcpFastInfoServer
} from './mcp-server.js';

export {
  db,
  auth,
  firebaseConfig,
  ensureAnonAuth
} from './firebase.js';

// Quick usage example
console.log(`
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║         🎯 INSTANT MOCK INTERVIEW SYSTEM 🎯                    ║
║                                                                 ║
║            ⚡ ALL ANSWERS ARE HARDCODED ⚡                      ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝

Available Commands:
  npm start      - Run web server
  npm run cli    - Run CLI interface

Documentation: See README.md
`);
