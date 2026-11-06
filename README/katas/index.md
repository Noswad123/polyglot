# Shared exercise question library (formerly katas)
[home](../../README.md)

## Overview

A kata is a focused challenge for deliberate, repeatable practice. This is the
front door to the **full existing collection: 37 normalized topic families**, not
just the five curated contracts. The inventory includes 20 question documents
(five curated, 15 draft) and 17 code-only topics needing questions, with 60 current
unverified legacy source artifacts across eight languages. Only six bindings are
active practice. The directory and filenames remain unchanged to preserve links;
there is no requirement to implement every problem in every language.

Start practice with the [Python track](../../practice/python/README.md) or the
[single Rust proof exercise](../../practice/rust/README.md). Preserved code under
[`practice/`](../../practice/) is unverified study material outside the active exercises, not blanks to overwrite or validated
solutions. Discovery never reads, imports, or executes those sources.

## API / Interfaces

The five curated question documents are authoritative for common behavior and
examples. A **binding** supplies a language-qualified exercise ID, native API,
blank path, and native check selector. Intentional binding differences are explicit
(notably Python prints Hello World while Rust returns its text).

| Question / problem ID | Python binding | Rust binding | Readiness |
|---|---|---|---|
| [Hello World](hello_world.md) · `hello-world` | `python/hello` | `rust/hello` | Contract ready; both bindings have native blanks + checks. |
| [Find in String](find_in_string.md) · `find-in-string` | `python/find_in_string` | Pending | Contract ready; Python native blank + checks. |
| [Length of Last Word](lengthOfLastWord.md) · `length-of-last-word` | `python/length_of_last_word` | Pending | Contract ready; Python native blank + checks. |
| [Binary Search](binarySearch.md) · `binary-search` | `python/binary_search` | Pending | Contract ready; Python native blank + checks. |
| [Fibonacci](fibonacci.md) · `fibonacci` | `python/fibonacci` | Pending | Contract ready; Python native blank + checks. |

Readiness terms are distinct:

- **Contract ready:** the shared question specifies inputs, outputs, and edge cases.
- **Native blank + checks:** a catalog binding selects a learner-editable exercise
  and its native harness. A blank is intentionally unsolved, not a passing solution.
- **Solution artifact:** unverified source artifact, possibly partial, empty, or
  accompanied by tests/demos; not proof of a solution or current-contract conformance.
- **Draft:** a registered document needing contract review; discoverable, not
  practice-ready. **Missing:** no question document registered, not missing code.
- **Pending:** no active binding; not an obligation to complete a mastery matrix.

Only Python and Rust have active adapters here: five Python bindings and
`rust/hello`. Go, JavaScript, TypeScript, and other source examples are not newly
active adapters or new exercise implementations. No claim is made that the whole
library has been converted. A question may be curated without a binding; question
status, reference availability, native binding readiness, and a committed reset
baseline are independent. The five linked contracts remain authoritative for common
behavior; general concept explanations remain in Darkness.

## Data Flow

`polyglot questions` defaults to JSON-only stdout; the retained `--json` flag is an
explicit alias. Both emit only an array of metadata objects, without a human
header/footer. The schema is unchanged: `id`, `title`, `question_status`, nullable
`question_doc`, `references` (language/path/nullable note), and `bindings`.
Document and reference paths remain repository-relative.
The legacy JSON `references` key remains for compatibility, with unchanged
language/path/nullable-note entries and no `solutions` alias. Its paths now point
to the mixed `practice/` roots described in the lifecycle guide; the export key
is not a verification claim.

For human browsing, `polyglot questions --pretty` selects an ASCII table, not
pretty-printed JSON. It fits within 80 columns with `Problem ID`, `Question`
(status), `Solutions` (unverified language list, same 18-character width), and `Practice` (runnable native
languages, e.g. `python, rust`; `-` means not converted). There is no duplicate
title column. The footer summarizes 37 topics,
20 docs, 60 solution artifacts, and six native bindings; its legend
distinguishes unverified solutions from native practice languages and explains
how to get details. JSON or `question ID` retains titles, exact native binding IDs,
and full source paths. Mixed or repeated format flags are rejected.

