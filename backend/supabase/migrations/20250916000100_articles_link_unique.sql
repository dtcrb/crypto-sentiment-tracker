-- Deduplicate existing articles by link (keep the most recent by published_date, then highest id)
WITH ranked AS (
    SELECT id, link,
           ROW_NUMBER() OVER (
               PARTITION BY link 
               ORDER BY published_date DESC, id DESC
           ) AS rn
    FROM articles
    WHERE link IS NOT NULL
)
DELETE FROM articles a
USING ranked r
WHERE a.id = r.id
  AND r.rn > 1;

-- Add unique constraint on link
ALTER TABLE articles
ADD CONSTRAINT articles_link_key UNIQUE (link);


