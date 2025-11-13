# Background Knowledge for Understanding Helios Design

**Target Audience**: VLDB reviewers with database systems expertise but limited blockchain/EVM knowledge

**Scope**: Concepts assumed but **not explained** in design.tex

---

## 1. Ethereum Virtual Machine (EVM) Architecture

### 1.1 Stack-Based Execution Model

The EVM is a **stack-based virtual machine** where all computation operates on a 1024-element stack of 256-bit unsigned integers (U256).

**Stack operations**:
- Opcodes pop operands from stack top
- Computation results pushed back onto stack
- No named registers or direct memory addressing

**Example execution**:
```
Initial stack: []
PUSH1 0x05      → Stack: [5]
PUSH1 0x03      → Stack: [5, 3]
ADD             → Pops 3 and 5, computes 8 → Stack: [8]
```

**Performance implications**:
- Every operation requires **stack pointer manipulation**
- Bounds checking on every push/pop (stack overflow/underflow)
- Poor cache locality (indirect addressing through stack pointer)
- Higher instruction count (explicit stack management overhead)

**Contrast with register-based ISAs** (x86, ARM):
- Registers: Direct addressing (`ADD R1, R2 → R3`)
- Stack-based: Indirect addressing (`POP, POP, ADD, PUSH`)

### 1.2 Stack Manipulation Instructions

Critical for understanding shadow stack tracing:

| Opcode | Operation | Effect |
|--------|-----------|--------|
| **DUP1-DUP16** | Duplicate stack item at depth 1-16 | `[a, b] → DUP1 → [a, b, b]` |
| **SWAP1-SWAP16** | Swap top with item at depth 1-16 | `[a, b] → SWAP1 → [b, a]` |
| **POP** | Discard top item | `[a, b] → POP → [a]` |

**Why these matter**:
- DUP/SWAP do not produce new values, only rearrange stack
- Shadow stack must mirror these operations to maintain LSN correspondence
- Frequent in EVM bytecode (compiler-generated boilerplate)

### 1.3 Memory and Storage Model

**Memory** (transient, transaction-scoped):
- Byte-addressable linear array
- Cleared after transaction completes
- Opcodes: MLOAD, MSTORE, MSTORE8
- Gas cost: Quadratic expansion (first 724 bytes = 3 gas/word, grows quadratically)

**Storage** (persistent, global state):
- Key-value store: U256 → U256 mapping
- Survives transaction boundaries
- Opcodes: SLOAD, SSTORE
- Gas cost: Cold access (first read) = 2,100 gas; warm access = 100 gas

**Why gas costs are dynamic**:
- Memory expansion depends on current memory size (runtime state)
- Storage costs depend on access history (cold/warm)
- Cannot be determined at compile time → must be computed during execution

### 1.4 Control Flow Semantics

**JUMP / JUMPI**:
- **JUMP**: Unconditional jump to PC (program counter)
  - Pops target address from stack
  - Target must be marked by JUMPDEST opcode (static validation)

- **JUMPI**: Conditional jump
  - Pops condition and target from stack
  - Jumps only if condition ≠ 0

**Why jump targets can be dynamic**:
```
Solidity switch-case compiles to jump table:
PUSH jump_table_base    // Base address
CALLDATALOAD            // Load function selector (runtime value)
ADD                     // Compute target = base + selector
JUMP                    // Jump to computed address
```

**Implication for guards**: Cached jump target may not match actual execution if input differs

### 1.5 Call Frame Hierarchy

**Frame-spawning opcodes**:
- **CALL**: External call to another contract
  - Creates child frame with isolated memory
  - Shares storage (world state)
  - Pops: gas, target address, value, input offset/size, output offset/size (7 args)

- **DELEGATECALL**: Call another contract's code in current context
  - Uses caller's storage
  - Pops 6 args (no value transfer)

- **CREATE / CREATE2**: Deploy new contract
  - Executes constructor bytecode
  - Returns deployed contract address

**Call depth**: Maximum 1024 nested frames (prevents stack overflow attacks)

**Relevance to Helios**: Each frame gets separate PathLog; TxPlan records sequence of frames

---

## 2. Gas Mechanism

### 2.1 Purpose and Design

**Problem**: EVM is Turing-complete → potential for infinite loops
**Solution**: Gas metering forces resource accountability

