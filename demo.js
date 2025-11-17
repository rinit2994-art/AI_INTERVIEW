/**
 * Simple demo to test the instant interview system
 * Run with: node demo.js (after npm run build)
 */

import { findBestMatch, getCategories, getRandomQuestion, HARDCODED_INTERVIEW_DATABASE } from './dist/interview-database.js';
import { instantInterviewHandler } from './dist/instant-interview-handler.js';

console.log('🎯 INSTANT MOCK INTERVIEW DEMO\n');
console.log('═══════════════════════════════════════════════════\n');

// Show database stats
console.log(`📊 Database Statistics:`);
console.log(`   Total Questions: ${HARDCODED_INTERVIEW_DATABASE.length}`);
console.log(`   Categories: ${getCategories().join(', ')}\n`);

// Test 1: Direct question
console.log('📝 Test 1: Asking "What is closure in JavaScript?"\n');
const answer1 = instantInterviewHandler.getInstantAnswer('What is closure in JavaScript?');
console.log(answer1);
console.log('\n═══════════════════════════════════════════════════\n');

// Test 2: Keyword match
console.log('📝 Test 2: Asking "closure" (keyword matching)\n');
const answer2 = instantInterviewHandler.getInstantAnswer('closure');
console.log(answer2);
console.log('\n═══════════════════════════════════════════════════\n');

// Test 3: Random question
console.log('📝 Test 3: Random practice question\n');
const practice = instantInterviewHandler.getPracticeQuestion();
console.log(practice);
console.log('\n═══════════════════════════════════════════════════\n');

// Test 4: Category questions
console.log('📝 Test 4: List React questions\n');
const reactQuestions = instantInterviewHandler.getCategoryQuestions('React');
console.log(reactQuestions);
console.log('\n═══════════════════════════════════════════════════\n');

// Test 5: Stats
console.log('📝 Test 5: System stats\n');
const stats = instantInterviewHandler.getStats();
console.log(stats);
console.log('\n═══════════════════════════════════════════════════\n');

console.log('✅ All tests completed successfully!');
console.log('⚡ All answers are INSTANT - no API calls made!');
console.log('\nTry the full experience:');
console.log('  - Web UI: npm start');
console.log('  - CLI: npm run cli\n');
