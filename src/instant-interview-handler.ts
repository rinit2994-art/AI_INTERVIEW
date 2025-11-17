/**
 * INSTANT INTERVIEW ANSWER HANDLER
 * Everything is hardcoded for immediate responses
 */

import { findBestMatch, getRandomQuestion, HARDCODED_INTERVIEW_DATABASE } from './interview-database.js';

export class InstantInterviewHandler {
  private questionHistory: string[] = [];
  private currentCategory: string | null = null;

  /**
   * Get instant answer for any interview question
   */
  getInstantAnswer(query: string): string {
    const match = findBestMatch(query);

    if (match) {
      this.questionHistory.push(query);
      return this.formatAnswer(match.question, match.answer, match.category);
    }

    return this.getSuggestions(query);
  }

  /**
   * Format answer in a clean way
   */
  private formatAnswer(question: string, answer: string, category: string): string {
    return `
╔═══════════════════════════════════════════════════════════════╗
║ 📝 INTERVIEW QUESTION
╚═══════════════════════════════════════════════════════════════╝

${question}

╔═══════════════════════════════════════════════════════════════╗
║ ✅ ANSWER
╚═══════════════════════════════════════════════════════════════╝

${answer}

─────────────────────────────────────────────────────────────────
📚 Category: ${category}
─────────────────────────────────────────────────────────────────
`.trim();
  }

  /**
   * Get suggestions when no match found
   */
  private getSuggestions(query: string): string {
    const categories = new Set(HARDCODED_INTERVIEW_DATABASE.map(q => q.category));
    const randomQ = getRandomQuestion();

    return `
╔═══════════════════════════════════════════════════════════════╗
║ ❌ NO EXACT MATCH FOUND
╚═══════════════════════════════════════════════════════════════╝

I couldn't find an exact match for: "${query}"

╔═══════════════════════════════════════════════════════════════╗
║ 💡 AVAILABLE TOPICS
╚═══════════════════════════════════════════════════════════════╝

${Array.from(categories).map(c => `  • ${c}`).join('\n')}

╔═══════════════════════════════════════════════════════════════╗
║ 🎲 TRY THIS QUESTION
╚═══════════════════════════════════════════════════════════════╝

${randomQ.question}

Category: ${randomQ.category}

─────────────────────────────────────────────────────────────────
💬 Ask me this question to see the answer!
─────────────────────────────────────────────────────────────────
`.trim();
  }

  /**
   * Get practice question
   */
  getPracticeQuestion(category?: string): string {
    let question;

    if (category) {
      const categoryQuestions = HARDCODED_INTERVIEW_DATABASE.filter(
        q => q.category.toLowerCase() === category.toLowerCase()
      );
      if (categoryQuestions.length > 0) {
        question = categoryQuestions[Math.floor(Math.random() * categoryQuestions.length)];
      } else {
        question = getRandomQuestion();
      }
    } else {
      question = getRandomQuestion();
    }

    return `
╔═══════════════════════════════════════════════════════════════╗
║ 🎯 PRACTICE QUESTION
╚═══════════════════════════════════════════════════════════════╝

${question.question}

─────────────────────────────────────────────────────────────────
📚 Category: ${question.category}
─────────────────────────────────────────────────────────────────

Think about your answer, then ask me the same question to see the solution!
`.trim();
  }

  /**
   * Get all questions in a category
   */
  getCategoryQuestions(category: string): string {
    const questions = HARDCODED_INTERVIEW_DATABASE.filter(
      q => q.category.toLowerCase() === category.toLowerCase()
    );

    if (questions.length === 0) {
      const categories = new Set(HARDCODED_INTERVIEW_DATABASE.map(q => q.category));
      return `
╔═══════════════════════════════════════════════════════════════╗
║ ❌ CATEGORY NOT FOUND
╚═══════════════════════════════════════════════════════════════╝

Available categories:
${Array.from(categories).map(c => `  • ${c}`).join('\n')}
`.trim();
    }

    return `
╔═══════════════════════════════════════════════════════════════╗
║ 📚 ${category.toUpperCase()} QUESTIONS (${questions.length})
╚═══════════════════════════════════════════════════════════════╝

${questions.map((q, i) => `${i + 1}. ${q.question}`).join('\n\n')}

─────────────────────────────────────────────────────────────────
💬 Ask me any question above to see the answer!
─────────────────────────────────────────────────────────────────
`.trim();
  }

  /**
   * Get stats
   */
  getStats(): string {
    const categories = new Set(HARDCODED_INTERVIEW_DATABASE.map(q => q.category));
    const categoryStats = Array.from(categories).map(cat => {
      const count = HARDCODED_INTERVIEW_DATABASE.filter(q => q.category === cat).length;
      return `  ${cat}: ${count} questions`;
    });

    return `
╔═══════════════════════════════════════════════════════════════╗
║ 📊 INTERVIEW DATABASE STATS
╚═══════════════════════════════════════════════════════════════╝

Total Questions: ${HARDCODED_INTERVIEW_DATABASE.length}
Total Categories: ${categories.size}
Questions Answered This Session: ${this.questionHistory.length}

╔═══════════════════════════════════════════════════════════════╗
║ 📚 BREAKDOWN BY CATEGORY
╚═══════════════════════════════════════════════════════════════╝

${categoryStats.join('\n')}

─────────────────────────────────────────────────────────────────
⚡ All answers are HARDCODED for instant responses!
─────────────────────────────────────────────────────────────────
`.trim();
  }
}

// Export singleton instance
export const instantInterviewHandler = new InstantInterviewHandler();