`polyglot question <problem-id>` accepts any registered topic: a curated contract,
a warning plus a draft body, an empty-draft success notice, or metadata/reference
paths without a fabricated prompt when no document is registered. Paths appear
under the `Solutions` heading, not a claim that the code conforms or runs.
`polyglot show <language-qualified-id>` displays that same full Markdown plus the
selected native binding. Language-specific hints stay in the CLI catalog and are
available through `polyglot hint`. The five curated question bodies contain no
solutions or implementation-code hints; drafts may retain legacy inventories and
examples. `list`, `practice`, `start`, `check`, `reset`, `hint`, and `show` still
select only the six active bindings (or supported track targets), not references.
Guessed IDs such as `python/stack` and `python/boggle` block without writes or
branch changes. Metadata listing needs no root files, Git, or tools: this is a
static catalog, not a runtime filesystem audit.

### Conversion procedure

1. Inspect existing prompts, unverified references, and their tests; preserve them.
2. Decide the common contract, examples, edge cases, and any binding differences.
3. Create or promote the `Problem` in `cli/src/library.rs`, explicitly setting its
   status, optional document, and references. Editing Markdown alone never curates
   it. Keep existing filenames stable. Reference labels do not extend the two-language
   native `Language` enum.
4. For practice, add an independent native blank/checks and an `Exercise` binding
   in `cli/src/model.rs` referencing a curated problem, keeping hints there.
5. Add CLI/root fixtures for discovery, full-Markdown display, binding selection,
   and native check behavior. `tests/test_library_inventory.py` independently
   covers all 20 non-index document paths and all 60 legacy source artifacts;
   new in-scope source additions fail the audit until registered. This is coverage,
   not execution or validation of legacy solutions.
6. Review and integrate the canonical blank on local `main` before treating it as
   a reset baseline. New paths are not automatically reset-ready.

## Edge Cases

ASCII examples define the shared string conformance scope; Unicode index/count
units need explicit binding decisions. A legacy checkmark or a source test does
not prove compliance with the new question. In particular, older last-word
references split literal spaces, JavaScript Fibonacci has a different prefix and
length, and some Python references print demos or diagnostics. See each question
for the precise distinctions.

Declared documents must be readable UTF-8 regular files with no symlink components;
missing/unreadable/non-UTF-8/symlink/directory errors block detail with exit `2`.
Empty drafts are allowed (Sudoku is a draft, not missing). Active selection still
requires a curated nonempty contract, validated before automatic branching; native
checks remain document-independent. Question-body edits are read at runtime;
metadata/binding edits require build/install. Reset prerequisites are unchanged:
the four original blanks have local-main baselines; the two newer Python blanks
still need user review and committed integration. No whole-library reset readiness
is implied.

### Remaining conversion queue

These 15 registered **Draft** topics (20 question files total, excluding this
index) are discoverable CLI questions, but not runnable practice bindings.
Resolve their contracts before adding bindings; old status tables are historical,
not readiness declarations. Spiral Matrix and Sudoku have documents but no
reference sources.

| Document | Contract/harness work before conversion |
|---|---|
| [Boggle](boggle.md) · `boggle` | Preserve adjacency/no-cube-reuse rules; resolve uppercase board vs lowercase examples, board shape, and empty inputs. |
| [Integer to Roman](integer_to_Roman.md) · `integer-to-roman` | Resolve the stated zero case, representation/range, and duplicate heading. |
| [Roman to Integer](romanToInteger.md) · `roman-to-integer` | Define valid numerals, zero representation, and invalid-input behavior. |
| [Is Subsequence](isSubsequence.md) · `is-subsequence` | Define ordering, empty inputs, and string scope. |
| [Majority Element](majorityElement.md) · `majority-element` | Define majority threshold and no-majority/empty behavior. |
| [Merge Sorted Array](MergeSortedArray.md) · `merge-sorted-array` | Decide in-place mutation vs returned array, logical lengths, and spare capacity. |
| [Product of Array Except Self](productOfArray.md) · `product-of-array-except-self` | Specify zeros, short inputs, numeric limits, and algorithm constraints. |
| [Reverse Words in a String](reverseWordsInAString.md) · `reverse-words-in-a-string` | Decide whitespace normalization and word definition. |
| [Rotate Array](rotateArray.md) · `rotate-array` | Resolve left vs right rotation, mutation/return, empty arrays, and step bounds. |
| [Scrabble](scrabble.md) · `scrabble` | Define scoring, case, alphabet, and unsupported characters. |
| [Spiral Matrix](spiral_matrix_walk.md) · `spiral-matrix` | Preserve the example; specify rectangular/empty shapes and traversal direction. |
| [Valid Palindrome](validPalindrome.md) · `valid-palindrome` | Define normalization, punctuation, case, and empty behavior. |
| [Sudoku Validator](sudoku_validator.md) · `sudoku-validator` | Currently empty; author the question, board shape, symbols, and validation rules. |
| [Pong / HTTP ping](pong.md) · `pong` | Preserve server comparisons; needs a larger HTTP harness with startup, ports, response, and teardown rules. |
| [Users](users.md) · `users` | Preserve endpoint examples; needs a larger database/HTTP harness with isolation, persistence, validation, and authentication rules. |

