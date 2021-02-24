1. Run create_info_tables.sql to create and fill informational tables from CSVs in the informational_tables folder
2. Run create_dwh_tables.sql to create the tables in the database
3. Run generate_dwh_fill.py to create SQL output to backfill the tables
4. Run SQL output from step 3 (this is included as __generated_dwh_full_fill.sql)
5. Run queries as desired from questions folder
