/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * HARDCODED MOCK INTERVIEW DATABASE
 * All questions and answers are pre-programmed for instant responses
 */

export interface InterviewQA {
  question: string;
  answer: string;
  category: string;
  keywords: string[];
}

export const HARDCODED_INTERVIEW_DATABASE: InterviewQA[] = [
  // JAVASCRIPT FUNDAMENTALS
  {
    question: "What is closure in JavaScript?",
    answer: `A closure is a function that has access to variables in its outer (enclosing) lexical scope, even after the outer function has returned.

Example:
\`\`\`javascript
function outer() {
  let count = 0;
  return function inner() {
    count++;
    return count;
  }
}
const counter = outer();
console.log(counter()); // 1
console.log(counter()); // 2
\`\`\`

Key points:
- Inner function retains access to outer function's variables
- Creates private variables
- Used in callbacks, event handlers, and module patterns`,
    category: "JavaScript",
    keywords: ["closure", "scope", "lexical", "function", "javascript"]
  },
  {
    question: "Explain event loop in JavaScript",
    answer: `The event loop is how JavaScript handles asynchronous operations despite being single-threaded.

Process:
1. Call Stack - executes synchronous code
2. Web APIs - handle async operations (setTimeout, fetch, etc.)
3. Callback Queue - holds completed async callbacks
4. Event Loop - moves callbacks from queue to stack when stack is empty

Example flow:
\`\`\`javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
console.log('3');
// Output: 1, 3, 2
\`\`\`

The event loop constantly checks if the call stack is empty and pushes callbacks from the queue.`,
    category: "JavaScript",
    keywords: ["event loop", "async", "asynchronous", "callback", "queue", "stack"]
  },
  {
    question: "What is the difference between let, const, and var?",
    answer: `Key differences:

**var:**
- Function-scoped
- Hoisted (initialized as undefined)
- Can be redeclared
- Not block-scoped

**let:**
- Block-scoped
- Hoisted but not initialized (temporal dead zone)
- Cannot be redeclared in same scope
- Can be reassigned

**const:**
- Block-scoped
- Hoisted but not initialized
- Cannot be redeclared or reassigned
- Must be initialized at declaration
- Objects/arrays can be mutated (reference is constant)

Best practice: Use const by default, let when reassignment needed, avoid var.`,
    category: "JavaScript",
    keywords: ["let", "const", "var", "scope", "hoisting", "variables"]
  },
  {
    question: "What is 'this' keyword in JavaScript?",
    answer: `'this' refers to the object that is executing the current function.

Rules:
1. **In methods**: this = owner object
2. **Alone**: this = global object (window in browsers)
3. **In functions**: this = global object (strict mode: undefined)
4. **In events**: this = element that received the event
5. **Arrow functions**: this = lexically inherited from parent scope

Examples:
\`\`\`javascript
const obj = {
  name: 'John',
  regular: function() { console.log(this.name); },
  arrow: () => { console.log(this.name); }
};
obj.regular(); // 'John'
obj.arrow(); // undefined (this from parent scope)
\`\`\`

Methods to set this: call(), apply(), bind()`,
    category: "JavaScript",
    keywords: ["this", "context", "bind", "call", "apply", "arrow function"]
  },
  {
    question: "What is promise in JavaScript?",
    answer: `A Promise is an object representing the eventual completion or failure of an asynchronous operation.

States:
- **Pending**: initial state
- **Fulfilled**: operation completed successfully
- **Rejected**: operation failed

Syntax:
\`\`\`javascript
const promise = new Promise((resolve, reject) => {
  if (success) {
    resolve(value);
  } else {
    reject(error);
  }
});

promise
  .then(result => console.log(result))
  .catch(error => console.error(error))
  .finally(() => console.log('Done'));
\`\`\`

Benefits:
- Avoids callback hell
- Better error handling
- Chainable with .then()
- Can use async/await syntax`,
    category: "JavaScript",
    keywords: ["promise", "async", "await", "then", "catch", "asynchronous"]
  },

  // REACT
  {
    question: "What is React and why use it?",
    answer: `React is a JavaScript library for building user interfaces, created by Facebook.

Key features:
- **Component-based**: Reusable UI pieces
- **Virtual DOM**: Fast rendering through diffing
- **Unidirectional data flow**: Predictable state management
- **JSX**: JavaScript + XML syntax
- **Rich ecosystem**: Large community and tools

Why use React:
✓ Fast rendering with Virtual DOM
✓ Reusable components
✓ Large community and resources
✓ SEO-friendly with SSR (Next.js)
✓ React Native for mobile apps
✓ Strong developer tools
✓ Maintained by Meta/Facebook`,
    category: "React",
    keywords: ["react", "library", "virtual dom", "component", "jsx"]
  },
  {
    question: "What are React hooks?",
    answer: `Hooks are functions that let you use state and lifecycle features in functional components.

Common hooks:

**useState**: Manage state
\`\`\`javascript
const [count, setCount] = useState(0);
\`\`\`

**useEffect**: Side effects and lifecycle
\`\`\`javascript
useEffect(() => {
  // Run on mount and updates
  return () => {}; // Cleanup
}, [dependencies]);
\`\`\`

**useContext**: Access context
**useRef**: Reference DOM elements or persist values
**useMemo**: Memoize expensive calculations
**useCallback**: Memoize functions
**useReducer**: Complex state logic

Rules:
1. Only call at top level
2. Only call from React functions
3. Custom hooks must start with "use"`,
    category: "React",
    keywords: ["hooks", "usestate", "useeffect", "react", "functional component"]
  },
  {
    question: "What is the difference between props and state?",
    answer: `**Props (Properties):**
- Passed from parent to child
- Read-only (immutable)
- Used for component configuration
- Controlled by parent component

\`\`\`javascript
<Child name="John" age={25} />
\`\`\`

**State:**
- Managed within component
- Mutable (can be changed)
- Used for component data that changes
- Controlled by component itself

\`\`\`javascript
const [count, setCount] = useState(0);
\`\`\`

Key differences:
- Props are external, state is internal
- Props are immutable, state is mutable
- Props flow down, state stays local (unless lifted)
- Changing props comes from parent, changing state uses setState`,
    category: "React",
    keywords: ["props", "state", "component", "react", "data"]
  },
  {
    question: "What is Virtual DOM?",
    answer: `Virtual DOM is a lightweight JavaScript representation of the actual DOM.

How it works:
1. **Render**: Component creates Virtual DOM tree
2. **Diff**: React compares new Virtual DOM with previous version
3. **Reconciliation**: Calculate minimal changes needed
4. **Update**: Apply only necessary changes to real DOM

Benefits:
✓ **Performance**: Batch updates, minimize DOM operations
✓ **Efficiency**: Only update what changed
✓ **Abstraction**: Write declarative code
✓ **Cross-platform**: Enable React Native

Example:
\`\`\`javascript
// You write:
<div>{count}</div>

// React creates Virtual DOM
{type: 'div', props: {children: count}}

// React efficiently updates real DOM
\`\`\``,
    category: "React",
    keywords: ["virtual dom", "dom", "reconciliation", "diff", "performance"]
  },
  {
    question: "What is useEffect and how does it work?",
    answer: `useEffect is a hook for side effects in functional components. It combines componentDidMount, componentDidUpdate, and componentWillUnmount.

Syntax:
\`\`\`javascript
useEffect(() => {
  // Side effect code
  return () => {
    // Cleanup function
  };
}, [dependencies]);
\`\`\`

Dependency array behaviors:
- **No array**: Runs after every render
- **Empty []**: Runs once on mount
- **[dep1, dep2]**: Runs when dependencies change

Common use cases:
- Fetching data
- Subscriptions
- Timers
- DOM manipulation
- Event listeners

Example:
\`\`\`javascript
useEffect(() => {
  const timer = setInterval(() => console.log('tick'), 1000);
  return () => clearInterval(timer); // Cleanup
}, []); // Run once
\`\`\``,
    category: "React",
    keywords: ["useeffect", "hook", "lifecycle", "side effect", "cleanup"]
  },

  // NODE.JS
  {
    question: "What is Node.js?",
    answer: `Node.js is a JavaScript runtime built on Chrome's V8 engine that executes JavaScript code outside the browser.

Key features:
- **Event-driven**: Non-blocking I/O model
- **Single-threaded**: With event loop for async operations
- **NPM**: Largest package ecosystem
- **Fast**: V8 engine compiles JS to machine code
- **Cross-platform**: Windows, Linux, macOS

Use cases:
✓ REST APIs and microservices
✓ Real-time applications (chat, gaming)
✓ Streaming applications
✓ Command-line tools
✓ Server-side rendering

NOT ideal for:
✗ CPU-intensive operations
✗ Heavy computation tasks

Architecture: Single-threaded event loop + Worker pool for blocking operations`,
    category: "Node.js",
    keywords: ["nodejs", "runtime", "javascript", "backend", "server"]
  },
  {
    question: "Explain Node.js event loop",
    answer: `The event loop is how Node.js handles asynchronous operations on a single thread.

Phases (in order):
1. **Timers**: Execute setTimeout/setInterval callbacks
2. **Pending callbacks**: I/O callbacks deferred to next loop
3. **Idle, prepare**: Internal use only
4. **Poll**: Retrieve new I/O events, execute callbacks
5. **Check**: Execute setImmediate() callbacks
6. **Close callbacks**: Handle close events (socket.on('close'))

Process:
\`\`\`javascript
┌───────────────────────┐
┌─>│        timers         │
│  └──────────┬────────────┘
│  ┌──────────┴────────────┐
│  │  pending callbacks    │
│  └──────────┬────────────┘
│  ┌──────────┴────────────┐
│  │    idle, prepare      │
│  └──────────┬────────────┘
│  ┌──────────┴────────────┐
│  │        poll           │
│  └──────────┬────────────┘
│  ┌──────────┴────────────┐
│  │        check          │
│  └──────────┬────────────┘
│  ┌──────────┴────────────┐
└──┤   close callbacks     │
   └───────────────────────┘
\`\`\`

Key: Non-blocking I/O allows handling many connections concurrently.`,
    category: "Node.js",
    keywords: ["event loop", "nodejs", "async", "timers", "poll", "setimmediate"]
  },
  {
    question: "What is Express.js?",
    answer: `Express is a minimal and flexible Node.js web application framework.

Features:
- **Routing**: Define URL endpoints and HTTP methods
- **Middleware**: Process requests before handlers
- **Template engines**: Render dynamic HTML
- **Error handling**: Centralized error management
- **Static files**: Serve CSS, images, JS files

Basic example:
\`\`\`javascript
const express = require('express');
const app = express();

// Middleware
app.use(express.json());

// Routes
app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});

app.post('/api/users', (req, res) => {
  const user = req.body;
  res.status(201).json(user);
});

// Error handling
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message });
});

app.listen(3000);
\`\`\`

Benefits: Fast development, robust routing, large ecosystem`,
    category: "Node.js",
    keywords: ["express", "expressjs", "framework", "routing", "middleware", "nodejs"]
  },

  // DATA STRUCTURES
  {
    question: "What is a hash table?",
    answer: `A hash table (hash map) is a data structure that maps keys to values using a hash function.

How it works:
1. Hash function converts key to array index
2. Store value at that index
3. Handle collisions (chaining or open addressing)

Time complexity:
- Average: O(1) for insert, delete, search
- Worst: O(n) with many collisions

Example:
\`\`\`javascript
class HashTable {
  constructor(size = 50) {
    this.table = new Array(size);
  }

  hash(key) {
    let hash = 0;
    for (let char of key) {
      hash += char.charCodeAt(0);
    }
    return hash % this.table.length;
  }

  set(key, value) {
    const index = this.hash(key);
    this.table[index] = value;
  }

  get(key) {
    const index = this.hash(key);
    return this.table[index];
  }
}
\`\`\`

Use cases: Caching, databases, unique data storage`,
    category: "Data Structures",
    keywords: ["hash table", "hash map", "data structure", "hashing", "o(1)"]
  },
  {
    question: "What is the difference between array and linked list?",
    answer: `**Array:**
- Contiguous memory locations
- Fixed size (in some languages)
- O(1) random access by index
- O(n) insertion/deletion (except at end)
- Better cache locality

**Linked List:**
- Scattered memory locations
- Dynamic size
- O(n) access by index
- O(1) insertion/deletion (with reference)
- Poor cache locality

Comparison:

| Operation | Array | Linked List |
|-----------|-------|-------------|
| Access    | O(1)  | O(n)        |
| Search    | O(n)  | O(n)        |
| Insert    | O(n)  | O(1)*       |
| Delete    | O(n)  | O(1)*       |

*With reference to node

Choose array when:
- Need random access
- Size is known
- Memory is continuous

Choose linked list when:
- Frequent insertions/deletions
- Unknown size
- No random access needed`,
    category: "Data Structures",
    keywords: ["array", "linked list", "data structure", "comparison", "complexity"]
  },
  {
    question: "Explain binary search tree",
    answer: `A Binary Search Tree (BST) is a tree data structure where each node has at most two children.

Properties:
- Left subtree contains only nodes with keys < parent's key
- Right subtree contains only nodes with keys > parent's key
- Both subtrees must also be BSTs
- No duplicate nodes

Time complexity:
- Average: O(log n) search, insert, delete
- Worst: O(n) when tree is skewed

Example:
\`\`\`javascript
class TreeNode {
  constructor(val) {
    this.val = val;
    this.left = null;
    this.right = null;
  }
}

class BST {
  insert(root, val) {
    if (!root) return new TreeNode(val);

    if (val < root.val) {
      root.left = this.insert(root.left, val);
    } else {
      root.right = this.insert(root.right, val);
    }
    return root;
  }

  search(root, val) {
    if (!root || root.val === val) return root;
    if (val < root.val) return this.search(root.left, val);
    return this.search(root.right, val);
  }
}
\`\`\`

Traversals: Inorder, Preorder, Postorder, Level-order`,
    category: "Data Structures",
    keywords: ["binary search tree", "bst", "tree", "data structure", "log n"]
  },

  // ALGORITHMS
  {
    question: "Explain quicksort algorithm",
    answer: `Quicksort is a divide-and-conquer sorting algorithm.

Algorithm:
1. Choose a pivot element
2. Partition: elements < pivot to left, > pivot to right
3. Recursively sort left and right partitions

Time complexity:
- Best/Average: O(n log n)
- Worst: O(n²) when already sorted
- Space: O(log n) for recursion stack

Implementation:
\`\`\`javascript
function quickSort(arr, low = 0, high = arr.length - 1) {
  if (low < high) {
    const pi = partition(arr, low, high);
    quickSort(arr, low, pi - 1);
    quickSort(arr, pi + 1, high);
  }
  return arr;
}

function partition(arr, low, high) {
  const pivot = arr[high];
  let i = low - 1;

  for (let j = low; j < high; j++) {
    if (arr[j] < pivot) {
      i++;
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }
  [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
  return i + 1;
}
\`\`\`

Advantages: In-place, fast on average, cache-efficient`,
    category: "Algorithms",
    keywords: ["quicksort", "sorting", "algorithm", "divide and conquer", "pivot"]
  },
  {
    question: "What is dynamic programming?",
    answer: `Dynamic Programming (DP) is an optimization technique that solves complex problems by breaking them into simpler subproblems.

Key concepts:
1. **Overlapping subproblems**: Same subproblems solved multiple times
2. **Optimal substructure**: Optimal solution contains optimal solutions to subproblems

Approaches:
**Top-down (Memoization):**
- Recursive with caching
\`\`\`javascript
const memo = {};
function fib(n) {
  if (n <= 1) return n;
  if (memo[n]) return memo[n];
  memo[n] = fib(n-1) + fib(n-2);
  return memo[n];
}
\`\`\`

**Bottom-up (Tabulation):**
- Iterative with table
\`\`\`javascript
function fib(n) {
  const dp = [0, 1];
  for (let i = 2; i <= n; i++) {
    dp[i] = dp[i-1] + dp[i-2];
  }
  return dp[n];
}
\`\`\`

Common problems: Fibonacci, knapsack, longest common subsequence, coin change`,
    category: "Algorithms",
    keywords: ["dynamic programming", "dp", "memoization", "optimization", "algorithm"]
  },
  {
    question: "Explain breadth-first search (BFS)",
    answer: `BFS is a graph traversal algorithm that explores vertices level by level.

Algorithm:
1. Start at root node
2. Visit all neighbors at current depth
3. Move to next depth level
4. Use queue data structure

Time: O(V + E) - vertices + edges
Space: O(V) - for queue

Implementation:
\`\`\`javascript
function bfs(graph, start) {
  const visited = new Set();
  const queue = [start];
  const result = [];

  visited.add(start);

  while (queue.length > 0) {
    const vertex = queue.shift();
    result.push(vertex);

    for (let neighbor of graph[vertex]) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push(neighbor);
      }
    }
  }

  return result;
}
\`\`\`

Use cases:
- Shortest path in unweighted graph
- Level-order tree traversal
- Finding connected components
- Web crawling`,
    category: "Algorithms",
    keywords: ["bfs", "breadth first search", "graph", "traversal", "queue"]
  },
  {
    question: "Explain depth-first search (DFS)",
    answer: `DFS is a graph traversal algorithm that explores as far as possible along each branch before backtracking.

Algorithm:
1. Start at root node
2. Explore each branch completely before backtracking
3. Use stack (or recursion)

Time: O(V + E) - vertices + edges
Space: O(V) - for stack/recursion

Implementation (Recursive):
\`\`\`javascript
function dfs(graph, start, visited = new Set()) {
  visited.add(start);
  console.log(start);

  for (let neighbor of graph[start]) {
    if (!visited.has(neighbor)) {
      dfs(graph, neighbor, visited);
    }
  }
}
\`\`\`

Implementation (Iterative):
\`\`\`javascript
function dfsIterative(graph, start) {
  const visited = new Set();
  const stack = [start];

  while (stack.length > 0) {
    const vertex = stack.pop();
    if (!visited.has(vertex)) {
      visited.add(vertex);
      console.log(vertex);
      stack.push(...graph[vertex]);
    }
  }
}
\`\`\`

Use cases: Topological sorting, cycle detection, pathfinding, maze solving`,
    category: "Algorithms",
    keywords: ["dfs", "depth first search", "graph", "traversal", "recursion", "stack"]
  },

  // SYSTEM DESIGN
  {
    question: "What is REST API?",
    answer: `REST (Representational State Transfer) is an architectural style for designing networked applications.

Key principles:
1. **Stateless**: Each request contains all needed information
2. **Client-Server**: Separation of concerns
3. **Cacheable**: Responses can be cached
4. **Uniform Interface**: Standard HTTP methods
5. **Layered System**: Client can't tell if connected directly to server

HTTP Methods:
- GET: Retrieve resource (idempotent)
- POST: Create resource
- PUT: Update/replace resource (idempotent)
- PATCH: Partial update
- DELETE: Remove resource (idempotent)

Example endpoints:
\`\`\`
GET    /api/users          - Get all users
GET    /api/users/123      - Get user 123
POST   /api/users          - Create user
PUT    /api/users/123      - Update user 123
DELETE /api/users/123      - Delete user 123
\`\`\`

Best practices:
✓ Use nouns, not verbs in endpoints
✓ Use plural nouns
✓ Return proper status codes (200, 201, 404, 500)
✓ Version your API (/api/v1/)`,
    category: "System Design",
    keywords: ["rest", "api", "http", "restful", "endpoints", "crud"]
  },
  {
    question: "What is database indexing?",
    answer: `An index is a data structure that improves the speed of data retrieval operations on a database table.

How it works:
- Creates a separate structure with pointers to table rows
- Like a book index - quickly find content without scanning all pages
- Trades storage space and write speed for read speed

Types:
**Primary Index**: On primary key (unique, automatically created)
**Secondary Index**: On non-primary columns
**Composite Index**: Multiple columns
**Unique Index**: Ensures column uniqueness

Example (SQL):
\`\`\`sql
-- Create index
CREATE INDEX idx_email ON users(email);

-- Without index: O(n) - full table scan
-- With index: O(log n) - B-tree traversal

-- Composite index
CREATE INDEX idx_name_age ON users(last_name, first_name);
\`\`\`

Pros:
✓ Faster SELECT queries
✓ Faster sorting and joining

Cons:
✗ Slower INSERT/UPDATE/DELETE
✗ Extra storage space
✗ Index maintenance overhead

When to use: High-read, low-write columns; WHERE, JOIN, ORDER BY clauses`,
    category: "System Design",
    keywords: ["index", "indexing", "database", "performance", "sql", "optimization"]
  },
  {
    question: "Explain microservices architecture",
    answer: `Microservices is an architectural style that structures an application as a collection of small, independent services.

Characteristics:
- **Independently deployable**: Each service can be deployed separately
- **Organized around business capabilities**: Each service = business function
- **Decentralized**: Own database per service
- **Communicate via APIs**: HTTP/REST, message queues
- **Technology diversity**: Different languages/frameworks per service

Example:
\`\`\`
Monolith:          Microservices:
┌─────────┐        ┌────┐ ┌────┐ ┌────┐
│         │        │Auth│ │User│ │Order│
│  All    │   →    │Svc │ │Svc │ │ Svc│
│  Code   │        └────┘ └────┘ └────┘
│         │          │      │      │
└─────────┘        ┌──────────────┐
                   │   API Gateway│
                   └──────────────┘
\`\`\`

Advantages:
✓ Independent scaling
✓ Fault isolation
✓ Technology flexibility
✓ Faster deployment
✓ Team autonomy

Disadvantages:
✗ Complex deployment
✗ Network latency
✗ Data consistency challenges
✗ Distributed system complexity`,
    category: "System Design",
    keywords: ["microservices", "architecture", "distributed", "system design", "api"]
  },
  {
    question: "What is caching and when to use it?",
    answer: `Caching is storing frequently accessed data in fast-access storage to reduce database/API calls.

Types:
**Client-side**: Browser cache, localStorage
**CDN**: Static assets (images, CSS, JS)
**Application**: Redis, Memcached
**Database**: Query result cache

Caching strategies:

**1. Cache-Aside (Lazy Loading)**
\`\`\`javascript
async function getData(key) {
  let data = cache.get(key);
  if (!data) {
    data = await database.get(key);
    cache.set(key, data, TTL);
  }
  return data;
}
\`\`\`

**2. Write-Through**
- Write to cache and database simultaneously

**3. Write-Behind**
- Write to cache, async write to database

**4. Refresh-Ahead**
- Proactively refresh before expiration

When to use caching:
✓ Read-heavy workloads
✓ Expensive computations
✓ Frequently accessed data
✓ Static/semi-static content
✓ API rate limiting

Eviction policies:
- LRU (Least Recently Used)
- LFU (Least Frequently Used)
- FIFO (First In First Out)
- TTL (Time To Live)`,
    category: "System Design",
    keywords: ["caching", "cache", "redis", "memcached", "performance", "optimization"]
  },

  // DATABASE
  {
    question: "What is the difference between SQL and NoSQL?",
    answer: `**SQL (Relational):**
- Structured schema (tables, rows, columns)
- ACID transactions
- Relationships via foreign keys
- Vertical scaling
- Examples: PostgreSQL, MySQL, Oracle

**NoSQL (Non-relational):**
- Flexible schema
- BASE (Basically Available, Soft state, Eventually consistent)
- No joins (data denormalized)
- Horizontal scaling
- Examples: MongoDB, Cassandra, Redis

Types of NoSQL:
- **Document**: MongoDB (JSON documents)
- **Key-Value**: Redis (simple key-value)
- **Column-family**: Cassandra (wide columns)
- **Graph**: Neo4j (nodes and relationships)

When to use SQL:
✓ Complex queries and joins
✓ ACID compliance needed
✓ Structured data
✓ Financial systems

When to use NoSQL:
✓ Massive scale
✓ Flexible schema
✓ High performance reads/writes
✓ Real-time analytics

Comparison:
| Feature | SQL | NoSQL |
|---------|-----|-------|
| Schema | Fixed | Flexible |
| Scaling | Vertical | Horizontal |
| Transactions | ACID | BASE |
| Joins | Yes | No |`,
    category: "Database",
    keywords: ["sql", "nosql", "database", "mongodb", "postgresql", "mysql"]
  },
  {
    question: "What is database normalization?",
    answer: `Normalization is organizing database tables to reduce redundancy and improve data integrity.

Normal Forms:

**1NF (First Normal Form):**
- Atomic values (no arrays/lists)
- Each row unique
- No repeating groups

**2NF (Second Normal Form):**
- Must be in 1NF
- No partial dependencies
- All non-key columns depend on entire primary key

**3NF (Third Normal Form):**
- Must be in 2NF
- No transitive dependencies
- Non-key columns depend only on primary key

Example:

Unnormalized:
\`\`\`
| OrderID | Customer | Products |
|---------|----------|----------|
| 1       | John     | A,B,C    | ❌
\`\`\`

3NF:
\`\`\`
Orders:               OrderItems:
| OrderID | Customer | | OrderID | Product |
|---------|----------| |---------|---------|
| 1       | John     | | 1       | A       |
                      | 1       | B       |
                      | 1       | C       | ✓
\`\`\`

Advantages:
✓ Reduces redundancy
✓ Improves data integrity
✓ Easier updates

Disadvantages:
✗ More joins (slower queries)
✗ Complex queries

Denormalization: Intentionally add redundancy for performance`,
    category: "Database",
    keywords: ["normalization", "database", "normal form", "sql", "redundancy"]
  },

  // TESTING
  {
    question: "What is the difference between unit testing and integration testing?",
    answer: `**Unit Testing:**
- Tests individual components in isolation
- Fast execution
- Mock external dependencies
- High code coverage
- Developer-written

Example:
\`\`\`javascript
// Unit test
test('add function', () => {
  expect(add(2, 3)).toBe(5);
});
\`\`\`

**Integration Testing:**
- Tests multiple components together
- Slower execution
- Real dependencies or test doubles
- Tests component interaction
- Catches integration issues

Example:
\`\`\`javascript
// Integration test
test('API endpoint creates user', async () => {
  const response = await request(app)
    .post('/api/users')
    .send({ name: 'John' });
  expect(response.status).toBe(201);
  const user = await db.users.findOne({ name: 'John' });
  expect(user).toBeDefined();
});
\`\`\`

Testing pyramid:
\`\`\`
    /\\
   /E2E\\       - Few, slow, expensive
  /──────\\
 /Integration\\  - Medium number
/──────────────\\
/  Unit Tests   \\ - Many, fast, cheap
\`\`\`

Both are essential for comprehensive testing strategy.`,
    category: "Testing",
    keywords: ["unit testing", "integration testing", "testing", "jest", "test"]
  },

  // SECURITY
  {
    question: "What is JWT and how does it work?",
    answer: `JWT (JSON Web Token) is a compact, self-contained way to securely transmit information between parties as a JSON object.

Structure:
\`\`\`
header.payload.signature
\`\`\`

**Header**: Algorithm and token type
\`\`\`json
{
  "alg": "HS256",
  "typ": "JWT"
}
\`\`\`

**Payload**: Claims (user data)
\`\`\`json
{
  "sub": "1234567890",
  "name": "John Doe",
  "exp": 1516239022
}
\`\`\`

**Signature**: Verify token integrity
\`\`\`
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
\`\`\`

Flow:
1. User logs in with credentials
2. Server creates JWT and sends to client
3. Client stores JWT (localStorage/cookie)
4. Client sends JWT in Authorization header
5. Server verifies JWT signature

Example:
\`\`\`javascript
// Create
const token = jwt.sign({ userId: 123 }, 'secret', { expiresIn: '1h' });

// Verify
const decoded = jwt.verify(token, 'secret');
\`\`\`

Advantages: Stateless, scalable, works across domains
Disadvantages: Can't revoke until expiration, larger than session ID`,
    category: "Security",
    keywords: ["jwt", "json web token", "authentication", "auth", "token", "security"]
  },
  {
    question: "What is CORS?",
    answer: `CORS (Cross-Origin Resource Sharing) is a security mechanism that allows or restricts web applications from making requests to a different domain.

Same-Origin Policy:
- Browser security feature
- Blocks requests to different origin (protocol + domain + port)
- Prevents malicious scripts from accessing sensitive data

Example:
\`\`\`
https://example.com:443 → https://api.example.com:443 ❌ Different subdomain
https://example.com:443 → http://example.com:443 ❌ Different protocol
https://example.com:443 → https://example.com:8080 ❌ Different port
\`\`\`

CORS Headers:
\`\`\`javascript
// Server response
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Credentials: true
\`\`\`

Implementation (Express):
\`\`\`javascript
const cors = require('cors');

app.use(cors({
  origin: 'https://example.com',
  credentials: true
}));
\`\`\`

Preflight request:
- Browser sends OPTIONS request first
- Server responds with allowed methods/headers
- Then actual request is sent

Security: Only allow trusted origins, not '*' in production`,
    category: "Security",
    keywords: ["cors", "cross origin", "security", "same origin", "browser"]
  },

  // GIT
  {
    question: "What is the difference between git merge and git rebase?",
    answer: `**Git Merge:**
- Creates a new merge commit
- Preserves complete history
- Non-destructive operation
- Shows when branches were merged

\`\`\`bash
git checkout main
git merge feature
\`\`\`

Result:
\`\`\`
    A---B---C feature
   /         \\
D---E---F---G---M main (merge commit)
\`\`\`

**Git Rebase:**
- Rewrites commit history
- Creates linear history
- Moves commits to new base
- Cleaner history

\`\`\`bash
git checkout feature
git rebase main
\`\`\`

Result:
\`\`\`
D---E---F---G main
             \\
              A'---B'---C' feature (rebased)
\`\`\`

When to use:
**Merge**:
✓ Public branches
✓ Preserving history important
✓ Team collaboration

**Rebase**:
✓ Local branches
✓ Clean history desired
✓ Before creating PR

⚠️ Golden Rule: Never rebase public branches others are working on!`,
    category: "Git",
    keywords: ["git", "merge", "rebase", "version control", "history"]
  },

  // WEB PERFORMANCE
  {
    question: "How do you optimize website performance?",
    answer: `**Frontend Optimization:**

1. **Minimize bundle size**
   - Code splitting
   - Tree shaking
   - Remove unused dependencies
   - Lazy loading

2. **Optimize images**
   - Use WebP format
   - Compress images
   - Responsive images (srcset)
   - Lazy load images

3. **Reduce network requests**
   - Bundle files
   - CSS sprites
   - Use CDN
   - HTTP/2 multiplexing

4. **Caching**
   - Browser caching
   - Service workers
   - CDN caching

5. **Code optimization**
   - Minify CSS/JS
   - Remove console.logs
   - Use production builds
   - Debounce/throttle events

**React-specific:**
\`\`\`javascript
// Code splitting
const Component = lazy(() => import('./Component'));

// Memoization
const MemoComponent = memo(Component);
const memoValue = useMemo(() => compute(a, b), [a, b]);
const memoCallback = useCallback(() => {}, []);

// Virtual scrolling for long lists
<VirtualList items={10000} />
\`\`\`

**Backend:**
- Database indexing
- Query optimization
- Caching (Redis)
- Load balancing
- Compression (gzip)

**Metrics to track:**
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Total Blocking Time (TBT)`,
    category: "Performance",
    keywords: ["performance", "optimization", "web", "speed", "loading", "bundle"]
  },

  // TYPESCRIPT
  {
    question: "What is TypeScript and why use it?",
    answer: `TypeScript is a statically typed superset of JavaScript that compiles to plain JavaScript.

Key features:
- **Static typing**: Catch errors at compile time
- **Interfaces**: Define contracts for objects
- **Generics**: Reusable type-safe code
- **Enums**: Named constants
- **Type inference**: Automatic type detection
- **Modern JS features**: ES6+ support

Example:
\`\`\`typescript
// Type annotations
function greet(name: string): string {
  return \`Hello, \${name}\`;
}

// Interface
interface User {
  id: number;
  name: string;
  email?: string; // Optional
}

// Generics
function identity<T>(arg: T): T {
  return arg;
}

// Type guards
function isString(value: unknown): value is string {
  return typeof value === 'string';
}
\`\`\`

Benefits:
✓ Early error detection
✓ Better IDE autocomplete
✓ Self-documenting code
✓ Easier refactoring
✓ Large codebase maintainability

Drawbacks:
✗ Learning curve
✗ Additional build step
✗ More verbose code

When to use: Medium to large projects, team collaboration, long-term maintenance`,
    category: "TypeScript",
    keywords: ["typescript", "types", "static typing", "javascript", "type safety"]
  },

  // CSS
  {
    question: "What is CSS Flexbox?",
    answer: `Flexbox is a one-dimensional layout method for arranging items in rows or columns.

Container properties:
\`\`\`css
.container {
  display: flex;
  flex-direction: row | column;
  justify-content: flex-start | center | flex-end | space-between | space-around;
  align-items: flex-start | center | flex-end | stretch;
  flex-wrap: nowrap | wrap;
  gap: 10px;
}
\`\`\`

Item properties:
\`\`\`css
.item {
  flex-grow: 1;      /* Grow to fill space */
  flex-shrink: 1;    /* Shrink if needed */
  flex-basis: 200px; /* Initial size */
  flex: 1 1 200px;   /* Shorthand */
  align-self: center; /* Override align-items */
  order: 2;          /* Change order */
}
\`\`\`

Common patterns:

**Center everything:**
\`\`\`css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
}
\`\`\`

**Responsive columns:**
\`\`\`css
.container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}
.item {
  flex: 1 1 300px; /* Min 300px, grows to fill */
}
\`\`\`

Use cases: Navigation bars, card layouts, centering, equal-height columns`,
    category: "CSS",
    keywords: ["flexbox", "css", "layout", "flex", "responsive"]
  },

  // ADDITIONAL COMMON QUESTIONS
  {
    question: "What is async/await?",
    answer: `Async/await is syntactic sugar for working with Promises, making asynchronous code look synchronous.

Syntax:
\`\`\`javascript
async function fetchUser(id) {
  try {
    const response = await fetch(\`/api/users/\${id}\`);
    const user = await response.json();
    return user;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
\`\`\`

Key points:
- **async**: Function always returns a Promise
- **await**: Pauses execution until Promise resolves
- **Error handling**: Use try/catch blocks
- **Parallel execution**: Use Promise.all()

\`\`\`javascript
// Sequential (slow)
const user = await fetchUser(1);
const posts = await fetchPosts(1);

// Parallel (fast)
const [user, posts] = await Promise.all([
  fetchUser(1),
  fetchPosts(1)
]);
\`\`\`

Advantages:
✓ More readable than .then() chains
✓ Better error handling with try/catch
✓ Easier debugging
✓ Works with any Promise

Common mistake: Forgetting await makes function continue without waiting!`,
    category: "JavaScript",
    keywords: ["async", "await", "promise", "asynchronous", "javascript"]
  },
  {
    question: "What is the difference between null and undefined?",
    answer: `**undefined:**
- Variable declared but not assigned
- Default function return value
- Missing object properties
- Missing function parameters

\`\`\`javascript
let x;
console.log(x); // undefined

function test() {}
console.log(test()); // undefined

const obj = {};
console.log(obj.name); // undefined
\`\`\`

**null:**
- Intentional absence of value
- Must be assigned explicitly
- Represents "no value"

\`\`\`javascript
let x = null; // Explicitly set to null
\`\`\`

Comparison:
\`\`\`javascript
console.log(typeof undefined); // "undefined"
console.log(typeof null);      // "object" (historical bug!)

console.log(undefined == null);  // true (loose equality)
console.log(undefined === null); // false (strict equality)

console.log(undefined + 5); // NaN
console.log(null + 5);      // 5 (null coerces to 0)
\`\`\`

Best practices:
- Use undefined for uninitialized/missing values
- Use null to explicitly represent "no value"
- Always use === for comparison`,
    category: "JavaScript",
    keywords: ["null", "undefined", "javascript", "difference", "types"]
  },
  {
    question: "What is RESTful API design best practices?",
    answer: `**Best Practices:**

1. **Use proper HTTP methods**
\`\`\`
GET    /api/users       - List users
GET    /api/users/123   - Get user
POST   /api/users       - Create user
PUT    /api/users/123   - Replace user
PATCH  /api/users/123   - Update user
DELETE /api/users/123   - Delete user
\`\`\`

2. **Use nouns, not verbs**
✓ GET /api/users
✗ GET /api/getUsers

3. **Use plural nouns**
✓ /api/users
✗ /api/user

4. **Proper status codes**
\`\`\`
200 OK           - Successful GET, PUT, PATCH
201 Created      - Successful POST
204 No Content   - Successful DELETE
400 Bad Request  - Invalid request
401 Unauthorized - Not authenticated
403 Forbidden    - Not authorized
404 Not Found    - Resource doesn't exist
500 Server Error - Server error
\`\`\`

5. **Versioning**
\`\`\`
/api/v1/users
\`\`\`

6. **Filtering, sorting, pagination**
\`\`\`
GET /api/users?role=admin&sort=name&page=2&limit=20
\`\`\`

7. **Consistent response format**
\`\`\`json
{
  "data": [...],
  "meta": {
    "page": 1,
    "total": 100
  },
  "error": null
}
\`\`\`

8. **Use HATEOAS (optional)**
\`\`\`json
{
  "id": 123,
  "name": "John",
  "links": {
    "self": "/api/users/123",
    "posts": "/api/users/123/posts"
  }
}
\`\`\``,
    category: "System Design",
    keywords: ["rest", "api", "best practices", "design", "http", "restful"]
  }
];

