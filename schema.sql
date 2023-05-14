CREATE TABLE "user" (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  profile_pic TEXT NOT NULL
);

CREATE TABLE "grammar_check" (
	"grammar_check_id"	INTEGER,
	"input"	TEXT,
	"output"	TEXT,
	"user_id"	TEXT NOT NULL,
	PRIMARY KEY("grammar_check_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);

CREATE TABLE "plagiarism_checker" (
	"plagiarism_checker_id"	INTEGER,
	"input"	TEXT,
	"output"	TEXT,
	"user_id"	TEXT NOT NULL,
	PRIMARY KEY("plagiarism_checker_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);

CREATE TABLE "text_completion" (
	"text_completion_id"	INTEGER,
	"input"	TEXT,
	"output"	TEXT,
	"user_id"	TEXT NOT NULL,
	PRIMARY KEY("text_completion_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);

CREATE TABLE "paraphrasing" (
	"paraphrasing_id"	INTEGER,
	"input"	TEXT,
	"output"	TEXT,
	"user_id"	TEXT NOT NULL,
	PRIMARY KEY("paraphrasing_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);

CREATE TABLE "grammar" (
	"id"	INTEGER,
	"input"	TEXT,
	"output"	TEXT,
	"user_id"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);