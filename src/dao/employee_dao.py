"""
Employee DAO implementation
"""
from typing import List
from .generic_dao import GenericDAO
from ..models.employee import Employee
from ..utils.database import DatabaseUtil


class EmployeeDAO(GenericDAO[Employee]):
    """Employee DAO implementation"""
    
    def create(self, employee: Employee) -> Employee:
        """Create a new employee"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO employees (employee_code, full_name, phone, email, 
                                      position, salary, hire_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (employee.employee_code, employee.full_name, employee.phone,
                  employee.email, employee.position, employee.salary,
                  employee.hire_date, employee.is_active))
            
            conn.commit()
            employee.id = cursor.lastrowid
            return employee
        except Exception as e:
            print(f"Error creating employee: {e}")
            conn.rollback()
            return None
    
    def find_by_id(self, employee_id: int) -> Employee:
        """Find employee by ID"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        row = cursor.fetchone()
        
        if row:
            return self._extract_employee_from_row(row)
        return None
    
    def find_by_code(self, code: str) -> Employee:
        """Find employee by code"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees WHERE employee_code = ?", (code,))
        row = cursor.fetchone()
        
        if row:
            return self._extract_employee_from_row(row)
        return None
    
    def find_all(self) -> List[Employee]:
        """Find all active employees"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees WHERE is_active = 1 ORDER BY employee_id")
        rows = cursor.fetchall()
        
        return [self._extract_employee_from_row(row) for row in rows]
    
    def find_by_name(self, name: str) -> List[Employee]:
        """Find employees by name"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM employees WHERE full_name LIKE ? AND is_active = 1
        """, (f"%{name}%",))
        rows = cursor.fetchall()
        
        return [self._extract_employee_from_row(row) for row in rows]
    
    def find_by_position(self, position: str) -> List[Employee]:
        """Find employees by position"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM employees WHERE position LIKE ? AND is_active = 1
        """, (f"%{position}%",))
        rows = cursor.fetchall()
        
        return [self._extract_employee_from_row(row) for row in rows]
    
    def sort_by_salary(self, ascending=True) -> List[Employee]:
        """Sort employees by salary"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        # Validate order direction to prevent SQL injection
        order = "ASC" if ascending else "DESC"
        assert order in ("ASC", "DESC"), "Invalid order direction"
        
        cursor.execute(f"""
            SELECT * FROM employees WHERE is_active = 1 ORDER BY salary {order}
        """)
        rows = cursor.fetchall()
        
        return [self._extract_employee_from_row(row) for row in rows]
    
    def update(self, employee: Employee) -> bool:
        """Update employee"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE employees SET employee_code = ?, full_name = ?, phone = ?,
                       email = ?, position = ?, salary = ?, hire_date = ?,
                       is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE employee_id = ?
            """, (employee.employee_code, employee.full_name, employee.phone,
                  employee.email, employee.position, employee.salary,
                  employee.hire_date, employee.is_active, employee.id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating employee: {e}")
            conn.rollback()
            return False
    
    def delete(self, employee_id: int) -> bool:
        """Soft delete employee"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE employees SET is_active = 0 WHERE employee_id = ?", (employee_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting employee: {e}")
            conn.rollback()
            return False
    
    def delete_all(self) -> bool:
        """Soft delete all employees"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE employees SET is_active = 0")
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting all employees: {e}")
            conn.rollback()
            return False
    
    def _extract_employee_from_row(self, row) -> Employee:
        """Extract Employee object from database row"""
        employee = Employee(
            employee_id=row['employee_id'],
            employee_code=row['employee_code'],
            full_name=row['full_name'],
            phone=row['phone'],
            email=row['email'],
            position=row['position'],
            salary=row['salary'],
            hire_date=row['hire_date']
        )
        employee.is_active = bool(row['is_active'])
        employee.created_at = row['created_at']
        employee.updated_at = row['updated_at']
        return employee
