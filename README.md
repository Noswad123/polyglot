# Polyglot

Polyglot helps developers learn programming concepts by comparing them across different languages and paradigms. Think of it as learning to communicate—not just memorize rules. As your communication skills evolve, so does your mastery.

Learn a programming language the way you’d learn to speak:
Start simple, practice often, and gradually embrace nuance and style.

Read more in the [Philosphy](#Philosophy) section.

## Contents
Each programming language will contain folders with the following name. Navigating the following links will expalin more about their contents.
- [Katas](./README/katas/index.md): Help You gain proficiency over a language
- [Scripts](./README/scripts/index.md): This incorporate workflows that are a little more involved.
- [Polyglot Frontend](./README/polyglot-frontend.md): An implementation of the Polylot repo
- [Polyglot Backend](./README/polyglot-backend.md): An implementation of the Polylot repo
- [Playground](./README/playground.md): A place to tinker with your programming language

## Philosophy

Learning a programming language is like learning to communicate in a new tongue.
You don’t start with poetry or debate—you start with everyday conversation. Only as you grow comfortable do you explore complex expression, style, and structure. Let’s dive further into this metaphor.

Basic Fluency: Conversational Skills
- In Language: Asking questions, stating facts, expressing needs, reading instructions.
- In Programming: Variables, loops, functions, conditions; reading/writing files; handling basic errors.

Intermediate: Style, Idioms, and Nuance
- In Language: Idioms, slang, and finding your unique voice.
- In Programming: Writing idiomatic code (“pythonic” in Python, etc.), discovering built-in functions, structuring solutions more elegantly.

Advanced: Rhetoric, Storytelling, and Philosophy
- In Language: Rhetoric, persuasive writing, storytelling, and literary analysis.
- In Programming: Software design, architecture, design patterns, coding paradigms, and principles like SOLID, DRY, and first principles thinking.

### Programming concepts from a linguistic perspective
#### Coding Paradigms (Modes of discourse: narration, argumentation, exposition)
Foundational styles and philosophies for thinking about code; influences every other advanced topic.
- Why? Understanding paradigms (procedural, OOP, functional, etc.) shapes your approach to all other patterns, architectures, and even how you refactor.
- In Language: Discourse modes define how you convey ideas—do you narrate a story, argue a position, or explain a concept?
- In Programming: Coding paradigms (procedural, object-oriented, functional, declarative, event-driven) are styles or philosophies that shape how you design solutions and reason about code.
- Purpose: Choosing the right paradigm can make solutions clearer and more natural, just like using a story, a debate, or an instruction manual fits different types of communication.

#### Architectural Patterns (Structure of essays, news articles, debates)
High-level blueprints for structuring applications or systems.
- Why? Once you know how to think (paradigms), you want to know how to organize large projects.
- In Language: Just as essays have introductions, bodies, and conclusions—or a news article uses the inverted pyramid structure—architectural patterns give code its “big-picture” organization.
- In Programming: Architectural patterns (like MVC, layered architecture, microservices) provide a blueprint for organizing large codebases. They determine how components interact, how data flows, and how responsibilities are separated.
- Purpose: Helps teams collaborate, maintain, and scale complex systems—just as a well-structured essay guides readers smoothly from idea to idea.

#### Design Patterns (Literary genres (poetry, essay), storytelling tropes (hero’s journey))
Reusable solutions to common design problems within your chosen paradigm and architecture.
- Why? Design patterns live “inside” architectures and paradigms, providing vocabulary for solving specific, recurring challenges.
- In Language: Literary genres or plot archetypes are tried-and-true ways to structure stories for different effects.
- In Programming: Design patterns (like Singleton, Observer, Factory, Strategy) are reusable solutions to common design problems.
- Example: The Singleton pattern manages global shared state (the “king” of your story); the Observer pattern handles notifications (the “town crier”).
- Purpose: Promotes proven, reusable approaches so others can instantly “get” your code structure—like knowing the beats of a detective novel.

#### Frameworks & Libraries(Idioms, proverbs, or quotations—using existing expressions for effect)
Toolsets and collections of solutions built on top of patterns and architectures.
- Why? Once you understand “how things are built,” you can better appreciate (and evaluate) the tools others have built for you.
- In Language: Instead of reinventing the wheel, writers use familiar idioms or quotations to convey meaning efficiently.
- In Programming: Frameworks (like Django, React, Rails) and libraries (like NumPy, Lodash) offer ready-made solutions for common problems.
- Purpose: Lets you build powerful things quickly, focusing on your unique logic instead of reinventing basics—just as idioms let you say more with less.

#### Clean Code & Refactoring (Editing for clarity, conciseness, and elegance)
Principles and practices for clarity, maintainability, and elegance in code.
- Why? No matter what you build, you’ll always be revisiting and improving code. Clean code bridges the gap from “it works” to “it’s clear and reliable.”
- In Language: Good writing is clear, direct, and elegant. Editing removes redundancy, ambiguity, and awkward phrasing.
- In Programming: Clean code means readable, simple, and expressive code. Refactoring is the process of improving the structure without changing its external behavior.
- Purpose: Makes code easier for others (and your future self) to read and modify, just as polished writing communicates ideas more effectively.

#### First Principles (Linguistics, grammar theory, logic, etymology)
Questioning assumptions and building from the ground up.
- Why? Once you’re comfortable with convention, you’re ready to break the rules and innovate—thinking beyond frameworks and patterns.
Strip away assumptions and ask: What am I really trying to do?
- In language: “How can I say this if I don’t know the right word?”
- In programming: "Do I need a class, or just a function? Is this pattern necessary, or am I following tradition?"
- Example: "Do I really need a database for this, or will a simple file work?” “Is this the most direct way to solve the problem, or am I layering on tradition?"
- Purpose: Encourages innovation, simplification, and deeper understanding, much like a linguist invents new words or grammar rules for new concepts.
 
#### Testing & Test-Driven Development (Peer review, editing, feedback)
Verifying code correctness, preventing regressions, and enabling safe change.
- Why? At this point, you’re building things worth testing and want to ensure quality over time.
- In Language: Writers share drafts for feedback and revise based on peer review.
- In Programming: Automated tests and TDD ensure code behaves as expected, prevent regressions, and give developers confidence to make changes.

#### Documentation (Writing instructions, essays, or reference materials)
Making your work understandable to others (and your future self).
- Why? Good documentation becomes essential as code grows and more people interact with it.
- In Language: Good documentation is like clear instructions or reference books—helping others understand and use your work.
- In Programming: Well-documented code is easier to maintain, share, and build upon.

#### Version Control (Revision history, drafts, and collaborative editing)
Tracking history, collaborating, and safely experimenting with code.
- Why? This skill is critical in any collaborative or evolving project—especially as you refactor, test, and document.
- In Language: Writers keep track of drafts and edits; editors may compare versions to track changes.
- In Programming: Tools like Git provide a detailed history of changes, facilitate collaboration, and allow you to revisit previous versions.

#### Code Reviews & Collaboration (Writing workshops, group projects)
Learning from others and maintaining code quality as a team.
- Why? After building a solid foundation, feedback and collaboration accelerate growth and prevent errors.
- In Language: Collaborative writing sharpens your skills and broadens your perspective.
- In Programming: Code reviews, pair programming, and open source contributions foster growth and catch issues early.

#### Performance Optimization (Editing for brevity, avoiding filler)
Ensuring code runs efficiently and scales well.
- Why? Once your code is correct, maintainable, and used by others, performance can become a priority.
- In Language: Good writing avoids unnecessary words and delivers impact efficiently.
- In Programming: Optimizing code makes programs faster, use fewer resources, and scale better.

#### Security & Privacy (Safe publishing, protecting sensitive information)
Protecting users, data, and systems from threats.
- Why? Security is always important but often requires an understanding of all the above to address effectively.
- In Language: Writers protect personal stories, respect privacy, and avoid libel.
- In Programming: Developers must secure sensitive data, prevent vulnerabilities, and respect user privacy.

## Resources
- Rosetta Code - programming chrestomathy

