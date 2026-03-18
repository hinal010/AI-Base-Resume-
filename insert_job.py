import sqlite3

conn = sqlite3.connect("users.db")
cur = conn.cursor()

# Insert experience types
cur.execute("INSERT INTO experience_type_master (type_name) VALUES ('Internship')")
cur.execute("INSERT INTO experience_type_master (type_name) VALUES ('Full Time Job')")
cur.execute("INSERT INTO experience_type_master (type_name) VALUES ('Part Time')")
cur.execute("INSERT INTO experience_type_master (type_name) VALUES ('Freelance')")

# Insert job roles
cur.execute("""
INSERT INTO job_title_master (job_title) VALUES
('Software Developer'),
('Web Developer'),
('Frontend Developer'),
('Backend Developer'),
('Full Stack Developer'),
('Python Developer'),
('Application Support Engineer'),
('Software Engineer'),
('System Engineer'),
('DevOps Engineer'),
('QA Engineer'),
('AI Engineer'),
('Machine Learning Engineer'),
('Cloud Engineer'),
('Tech Lead'),
('Software Architect'),
('Data Analyst'),
('Data Scientist'),
('Research Assistant'),
('Research Scientist'),
('Lab Technician'),
('Quality Analyst'),
('Statistician'),
('Accountant'),
('Finance Executive'),
('Bank Clerk'),
('Tax Consultant'),
('Auditor'),
('Finance Manager'),
('Senior Accountant'),
('Tax Advisor'),
('Marketing Executive'),
('Sales Executive'),
('HR Executive'),
('Business Development Executive'),
('Operations Executive'),
('Project Manager'),
('Business Analyst'),
('HR Manager'),
('Marketing Manager'),
('Operations Manager'),
('Product Manager'),
('Content Writer'),
('Teacher'),
('Journalist'),
('Social Worker'),
('Customer Support Executive'),
('Professor'),
('Content Strategist'),
('Editor'),
('Policy Analyst'),
('Technician'),
('Junior Engineer'),
('Site Supervisor'),
('Maintenance Engineer'),
('Intern'),
('Freelancer'),
('Consultant'),
('Project Coordinator'),
('Office Assistant')
""")

conn.commit()
conn.close()

print("Data inserted successfully!")