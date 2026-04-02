-- 1. Pattern search function (by name or phone)
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern VARCHAR)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT c.name, c.phone FROM contacts c
    WHERE c.name ILIKE '%' || p_pattern || '%'
       OR c.phone ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- 2. Function for pagination (limit and offset)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT c.name, c.phone FROM contacts c
    ORDER BY c.name
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
