-- STRG + SHIFT + Q
-- SELECT * FROM hat
-- DELETE FROM hat

SELECT * FROM Standards 
INNER JOIN hat ON Standards.SID = hat.SID 
INNER JOIN Keywords ON hat.KID = Keywords.KID
WHERE Keywords.title IN ('Dry', 'Shape')
ORDER BY Standards.title