### Code-only topics: 17 missing questions

Every row needs a shared question and contract review before a native binding.
Links are source inventory, not verified solutions; no row is practice-ready.

| Topic / problem ID | Current unverified source artifacts |
|---|---|
| Best Time to Buy and Sell Stock · `best-time-to-buy-and-sell-stock` | [TypeScript](../../practice/typescript/bestTimeToBuyAndSellStock.ts) |
| Candy · `candy` | [Python](../../practice/python/soutions/candy.py), [TypeScript](../../practice/typescript/candy.ts) |
| Container With Most Water · `container-with-most-water` | [Python](../../practice/python/soutions/container_with_most_water.py) |
| Find Pivot Index · `find-pivot-index` | [Python](../../practice/python/soutions/find_pivot_index.py) **empty placeholder, not implemented**; [TypeScript](../../practice/typescript/findPivotIndex.ts) |
| Gas Station · `gas-station` | [TypeScript](../../practice/typescript/gasStation.ts) |
| H-Index · `h-index` | [TypeScript](../../practice/typescript/hIndex.ts) |
| Insert Delete GetRandom · `insert-delete-get-random` | [TypeScript](../../practice/typescript/insertDeleteGetRandom.ts) |
| Jump Game · `jump-game` | [TypeScript](../../practice/typescript/jumpGame.ts) |
| Longest Common Prefix · `longest-common-prefix` | [TypeScript](../../practice/typescript/longestCommonPrefix.ts) |
| Queue · `queue` | [Python](../../practice/python/soutions/queue.py) |
| Remove Duplicates from Sorted Array · `remove-duplicates-from-sorted-array` | [TypeScript](../../practice/typescript/removeDuplicatesFromSortedArray.ts) |
| Remove Element · `remove-element` | [TypeScript](../../practice/typescript/removeElement.ts) |
| Stack · `stack` | [Python](../../practice/python/soutions/stack.py) |
| Text Justification · `text-justification` | [TypeScript](../../practice/typescript/textJustification.ts) |
| Trapping Rain Water · `trapping-rain-water` | [TypeScript](../../practice/typescript/trappingRainWater.ts) |
| Two Sum · `two-sum` | [TypeScript](../../practice/typescript/twoSum.ts) |
| Zigzag Conversion · `zigzag-conversion` | [TypeScript](../../practice/typescript/zigzagConversion.ts) |

### Solutions for documented topics (unverified)

Together with the code-only table, these links enumerate all 60 current source
artifacts: Python 21, TypeScript 27, JavaScript 3, Go 3, Rust 1, Bash 2, Lua 2,
and Lisp 1. Tests/specs, manifests, generated files, playgrounds, and backlog ideas
are excluded. Multiple in-file variants (stocks, Jump Game, Remove Duplicates)
belong to one topic family, not separate topics/artifacts. Historical deleted Rust
Pong is not restored or counted. No legacy source is executed or validated here.

