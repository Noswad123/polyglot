CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS examples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language_id INTEGER NOT NULL,
        concept_id INTEGER NOT NULL,
        code_snippet TEXT NOT NULL,
        explanation TEXT, language_trackable_id INTEGER, concept_trackable_id INTEGER,
        FOREIGN KEY (language_id) REFERENCES languages (id),
        FOREIGN KEY (concept_id) REFERENCES concepts (id)
    );
CREATE TABLE IF NOT EXISTS "languages" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "name" varchar NOT NULL, "version" varchar, "documentation_url" varchar, "description" varchar);
CREATE TABLE IF NOT EXISTS "concepts" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "name" varchar NOT NULL, "description" varchar);

CREATE TABLE trackables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('language', 'concept', 'kata', 'project')),
    description TEXT
);
CREATE TABLE trackable_relationships (
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation TEXT NOT NULL CHECK (relation IN ('uses', 'includes', 'depends_on', 'implements')),
    PRIMARY KEY (source_id, target_id, relation),
    FOREIGN KEY (source_id) REFERENCES trackables(id),
    FOREIGN KEY (target_id) REFERENCES trackables(id)
);
CREATE TABLE language_info (
    trackable_id INTEGER PRIMARY KEY,
    version TEXT,
    documentation_url TEXT,
    FOREIGN KEY (trackable_id) REFERENCES trackables(id)
);
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
);
CREATE TABLE trackable_tags (
    trackable_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (trackable_id, tag_id),
    FOREIGN KEY (trackable_id) REFERENCES trackables(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
CREATE TABLE trackable_progress (
    trackable_id INTEGER PRIMARY KEY,
    status TEXT CHECK (status IN ('not started', 'in progress', 'mastered', 'abandoned')) DEFAULT 'not started',
    notes TEXT,
    FOREIGN KEY (trackable_id) REFERENCES trackables(id)
);
CREATE TABLE IF NOT EXISTS example_tags(
    example_Id INTEGER PRIMARY KEY,
    tag_id INTEGER NOT NULL,
    Primary KEY (example_Id, tag_id),
    FOREIGN KEY (example_Id) REFERENCES examples(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
