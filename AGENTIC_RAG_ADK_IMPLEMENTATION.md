# 🤖 Enhanced Agentic RAG with ADK Multi-Agent Patterns

## Overview

This document describes the **Enhanced Agentic RAG System** that implements Google Agent Development Kit (ADK) patterns for intelligent multi-agent orchestration.

---

## Key Improvements from Previous Version

### ❌ Previous Issues (Simple Version)
- Generic search term extraction picking up stop words ("what", "explain", "is")
- Answers going off-topic (asked about A2A, got XAI answer)
- No conditional routing logic
- Limited orchestration capabilities
- Half answers with truncation

### ✅ Enhanced Version Solutions
- **Intelligent search term extraction** with stop word filtering
- **Focused answer generation** that stays on topic
- **Conditional orchestration** based on query complexity
- **Multiple processing strategies** (SIMPLE, MULTI_TOPIC, DEEP_SEQUENTIAL, PARALLEL_SEARCH)
- **Complete answers** with NO truncation
- **Proper ADK patterns** implemented

---

## ADK Patterns Implemented

### 1. Agent Hierarchy (Parent-Child Relationships)

```python
class CustomOrchestrator(BaseAgent):
    def __init__(self, kb_manager):
        # Parent agent manages all sub-agents
        self.coordinator = CoordinatorAgent()
        self.searcher = SearchAgent()
        self.retriever = RetrievalAgent(kb_manager)
        self.analyzer = AnalysisAgent()
        self.synthesizer = SynthesisAgent()
```

**ADK Pattern**: Parent agents manage child agent lifecycle and coordination

### 2. Shared State (Session State Pattern)

```python
@dataclass
class AgentContext:
    """Shared state for agent communication (ADK pattern)"""
    query: str
    strategy: str = ""
    search_terms: List[str] = field(default_factory=list)
    documents: List[Dict] = field(default_factory=list)
    analyses: List[Dict] = field(default_factory=list)
    answer: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_state(self, key: str, value: Any):
        """Set state value (simulates ctx.session.state)"""
        self.metadata[key] = value
```

**ADK Pattern**: Agents communicate through shared session state

### 3. LLM Agents (Thinking Components)

```python
class CoordinatorAgent(BaseAgent):
    """LLM Agent - Decides processing strategy"""
    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            instruction="""You are the Coordinator Agent. Analyze the query and decide the optimal strategy.

            Strategies:
            - SIMPLE: Single concept, direct answer
            - MULTI_TOPIC: Multiple topics to combine
            - DEEP_SEQUENTIAL: Complex query needing step-by-step analysis
            - PARALLEL_SEARCH: Broad query benefiting from concurrent searches

            Return ONLY the strategy name."""
        )
```

**ADK Pattern**: Non-deterministic, LLM-driven reasoning agents

### 4. Workflow Agents (Deterministic Orchestration)

```python
class SequentialAgent:
    """Workflow Agent - Sequential execution pattern"""
    def run(self, ctx: AgentContext) -> AgentContext:
        for agent in self.sub_agents:
            ctx = agent.run(ctx)
        return ctx

class ParallelAgent:
    """Workflow Agent - Parallel execution pattern"""
    def run(self, ctx: AgentContext) -> AgentContext:
        with ThreadPoolExecutor(max_workers=len(self.sub_agents)) as executor:
            futures = [executor.submit(agent.run, ctx) for agent in self.sub_agents]
            for future in futures:
                future.result()
        return ctx
```

**ADK Pattern**: Predefined, deterministic execution flows

### 5. Custom Agent (Conditional Logic)

```python
class CustomOrchestrator(BaseAgent):
    """Custom Agent - Intelligent orchestration with conditional logic"""
    def run(self, ctx: AgentContext) -> AgentContext:
        # Step 1: Decide strategy
        ctx = self.coordinator.run(ctx)

        # Step 2: Extract search terms
        ctx = self.searcher.run(ctx)

        # Step 3: Retrieve documents
        ctx = self.retriever.run(ctx)

        # Step 4: Conditional orchestration based on strategy
        if ctx.strategy == "SIMPLE":
            ctx = self.synthesizer.run(ctx)

        elif ctx.strategy == "MULTI_TOPIC":
            # Parallel analysis of multiple topics
            all_analyses = []
            for topic, docs in topic_groups.items():
                temp_ctx = AgentContext(query=f"{ctx.query} (focusing on {topic})", documents=docs)
                temp_ctx = self.analyzer.run(temp_ctx)
                all_analyses.extend(temp_ctx.analyses)
            ctx.analyses = all_analyses
            ctx = self.synthesizer.run(ctx)

        elif ctx.strategy == "DEEP_SEQUENTIAL":
            ctx = self.analyzer.run(ctx)
            ctx = self.synthesizer.run(ctx)

        elif ctx.strategy == "PARALLEL_SEARCH":
            # Concurrent processing
            ...
```

