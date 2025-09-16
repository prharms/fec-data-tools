I want to create the main project , which will be in the subfolder /fec_formatter.

The python script will accept the following CLI arguments:

"--input-file" (MANDATORY) will be a CSV file. This CSV file will be output from the Federal Elections Commission (FEC) database in the same format as the file data\01 - C00831107 (Sen) - 2025-2026.csv

"--contrbutor-name" export will limit the output to only rows from the input file matching this exact name. I want to be able to include multiple --contributor-name inputs if possible (which should work under "OR" Boolean logic).

"--contributor-id" I want to be able to include multiple --contributor-name inputs if possible (which should work under "OR" Boolean logic).I 

The output should be an XSLX file, containing the following columns:

- Recipient, constructed out of the committee_name column and committee ID column, in the style of KATIE PORTER FOR SENATE (C00831107)   

- Contributor, constructed out of contributor_name.  If contributor_id exists, and IS NOT EQUAL TO C00401224, append contributor_id within parentheses, in the style of WOMEN IN LEADERSHIP PAC (C00790790)

Contributor address, constructed out of contributor_street_1, contributor_street_2, contributor_city, contributor_state, contributor_zip in the style of 393 7TH AVE STE 301, SAN FRANCISCO, CA 941182378

Contributor Occupation/Employer. If fields have a value in them, construct from from the contributor_employer and contributor_occupation fields in the form of CEO/Jones construction. If the fields are blank, leave this blank.

Contribution date, from contribution_receipt_date

Contribution amount from contribution_receipt_amount

FEC ID from image_number, with pdf_url as an embedded hyperlink.