**Gas mechanics**:
- User specifies **gas limit** (maximum willing to pay)
- Each opcode deducts gas
- Execution aborts if gas exhausted (**out-of-gas exception**, OOG)
- Remaining gas refunded to user

**Economic role**:
- Prevents DoS attacks (attacker must pay for computation)
- Aligns incentives (validators compensated for execution cost)

### 2.2 Static vs Dynamic Gas Costs

**Static costs** (compile-time determinable):
- ADD, MUL, SUB: 3-5 gas (fixed)
- SSTORE to zero slot: 20,000 gas (fixed)
- Most opcodes have static base costs

**Dynamic costs** (runtime-dependent):
- **Memory expansion**:
  - Cost = 3 × new_words + (new_words²) / 512
  - Depends on current memory size (state variable)

- **SSTORE**:
  - Cold access (never touched): 20,000 gas
  - Warm access (recently touched): 100 gas
  - Refund on delete: -15,000 gas
  - Requires tracking access history (EIP-2929)

- **CALL**:
  - Base: 100 gas
  - If transferring value: +9,000 gas
  - If account doesn't exist: +25,000 gas
  - Depends on runtime state inspection

**Why this constrains optimization**:
- Cannot optimize away SLOAD/SSTORE (dynamic costs + side effects)
- Cannot eliminate CALL (external observable effects)
- Full-trace systems must log these operations → high overhead
- **Helios insight**: Only trace stack dependencies (static operations)

### 2.3 Gas Forwarding and Delimiters