| Registered topic | Current unverified source artifacts |
|---|---|
| `hello-world` | [Python](../../practice/python/soutions/hello_world.py), [JavaScript](../../practice/javascript/helloWorld.js), [Go](../../practice/go/helloWorld.go), [Bash](../../practice/bash/hello_world.sh), [Lua](../../practice/lua/helloWorld.lua), [Lisp](../../practice/lisp/hello-world.lisp) |
| `find-in-string` | [Python](../../practice/python/soutions/find_in_string.py), [TypeScript](../../practice/typescript/findTheIndexOfTheFirstOccurrenceInAString.ts) |
| `length-of-last-word` | [Python](../../practice/python/soutions/length_of_last_word.py), [TypeScript](../../practice/typescript/lengthOfLastWord.ts) |
| `binary-search` | [Python](../../practice/python/soutions/binary_search.py) |
| `fibonacci` | [Python](../../practice/python/soutions/fibonacci.py), [JavaScript](../../practice/javascript/fibonacci.js) |
| `boggle` | [Python](../../practice/python/soutions/boggle.py), [TypeScript](../../practice/typescript/boggle.ts) |
| `integer-to-roman` | [Python](../../practice/python/soutions/integer_to_roman.py), [TypeScript](../../practice/typescript/integerToRoman.ts) |
| `roman-to-integer` | [Python](../../practice/python/soutions/roman_to_integer.py), [TypeScript](../../practice/typescript/romanToInteger.ts) |
| `is-subsequence` | [Python](../../practice/python/soutions/is_subsequence.py), [TypeScript](../../practice/typescript/isSubsequence.ts) |
| `majority-element` | [Python](../../practice/python/soutions/majority_element.py), [TypeScript](../../practice/typescript/majorityElement.ts) |
| `merge-sorted-array` | [Python](../../practice/python/soutions/merge_sorted_array.py), [TypeScript](../../practice/typescript/mergeSortedArray.ts) |
| `product-of-array-except-self` | [Python](../../practice/python/soutions/product_of_array_except_self.py), [TypeScript](../../practice/typescript/productOfArrayExceptSelf.ts) |
| `reverse-words-in-a-string` | [Python](../../practice/python/soutions/reverse_words_in_a_string.py), [TypeScript](../../practice/typescript/reverseWordsInAString.ts) |
| `rotate-array` | [Python](../../practice/python/soutions/rotate_array.py), [TypeScript](../../practice/typescript/roateArray.ts) (existing filename) |
| `scrabble` | [TypeScript](../../practice/typescript/scrabble.ts) |
| `spiral-matrix` | None: document only |
| `valid-palindrome` | [TypeScript](../../practice/typescript/validPalindrome.ts) |
| `sudoku-validator` | None: empty draft document only |
| `pong` | [Python](../../practice/python/soutions/pong.py), [JavaScript](../../practice/javascript/pong.js), [Go](../../practice/go/pong.go), [Bash](../../practice/bash/pong.sh), [Lua](../../practice/lua/pong.lua) |
| `users` | [Python](../../practice/python/soutions/users.py), [Go](../../practice/go/users/main.go), [Rust](../../practice/rust/solutions/users/src/main.rs) |

## Example usage

From the repository root, with the shared CLI available:

```sh
polyglot questions --pretty
polyglot question binary-search
polyglot question boggle
polyglot question stack
polyglot question two-sum
polyglot show python/binary_search
polyglot hint python/binary_search
polyglot practice python/binary_search
```

For machine export, use either JSON form (examples only):

```sh
polyglot questions > /tmp/polyglot-questions.json
polyglot questions --json
```

Reading a question is not starting an exercise. Follow the track and lifecycle
docs for branch, checking, and safe reset requirements.

## Related files

- [Full topic metadata](../../cli/src/library.rs), [native bindings](../../cli/src/model.rs),
  [independent inventory audit](../../tests/test_library_inventory.py), [CLI entry point](../../cli/src/main.rs)
