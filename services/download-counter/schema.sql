CREATE TABLE IF NOT EXISTS daily_downloads (
  day TEXT NOT NULL,
  asset TEXT NOT NULL CHECK (asset IN ('starter', 'overleaf', 'class', 'cheatsheet')),
  total INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, asset)
);
