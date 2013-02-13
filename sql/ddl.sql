-- Shamelessly adapted from queue_classic

DROP FUNCTION IF EXISTS pop_lock(name varchar);
DROP FUNCTION IF EXISTS pop_lock(name varchar, boundary integer);

CREATE OR REPLACE FUNCTION pop_lock(name varchar, boundary integer)
RETURNS SETOF trunk_queue AS $$
DECLARE
  unlocked bigint;
  relative_top integer;
  job_count integer;
BEGIN
  -- The purpose is to release contention for the first spot in the table.
  -- The select count(*) is going to slow down dequeue performance but allow
  -- for more workers. Would love to see some optimization here...

  EXECUTE 'SELECT count(*) FROM '
    || '(SELECT * FROM trunk_queue WHERE name = '
    || quote_literal(name)
    || ' AND locked_at IS NULL'
    || ' LIMIT '
    || quote_literal(boundary)
    || ') limited'
  INTO job_count;

  SELECT TRUNC(random() * (boundary - 1))
  INTO relative_top;

  IF job_count < boundary THEN
    relative_top = 0;
  END IF;

  LOOP
    BEGIN
      EXECUTE 'SELECT id FROM trunk_queue '
        || ' WHERE locked_at IS NULL'
        || ' AND name = '
        || quote_literal(name)
        || ' ORDER BY id ASC'
        || ' LIMIT 1'
        || ' OFFSET ' || quote_literal(relative_top)
        || ' FOR UPDATE NOWAIT'
      INTO unlocked;
      EXIT;
    EXCEPTION
      WHEN lock_not_available THEN
        -- do nothing. loop again and hope we get a lock
    END;
  END LOOP;

  RETURN QUERY EXECUTE 'UPDATE trunk_queue '
    || ' SET locked_at = (CURRENT_TIMESTAMP)'
    || ' WHERE id = $1'
    || ' AND locked_at is NULL'
    || ' RETURNING *'
  USING unlocked;

  RETURN;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pop_lock(name varchar)
RETURNS SETOF trunk_queue AS $$
BEGIN
RETURN QUERY EXECUTE 'SELECT * FROM pop_lock($1,10)' USING name;
END;
$$ LANGUAGE plpgsql;