- [Python track](../../practice/python/README.md), [Rust track](../../practice/rust/README.md)
- [Exercise lifecycle](../exercises.md), [CLI guide](../rust-cli.md)
- [Collection layout and execution limits](../exercises.md#collection-layout-and-execution-limits):
  native support, removed legacy tests, and server/database risks; no whole-collection verification.
- Solution directories: [Python](../../practice/python/soutions/), [TypeScript](../../practice/typescript/), [JavaScript](../../practice/javascript/)

## Katas to add

The following backlog is preserved as ideas and external resources, **not required
assignments, active bindings, or a promise to implement every language**. Some
topics overlap existing reference documents and still need contract review.

### Assorted
    - Bowling
    - Poker
    - Fizzbuzz
    - PrimeFactor
    - Read a list of numbers and print only the even ones.
    - Running pointers
    - Linked List cycle or intersection detection
    - Divide and conquer or decrease and conquer
    - Recursive Problems that can be memoized or solved tabularly
    - Using FIFO and LIFO on onion layer problems
    - Binary search variations: left == right, left < right, left > right by 1 or more
    - counting or bucket sort
    - using min or max heap to find top k items
    - sliding, tumbling or fixed window
    - hash maps for quick lookups or duplicate detection
    - greedy algorithms
    - dealing with intervals
    - Dfs/Bfs serially or in parallel
    - Permutation and combination (repetitions and ordering using backtracking, loops or the choose vs. not choose strategy)
    - graph coloring
    - topological sort
    - shortest path variations
    - connected components

### Array
    - [Two Sum](https://leetcode.com/problems/two-sum/)
    - [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)
    - [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/)
    - [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/)
    - [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/)
    - [Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/)
    - [Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)
    - [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)
    - [3 Sum](https://leetcode.com/problems/3sum/)
    - [Container With Most Water](https://leetcode.com/problems/container-with-most-water/)
### Binary
    - [Sum of Two Integers](https://leetcode.com/problems/sum-of-two-integers/)
    - [Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
    - [Counting Bits](https://leetcode.com/problems/counting-bits/)
    - [Missing Number](https://leetcode.com/problems/missing-number/)
    - [Reverse Bits](https://leetcode.com/problems/reverse-bits/)
### Dynamic Programming
    - [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/)
    - [Coin Change](https://leetcode.com/problems/coin-change/)
    - [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/)
    - [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/)
    - [Word Break Problem](https://leetcode.com/problems/word-break/)
    - [Combination Sum](https://leetcode.com/problems/combination-sum-iv/)
    - [House Robber](https://leetcode.com/problems/house-robber/)
    - [House Robber II](https://leetcode.com/problems/house-robber-ii/)
    - [Decode Ways](https://leetcode.com/problems/decode-ways/)
    - [Unique Paths](https://leetcode.com/problems/unique-paths/)
    - [Jump Game](https://leetcode.com/problems/jump-game/)
### Graph
    - [Clone Graph](https://leetcode.com/problems/clone-graph/)
    - [Course Schedule](https://leetcode.com/problems/course-schedule/)
    - [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/)
    - [Number of Islands](https://leetcode.com/problems/number-of-islands/)
    - [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/)
    - [Alien Dictionary (Leetcode Premium)](https://leetcode.com/problems/alien-dictionary/)
    - [Graph Valid Tree (Leetcode Premium)](https://leetcode.com/problems/graph-valid-tree/)
    - [Number of Connected Components in an Undirected Graph (Leetcode Premium)](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/)
### Interval
    - [Insert Interval](https://leetcode.com/problems/insert-interval/)
    - [Merge Intervals](https://leetcode.com/problems/merge-intervals/)
    - [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/)
    - [Meeting Rooms (Leetcode Premium)](https://leetcode.com/problems/meeting-rooms/)
    - [Meeting Rooms II (Leetcode Premium)](https://leetcode.com/problems/meeting-rooms-ii/)
### Linked List
    - [Reverse a Linked List](https://leetcode.com/problems/reverse-linked-list/)
    - [Detect Cycle in a Linked List](https://leetcode.com/problems/linked-list-cycle/)
    - [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/)
    - [Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/)
    - [Remove Nth Node From End Of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)
    - [Reorder List](https://leetcode.com/problems/reorder-list/)
### Matrix
    - [Set Matrix Zeroes](https://leetcode.com/problems/set-matrix-zeroes/)
    - [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/)
    - [Rotate Image](https://leetcode.com/problems/rotate-image/)
    - [Word Search](https://leetcode.com/problems/word-search/)
### String
    - [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)
    - [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)
    - [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)
    - [Valid Anagram](https://leetcode.com/problems/valid-anagram/)
    - [Group Anagrams](https://leetcode.com/problems/group-anagrams/)
    - [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)
    - [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/)
    - [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/)
    - [Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/)
    - [Encode and Decode Strings (Leetcode Premium)](https://leetcode.com/problems/encode-and-decode-strings/)
### Tree
    - [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/)
    - [Same Tree](https://leetcode.com/problems/same-tree/)
    - [Invert/Flip Binary Tree](https://leetcode.com/problems/invert-binary-tree/)
    - [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/)
    - [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/)
    - [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)
    - [Subtree of Another Tree](https://leetcode.com/problems/subtree-of-another-tree/)
    - [Construct Binary Tree from Preorder and Inorder Traversal](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)
    -   [Kth Smallest Element in a BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/)
    - [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/)
    - [Lowest Common Ancestor of BST](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/)
    - [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/)
    - [Add and Search Word](https://leetcode.com/problems/add-and-search-word-data-structure-design/)
    - [Word Search II](https://leetcode.com/problems/word-search-ii/)
### Heap
    - [Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/)
    - [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/)
    - [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)
