CREATE TABLE IF NOT EXISTS "articles" (
	"id"	                INTEGER NOT NULL,
	"pushed"                BOOLEAN NOT NULL DEFAULT 0,
	"icon"                  TEXT,
    "title"                 TEXT UNIQUE,
    "summary"               TEXT,
    "publisher"             TEXT,
    "authors"               TEXT,
    "category"              TEXT,
    "sentiment"             TEXT,
    "sentiment_score"       INTEGER,
    "article_type"          TEXT,
    "published"             TEXT,
    "modified"              TEXT,
    "tags"                  TEXT,
    "body"                  TEXT,
    "url"                   TEXT UNIQUE,
    "images"                TEXT,

	PRIMARY KEY("id" AUTOINCREMENT) ON CONFLICT IGNORE
)