/**
 * Fast keyword-based search for instant answers
 */
export function findBestMatch(query: string): InterviewQA | null {
  const normalizedQuery = query.toLowerCase().trim();

  // Exact question match
  for (const qa of HARDCODED_INTERVIEW_DATABASE) {
    if (qa.question.toLowerCase() === normalizedQuery) {
      return qa;
    }
  }

  // Partial question match
  for (const qa of HARDCODED_INTERVIEW_DATABASE) {
    if (qa.question.toLowerCase().includes(normalizedQuery) ||
        normalizedQuery.includes(qa.question.toLowerCase())) {
      return qa;
    }
  }

  // Keyword match - find best scoring match
  let bestMatch: InterviewQA | null = null;
  let bestScore = 0;

  for (const qa of HARDCODED_INTERVIEW_DATABASE) {
    let score = 0;
    const queryWords = normalizedQuery.split(/\s+/);

    for (const keyword of qa.keywords) {
      if (normalizedQuery.includes(keyword)) {
        score += 3; // Exact keyword match
      }
      for (const word of queryWords) {
        if (keyword.includes(word) || word.includes(keyword)) {
          score += 1; // Partial word match
        }
      }
    }

    if (score > bestScore && score > 2) { // Minimum threshold
      bestScore = score;
      bestMatch = qa;
    }
  }

  return bestMatch;
}

/**
 * Get all available categories
 */
export function getCategories(): string[] {
  const categories = new Set<string>();
  for (const qa of HARDCODED_INTERVIEW_DATABASE) {
    categories.add(qa.category);
  }
  return Array.from(categories).sort();
}

/**
 * Get questions by category
 */
export function getQuestionsByCategory(category: string): InterviewQA[] {
  return HARDCODED_INTERVIEW_DATABASE.filter(qa =>
    qa.category.toLowerCase() === category.toLowerCase()
  );
}

/**
 * Get random question for practice
 */
export function getRandomQuestion(): InterviewQA {
  const randomIndex = Math.floor(Math.random() * HARDCODED_INTERVIEW_DATABASE.length);
  return HARDCODED_INTERVIEW_DATABASE[randomIndex];
}
