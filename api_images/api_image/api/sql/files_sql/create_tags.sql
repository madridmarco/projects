CREATE TABLE IF NOT EXISTS tags (
    tag VARCHAR(32),
    picture_id VARCHAR(36),
    confidence FLOAT,
    date TIMESTAMP,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);