CREATE TABLE IF NOT EXISTS example_tags(
    example_Id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    Primary KEY (example_Id, tag_id),
    FOREIGN KEY (example_Id) REFERENCES examples(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- ALTER TABLE tags ADD COLUMN description TEXT;