**ADK Pattern**: Custom orchestration logic with conditional flows

---

## Agent Architecture

### 1. CoordinatorAgent (LLM Agent)
**Role**: Strategy selection
**Input**: User query
**Output**: Strategy decision (SIMPLE, MULTI_TOPIC, DEEP_SEQUENTIAL, PARALLEL_SEARCH)

### 2. SearchAgent (LLM Agent)
**Role**: Optimal term extraction
**Input**: User query
**Output**: List of meaningful search terms (filtering stop words)

**Improvements**:
- Extracts technical terms and acronyms
- Ignores generic words ("what", "how", "explain")
- Includes full forms of acronyms
- Examples given in instruction

### 3. RetrievalAgent (Workflow Agent)
**Role**: Knowledge base search
**Input**: Search terms
**Output**: Ranked documents
**Pattern**: Deterministic retrieval workflow

### 4. AnalysisAgent (LLM Agent)
**Role**: Deep document analysis
**Input**: Documents + Query
**Output**: Key insights per document
**Used in**: DEEP_SEQUENTIAL and MULTI_TOPIC strategies

### 5. SynthesisAgent (LLM Agent)
**Role**: Comprehensive answer generation
**Input**: Query + Documents/Analyses
**Output**: Complete, focused answer

**Improvements**:
- Strong focus on answering exact question asked
- Explicitly instructed to stay on topic
- Uses top 5 documents for better coverage
- NO TRUNCATION requirement in instruction

### 6. CustomOrchestrator (Custom Agent)
**Role**: Intelligent routing and execution
**Input**: User query
**Output**: Complete result with answer, sources, metadata

**Conditional Logic**:
- SIMPLE → Direct synthesis
- MULTI_TOPIC → Group by category, analyze each
- DEEP_SEQUENTIAL → Analyze then synthesize
- PARALLEL_SEARCH → Concurrent processing

---

## Processing Strategies

### SIMPLE Strategy
**Use Case**: Single concept queries ("What is X?")
**Flow**:
1. Extract search terms
2. Retrieve documents
3. Direct synthesis

### MULTI_TOPIC Strategy
**Use Case**: Comparing multiple topics ("X vs Y")
**Flow**:
1. Extract multiple search terms
2. Retrieve documents
3. Group documents by category/topic
4. Analyze each group in parallel
5. Synthesize combined answer

### DEEP_SEQUENTIAL Strategy
**Use Case**: Complex queries needing step-by-step analysis
**Flow**:
1. Extract search terms
2. Retrieve documents
3. **Analyze each document** for key insights
4. Synthesize from analyses (not raw docs)

### PARALLEL_SEARCH Strategy
**Use Case**: Broad queries benefiting from concurrent processing
**Flow**:
1. Extract search terms
2. Retrieve documents
3. Split documents into groups
4. **Analyze groups in parallel**
5. Merge analyses
6. Synthesize final answer

---

## Best Practices Implemented

### 1. Clear Agent Responsibilities
✅ Each agent has focused, single-purpose role
✅ Descriptive names and detailed instructions
✅ Well-defined inputs and outputs

### 2. Explicit State Contracts
✅ `output_key` pattern via metadata
✅ Documented state keys (`search_terms_extracted`, `documents_retrieved`, etc.)
✅ Type-safe state access via `AgentContext`

### 3. Instruction Clarity
✅ Detailed instructions with examples
✅ Tool usage guidance (for search terms)
✅ Format expectations (comma-separated, no stop words)
✅ Behavioral constraints (NO TRUNCATION, stay on topic)

### 4. Hierarchy Design
✅ CustomOrchestrator is parent
✅ All specialist agents are children
✅ Logical task decomposition

### 5. Error Handling
✅ Fallback mechanisms in each agent
✅ State checks before processing
✅ Graceful degradation

---

## File Structure

```
rag_app/
├── agentic_rag_enhanced.py      # Enhanced multi-agent system
├── agentic_rag_simple.py        # Simplified version (older)
├── agentic_rag_app.py           # Attempted full ADK SDK (blocked)
├── knowledge_base_manager_v2.py # KB parsing and search
└── ultimate_adk_langchain_pipeline.py # Expansion pipeline
```

---

## Running the System

### Start Server

```bash
cd /home/user/AI_INTERVIEW/rag_app
python agentic_rag_enhanced.py
```