**Gas forwarding** (line 40 in design.tex mentions this):
- When calling child contract via CALL/CREATE, parent must specify gas allocation
- Child gets forwarded gas limit (capped by parent's remaining gas)
- Unused gas returned to parent
- **Delimiter property**: CREATE/CREATE2 must query exact gas balance before forwarding

**Six gas delimiters** (design.tex lines 38-40):
1. **GAS**: Pushes current remaining gas onto stack (explicit query)
2. **RETURN/STOP/REVERT**: Finalization requires gas check
3. **CREATE/CREATE2**: Must read gas for forwarding

**Why only these six**:
- Other opcodes don't expose gas balance to program logic
- Between delimiters, gas balance is unobservable → can batch deduction

---

## 3. Blockchain Node Types and Workload Characteristics

### 3.1 Full Node (Online Mode Target)

**Responsibilities**:
- Validate new blocks in real-time
- Maintain UTXO/state tree
- Relay transactions to peers
- Participate in consensus (if validator)

**Workload characteristics**:
- **Unpredictable transactions**: Never-seen contracts, novel inputs
- **Low latency requirement**: Block time = 12 seconds (Ethereum)
- **Diverse call patterns**: Token transfers, DeFi swaps, NFT mints
- **Cold start problem**: New contracts have no execution history

**Why Online mode needs speculation**:
- Cannot predict execution paths ahead of time
- Must optimize for cache hit rate while handling misses gracefully
- Trade occasional fallback cost for zero profiling overhead on hot paths

### 3.2 Archive Node (Replay Mode Target)

**Responsibilities**:
- Store complete historical state (all blocks since genesis)
- Serve RPC queries for blockchain explorers, analytics
- Re-execute historical blocks for state reconstruction

**Workload characteristics**:
- **Deterministic transactions**: Re-executing known blocks
- **High throughput requirement**: Process millions of historical transactions
- **Batch processing**: Sync entire blockchain (years of data)
- **Known execution patterns**: All paths traced during original execution

**Why Replay mode achieves 100% cache hit**:
- TxPlans provide exact PathDigest sequence
- No speculation needed (deterministic replay)
- Zero guard overhead
- Optimized for throughput over latency

**VLDB analogy**:
- Full node ≈ OLTP (latency-sensitive, unpredictable)
- Archive node ≈ OLAP (throughput-optimized, known query patterns)

---

## 4. Static Single Assignment (SSA) Form

### 4.1 SSA Definition

**Core principle**: Each variable assigned exactly once

**Example transformation**:
```
Non-SSA:                SSA:
x = 3                   x₁ = 3
x = x + 5               x₂ = x₁ + 5
y = x * 2               y₁ = x₂ * 2
```

**Properties**:
- Unique definition point for each value
- Explicit data flow dependencies
- Simplifies optimization (no aliasing ambiguity)

### 4.2 Why SSA Simplifies Optimization

**Constant folding without SSA**:
```
x = 3
x = 5      // Overwrites previous assignment
y = x + 2  // Which x? Need dataflow analysis
```

**Constant folding with SSA**:
```
x₁ = 3     // Dead code (no uses)
x₂ = 5
y₁ = x₂ + 2  // Unambiguous: x₂ = 5 → y₁ = 7
```

**Benefits for Helios**:
- LSN (log sequence number) acts as SSA subscript
- Each opcode produces unique LSN → natural SSA form
- `stack_in = [lsn_8, lsn_1]` explicitly encodes dependencies

### 4.3 Topological Order

**Definition**: Ordering where all dependencies of a node appear before the node

**Example graph**:
```
lsn_1: PUSH 3
lsn_2: PUSH 5
lsn_3: ADD (depends on lsn_1, lsn_2)
lsn_4: PUSH 2
lsn_5: MUL (depends on lsn_3, lsn_4)

Valid topological orders:
  [1, 2, 3, 4, 5]  or  [2, 1, 3, 4, 5]  or  [1, 4, 2, 3, 5]
```

**Why Helios needs this** (line 120 in design.tex):
- Traced Interpreter executes nodes in topological order
- Ensures operands computed before use
- Register file: `registers[lsn]` populated before dependent nodes read it

**Algorithm**: Kahn's algorithm or DFS-based topological sort (O(V + E))

---

## 5. Standard Compiler Optimization Techniques

Design.tex describes EVM-specific implementations but assumes familiarity with underlying techniques.

### 5.1 Constant Folding (Generic)

**Goal**: Evaluate expressions with all-constant operands at compile time

**Example**:
```
x = 3 * 5 + 2       // Compute at compile time
→ x = 17            // Emit single constant
```

**Algorithm** (design.tex line 60 describes EVM variant):
1. Identify constant sources (literals, PUSH in EVM)
2. Propagate constants through expression tree
3. Evaluate pure operations (no side effects)
4. Iterate until fixed point (no more foldable expressions)

**Pure operation**: No observable effects besides return value
- EVM examples: ADD, MUL, XOR (pure)
- EVM counter-examples: SLOAD, CALL (side effects)

### 5.2 Dead Code Elimination (Generic)

**Goal**: Remove computations whose results are never used

**Example**:
```
x = expensive_computation()  // Computed but never read
y = 42
return y
→ y = 42; return y  // x eliminated
```

**Algorithm** (design.tex line 62 describes EVM variant):
1. Identify **live** values (used by side-effecting operations or outputs)
2. Mark dependencies of live values as live (backward propagation)
3. Delete all unmarked (dead) nodes

**Side effect** (formal definition):
- Operation whose execution has observable consequences beyond return value
- Examples: I/O, memory writes, state modification, control flow

**EVM side effects** (design.tex assumes this is known):
- Storage: SLOAD, SSTORE
- Memory: MLOAD, MSTORE
- Events: LOG0-LOG4
- External interaction: CALL, CREATE
- Control flow: JUMP, JUMPI
- Termination: RETURN, REVERT

### 5.3 Common Subexpression Elimination (Generic)

**Goal**: Reuse results of identical computations

**Example**:
```
a = x * y + z
b = x * y + 10      // x * y recomputed
→ temp = x * y
a = temp + z
b = temp + 10
```

**Algorithm** (design.tex line 64 describes EVM variant):
1. Compute canonical signature for each operation (opcode + ordered inputs)
2. Hash table: signature → first occurrence
3. Redirect duplicates to first occurrence
4. Delete redundant nodes

**EVM-specific challenge**: Must handle constants vs variables in signatures
- `ADD(CONST_3, VAR_5)` ≠ `ADD(VAR_3, VAR_5)`

---

## 6. EVM Execution Details

### 6.1 Program Counter (PC)

**Definition**: Index into bytecode array indicating next instruction to execute

**Example bytecode**:
```
PC   Opcode       Mnemonic
0    0x60 0x03    PUSH1 3
2    0x60 0x05    PUSH1 5
4    0x01         ADD
5    0x56         JUMP
```

**JUMP semantics**:
1. Pop target PC from stack
2. Verify `bytecode[target] == JUMPDEST` (0x5B)
3. Set PC = target
4. Continue execution

**Guard validation** (design.tex line 106):
- Cached SsaGraph stores `expected_pc` observed during tracing
- Runtime computes `actual_pc` from current stack state
- Mismatch → fallback (input led to different branch)

### 6.2 Revm's Journal Mechanism

**Revm** (Rust EVM implementation): Underlying interpreter Helios integrates with

**Journal**: Transaction-local change log recording all state modifications
- Storage writes: `(address, key, old_value, new_value)`
- Balance transfers: `(address, Δbalance)`
- Account creation/deletion
- Log emissions (events)

**Transaction atomicity**:
- Modifications buffered in journal during execution
- On success: Commit journal to global state
- On revert/OOG: Discard journal, rollback state

**Helios integration** (design.tex line 96):
- On guard violation or cache miss: `journal.clear()`
- Discards partial work without complex checkpointing
- Re-execution starts with clean pre-transaction state

### 6.3 Why Stack-Based Execution is Slow

Design.tex (line 98) states register-based execution is faster but doesn't explain why.

**Stack overhead breakdown** (per opcode):
1. **Pointer arithmetic**: `stack_ptr -= 2` (for 2 operands)
2. **Bounds checking**:
   - Underflow: `if stack_ptr < 2 then abort`
   - Overflow: `if stack_depth > 1024 then abort`
3. **Indirect memory access**: `operand1 = memory[stack_ptr]`
4. **Cache thrashing**: Stack pointer constantly changes → poor locality

**Register-based execution** (design.tex line 100):
1. **Direct addressing**: `registers[8]` (LSN-indexed array)
2. **No bounds checking**: Array size fixed at graph construction
3. **Sequential access**: Better cache locality
4. **Fewer instructions**: No stack manipulation boilerplate

**Quantitative difference** (typical EVM instruction):
- Stack-based: 10-15 CPU instructions (including checks/pointer updates)
- Register-based: 3-5 CPU instructions (load, compute, store)

---

## 7. Smart Contract Patterns

### 7.1 ERC-20 Token Standard

**Definition**: Fungible token interface standard (like ERC-721 for NFTs)

**Core functions**:
- `transfer(address to, uint256 amount)`: Send tokens
- `balanceOf(address owner)`: Query balance
- `approve(address spender, uint256 amount)`: Authorize spending

**Why this matters for Helios** (design.tex line 26):
- Thousands of ERC-20 tokens deployed with identical logic
- Same bytecode template → same PathDigest
- Different constants (token name, supply) → different DataKey
- **Execution-data separation exploits this**: 1 SsaGraph shared, N ConstantTables

### 7.2 Factory Contract Pattern

**Concept**: Contract that deploys other contracts programmatically

**Example**:
```solidity
contract TokenFactory {
    function createToken(string name, uint256 supply) {
        new ERC20Token(name, supply);  // Deploys new contract
    }
}
```

**CREATE2 opcode** (deterministic deployment):
- Address = hash(deployer, salt, bytecode)
- Same bytecode + salt → same address across chains
- Used for cross-chain contract deployment

**Relevance** (design.tex line 76):
- Factory-deployed contracts share bytecode structure
- Only differ in constructor arguments (embedded as PUSH immediates)
- Graph sharing saves memory (1 graph for 1000s of instances)

### 7.3 Function Selector

**ABI encoding**: Contract calls encode function identity in first 4 bytes of calldata

**Selector computation**:
```
function transfer(address, uint256)
Selector = keccak256("transfer(address,uint256)")[0:4]
         = 0xa9059cbb
```

**CallSig construction** (design.tex line 24):
```
CallSig = code_hash (20 bytes) || selector (4 bytes)
```

**Why this enables prediction**:
- Same contract + same function → likely same execution path
- Different inputs to same function may diverge (e.g., `if (balance > amount)`)
- PML tracks frequency of paths per CallSig

---

## 8. Performance Analysis Concepts

### 8.1 Why Instruction-Level Parallelism (ILP) Fails for EVM

Design.tex (line 13) claims thread synchronization overhead exceeds parallelism gains.

**Background**:
- Modern CPUs execute instructions in ~1 ns
- EVM opcodes (interpreted): ~5-10 ns
- Thread synchronization primitives:
  - Lock acquisition: ~50-100 ns
  - Atomic operations: ~20 ns
  - Context switch: ~1-5 μs

**Parallelism overhead**:
```
Sequential execution of 10 opcodes: 10 × 10 ns = 100 ns

Parallel execution (2 threads):
  - Spawn threads: ~500 ns
  - Execute 5 opcodes/thread: 5 × 10 ns = 50 ns
  - Synchronize results: ~100 ns
  - Join threads: ~500 ns
  Total: ~1150 ns (11× slower)
```

**Full-trace systems** (Forerunner, ParallelEVM):
- Trace memory/storage dependencies → enable ILP
- But: Synchronization cost dominates for short instruction sequences
- **Helios insight**: Skip ILP, optimize sequential execution instead

### 8.2 Cache Thrashing

**Definition**: Frequent cache evictions due to poor access patterns

**Stack-based execution**:
```
Stack base: 0x1000
Stack pointer: 0x1000 + (depth * 32)

Execution trace:
  PUSH → write 0x1020
  PUSH → write 0x1040
  ADD  → read 0x1040, 0x1020, write 0x1020
  PUSH → write 0x1040
  MUL  → read 0x1040, 0x1020, write 0x1020
```
- Random access pattern (pointer chasing)
- Poor spatial locality

**Register-based execution**:
```
Register file: contiguous array 0x2000-0x3000

Execution trace:
  Node 1 → write 0x2008
  Node 2 → write 0x2010
  Node 3 → read 0x2008, 0x2010, write 0x2018
```
- Sequential allocation (LSN-indexed)
- Cache-friendly (prefetcher can predict)

### 8.3 Asynchronous Profiling

**Hot path**: Critical execution path (must be fast)
**Cold path**: Profiling/optimization (can be slow)

**Synchronous profiling** (traditional JIT):
```
Execute → Profile → Optimize → Execute optimized
          ^^^^^^^^^^^^^^^^ Blocks execution
```

**Asynchronous profiling** (Helios):
```
Execute (native) → Result returned
     |
     └─> Profile (async) → Optimize → Cache (for future use)
         ^^^^^^^^^^^^^^^^^ Does not block
```

**Design.tex implication** (line 4):
- "Decoupling of profiling from execution"
- Path Tracer triggered only on cache miss/fallback
- Zero overhead on hot path (cached executions)

---

## 9. FNV-1a Hash Properties

Design.tex (lines 19-22) provides FNV-1a formula but not rationale.

**FNV-1a (Fowler-Noll-Vo) hash**:
```
hash = OFFSET_BASIS  (typically 0xcbf29ce484222325)
For each byte b:
    hash = (hash ⊕ b) × FNV_PRIME  (0x100000001b3)
```

**Properties**:
1. **Incremental**: Update in O(1) per byte
2. **Efficient**: 1 XOR + 1 MUL (no divisions, no loops)
3. **Good distribution**: Low collision rate for sequential data
4. **Non-cryptographic**: Fast but not secure (acceptable for cache indexing)

**Alternatives and why rejected**:
| Hash | Speed | Collision Rate | Incrementality |
|------|-------|----------------|----------------|
| SHA-256 | Slow (crypto) | Excellent | No (requires full input) |
| xxHash | Fast | Excellent | Partial (block-based) |
| FNV-1a | Very fast | Good | Yes (byte-by-byte) |
| CRC32 | Fast | Fair | Yes |

**Helios choice**: FNV-1a prioritizes speed + incrementality over collision resistance

**Collision rate** (empirical):
- For 10,000 distinct execution paths: ~0.1% collision probability
- Acceptable (cache handles collisions with secondary key checks)

---

## Summary: Minimal Prerequisites

**Critical for understanding design.tex**:
1. EVM stack-based architecture and opcodes
2. Gas mechanism (static vs dynamic costs)
3. Memory/storage model
4. Node types (full vs archive)
5. SSA form basics
6. Standard compiler optimizations (constant folding, DCE, CSE)

**Helpful for deeper understanding**:
7. Call frame hierarchy and CALL/CREATE semantics
8. Jump mechanics and dynamic targets
9. Revm's journal-based atomicity
10. ERC-20 tokens and factory patterns
11. Why stack-based execution is slow
12. Performance analysis (ILP overhead, cache effects)

**Advanced (optional)**:
13. FNV-1a hash properties
14. Function selectors and ABI encoding
15. CREATE2 and deterministic deployment

**Estimated reading time**: ~45 minutes for critical sections (1-6)
