import sqlite3

def create_employee_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            position TEXT,
            contact TEXT,
            job_history TEXT,
            skills TEXT
        )
    ''')

def add_employee(cursor, name, department, position, contact, job_history, skills):
    cursor.execute('''
        INSERT INTO employees (name, department, position, contact, job_history, skills)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, department, position, contact, job_history, skills))

def search_employees(cursor, criteria):
    cursor.execute('''
        SELECT * FROM employees
        WHERE name LIKE ? OR department LIKE ? OR position LIKE ? OR contact LIKE ? OR job_history LIKE ? OR skills LIKE ?
    ''', ('%{}%'.format(criteria), '%{}%'.format(criteria), '%{}%'.format(criteria), '%{}%'.format(criteria), '%{}%'.format(criteria), '%{}%'.format(criteria)))
    return cursor.fetchall()

def update_employee(cursor, employee_id, name, department, position, contact, job_history, skills):
    cursor.execute('''
        UPDATE employees
        SET name = ?, department = ?, position = ?, contact = ?, job_history = ?, skills = ?
        WHERE id = ?
    ''', (name, department, position, contact, job_history, skills, employee_id))
def delete_employee(cursor, employee_id):
    cursor.execute('''
        DELETE FROM employees
        WHERE id = ?
    ''', (employee_id,))

# Main function
def main():
    conn = sqlite3.connect('employee_directory.db')
    cursor = conn.cursor()

    # Create the employee table if it does not exist
    create_employee_table(cursor)

    while True:
        print("\nEmployee Directory")
        print("1. Add New Employee")
        print("2. Search Employees")
        print("3. Update Employee Information")
        print("4. Delete Employee")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            try:
                name = input("Enter employee name: ")
                department = input("Enter employee department: ")
                position = input("Enter employee position: ")
                contact = input("Enter employee contact details: ")
                job_history = input("Enter employee job history: ")
                skills = input("Enter employee skills: ")
                
                # Added input validation
                if not (name and department and position):
                    raise ValueError("Name, department, and position cannot be empty.")
                
                add_employee(cursor, name, department, position, contact, job_history, skills)
                conn.commit()
                print("Employee added successfully!")
            except Exception as e:
                print("Error:", e)
        
        elif choice == '2':
            criteria = input("Enter search criteria: ")
            results = search_employees(cursor, criteria)
            if results:
                print("\nSearch Results:")
                for employee in results:
                    print(employee)
            else:
                print("No matching employees found.")

        elif choice == '3':
            try:
                employee_id = int(input("Enter employee ID to update: "))
                name = input("Enter updated employee name: ")
                department = input("Enter updated employee department: ")
                position = input("Enter updated employee position: ")
                contact = input("Enter updated employee contact details: ")
                job_history = input("Enter updated employee job history: ")
                skills = input("Enter updated employee skills: ")
                
                # Added input validation
                if not (name and department and position):
                    raise ValueError("Name, department, and position cannot be empty.")
                
                update_employee(cursor, employee_id, name, department, position, contact, job_history, skills)
                conn.commit()
                print("Employee information updated successfully!")
            except Exception as e:
                print("Error:", e)

        elif choice == '4':
            try:
                employee_id = int(input("Enter employee ID to delete: "))
                delete_employee(cursor, employee_id)
                conn.commit()
                print("Employee deleted successfully!")
            except Exception as e:
                print("Error:", e)

        elif choice == '5':
            break

        else:
            print("Invalid choice. Please enter a valid option.")

    conn.close()

if __name__ == "__main__":
    main()