Server starts on: `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET http://localhost:8000/api/health
```

Response:
```json
{
    "status": "healthy",
    "system": "Enhanced Multi-Agent Agentic RAG",
    "agents": ["Coordinator", "Search", "Retrieval", "Analysis", "Synthesis"],
    "orchestration": ["Sequential", "Parallel", "Conditional"],
    "total_documents": 4194
}
```

#### Query
```bash
POST http://localhost:8000/api/query
Content-Type: application/json

{
    "question": "What is MCP protocol?",
    "top_k": 5
}
```

Response:
```json
{
    "answer": "...",  // Complete, focused answer
    "sources": [...],  // Top 5 documents with FULL content
    "metadata": {
        "strategy": "SIMPLE",
        "search_terms": ["MCP protocol", "MCP"],
        "documents_found": 10,
        "analyses_performed": 0
    }
}
```

---

## Comparison: Before vs After

### Search Term Extraction

**Before**:
- Query: "What is MCP protocol?"
- Terms: ["What", "protocol", "does"]
- ❌ Generic stop words, no meaningful terms

**After**:
- Query: "What is MCP protocol?"
- Terms: ["MCP protocol", "MCP"]
- ✅ Technical terms, acronyms extracted

### Answer Quality

**Before**:
- Query: "Explain A2A protocol"
- Answer: "Explainable AI (XAI) refers to methods..."
- ❌ Wrong topic!

**After**:
- Query: "Explain A2A protocol in ADK"
- Answer: "The A2A (Agent-to-Agent) Protocol in ADK defines a standardized way for different AI agents to communicate..."
- ✅ Correct, focused answer

### Orchestration

**Before**:
- Single strategy: Always same processing
- No conditional logic
- Limited to simple queries

**After**:
- 4 strategies: SIMPLE, MULTI_TOPIC, DEEP_SEQUENTIAL, PARALLEL_SEARCH
- Conditional routing based on query type
- Handles simple to complex queries

---

## ADK Patterns Summary

| Pattern | Implementation | ADK Equivalent |
|---------|---------------|----------------|
| **LLM Agents** | CoordinatorAgent, SearchAgent, AnalysisAgent, SynthesisAgent | `LlmAgent` with model, instruction, tools |
| **Workflow Agents** | SequentialAgent, ParallelAgent | `SequentialAgent`, `ParallelAgent` |
| **Custom Agent** | CustomOrchestrator | Extends `BaseAgent` with `_run_async_impl` |
| **Shared State** | AgentContext with metadata | `ctx.session.state` |
| **Agent Hierarchy** | Parent-child via initialization | `sub_agents` parameter |
| **Conditional Flow** | if/elif in CustomOrchestrator.run() | Custom agent implementation |

---

## Future Enhancements

1. **LoopAgent Pattern**: Implement iterative refinement
2. **Callback Hooks**: Add `before_model_callback`, `after_tool_call`
3. **LLM-Driven Delegation**: Use `transfer_to_agent()` function calls
4. **Structured Output**: Add `input_schema`/`output_schema`
5. **Full ADK SDK**: When environment supports, migrate to `google.adk`

---

## Testing

### Test Queries

```bash
# Simple query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'

# Multi-topic query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare MCP and A2A protocols", "top_k": 5}'

# Deep analysis query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do transformers work in neural networks?", "top_k": 5}'
```

### Expected Behavior

- ✅ Coordinator selects appropriate strategy
- ✅ Search extracts meaningful terms (no stop words)
- ✅ Retrieval finds relevant documents
- ✅ Synthesis provides focused, complete answer
- ✅ No truncation in responses
- ✅ Metadata shows strategy, terms, doc count

---

## Key Takeaways

1. **ADK patterns enable sophisticated orchestration** without full SDK
2. **Conditional routing improves answer quality** dramatically
3. **Clear agent responsibilities** make debugging easier
4. **Shared state enables complex flows** with minimal coupling
5. **Instruction engineering is critical** for LLM agents
6. **Fallback mechanisms** ensure robustness

---

## References

- **ADK Documentation**: llms-full (1).txt (from user)
- **Code**: `rag_app/agentic_rag_enhanced.py`
- **Knowledge Base**: 4,194 entries from `knowledge_base.ts`
- **Model**: Gemini 1.5 Flash

---

**System Status**: ✅ Running on http://localhost:8000
**Total Documents**: 4,194
**Agents**: 6 (1 orchestrator, 5 specialists)
**Strategies**: 4 (SIMPLE, MULTI_TOPIC, DEEP_SEQUENTIAL, PARALLEL_SEARCH)
**ADK Patterns**: 6 implemented
