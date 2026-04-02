-- 1. Upsert Procedure (Update if exists, insert if not)
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;

-- 2. Bulk Insert Procedure with Validation (using INOUT parameter to return errors)
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_names VARCHAR[],
    p_phones VARCHAR[],
    INOUT invalid_data VARCHAR[] DEFAULT '{}'
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    invalid_data := '{}';
    FOR i IN 1 .. array_length(p_names, 1) LOOP
        -- Basic validation: phone is not empty and contains only digits and a plus sign
        IF p_phones[i] ~ '^\+?[0-9]+$' THEN
            -- Call our upsert procedure for correct insertion
            CALL upsert_contact(p_names[i], p_phones[i]);
        ELSE
            -- If the phone number is invalid, add it to the invalid_data array
            invalid_data := array_append(invalid_data, p_names[i] || ' (' || p_phones[i] || ')');
        END IF;
    END LOOP;
END;
$$;

-- 3. Procedure to delete by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_search_val VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts 
    WHERE name = p_search_val OR phone = p_search_val;
END;
$$;
