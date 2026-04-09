I have a JSON file containing user data from our web application's API response at /home/user/data/users.json. The file contains an array of user objects, each with fields: id, name, email, and signup_date.

I need you to transform this data into a CSV file for our analytics team. Please create a CSV file at /home/user/output/users.csv with the following requirements:

1. The CSV should have a header row with columns in this exact order: id,name,email,signup_date
2. Each user should be on its own line
3. No spaces after commas
4. No quotes around fields unless the field contains a comma (which none of these should)
5. The rows should be in the same order as they appear in the JSON array

The output file must be saved to /home/user/output/users.csv (you may need to create the output directory if it doesn't exist).
