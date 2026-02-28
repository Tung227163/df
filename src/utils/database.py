"""
Database utility for SQLite connection and initialization
"""
import sqlite3
import os


class DatabaseUtil:
    """
    Database connection utility using SQLite
    
    NOTE: This singleton implementation is not thread-safe. For multi-threaded
    applications, consider using threading.Lock() or a thread-safe singleton pattern.
    This is acceptable for single-threaded CLI applications.
    """
    
    DB_PATH = "supermarket.db"
    _connection = None
    
    @classmethod
    def get_connection(cls):
        """Get database connection (singleton pattern)"""
        if cls._connection is None:
            cls._connection = sqlite3.connect(cls.DB_PATH)
            cls._connection.row_factory = sqlite3.Row
        return cls._connection
    
    @classmethod
    def initialize_database(cls):
        """Initialize database with schema"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_code VARCHAR(50) UNIQUE NOT NULL,
                    product_name VARCHAR(200) NOT NULL,
                    category VARCHAR(100),
                    price DECIMAL(10, 2) NOT NULL,
                    stock_quantity INTEGER DEFAULT 0,
                    unit VARCHAR(20),
                    supplier VARCHAR(200),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_code VARCHAR(50) UNIQUE NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    position VARCHAR(50),
                    salary DECIMAL(10, 2),
                    hire_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default admin user
            # SECURITY NOTE: This is a demo/development setup with plain text password.
            # In production, passwords should be hashed using bcrypt or similar,
            # and users should be prompted to change default credentials on first login.
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password, full_name, role)
                VALUES ('admin', 'admin123', 'Administrator', 'ADMIN')
            """)
            
            # Insert sample products
            sample_products = [
                ('P001', 'Gạo Thơm', 'Thực phẩm', 25000, 100, 'kg', 'Nhà cung cấp A'),
                ('P002', 'Dầu ăn', 'Thực phẩm', 45000, 50, 'lít', 'Nhà cung cấp B'),
                ('P003', 'Sữa tươi', 'Sữa', 35000, 80, 'hộp', 'Nhà cung cấp C'),
                ('P004', 'Bánh mì', 'Bánh', 15000, 120, 'ổ', 'Nhà cung cấp D')
            ]
            
            for product in sample_products:
                cursor.execute("""
                    INSERT OR IGNORE INTO products 
                    (product_code, product_name, category, price, stock_quantity, unit, supplier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, product)
            
            # Insert sample employees
            sample_employees = [
                ('E001', 'Nguyễn Văn A', '0901234567', 'nva@email.com', 'Quản lý', 15000000, '2023-01-15'),
                ('E002', 'Trần Thị B', '0912345678', 'ttb@email.com', 'Thu ngân', 8000000, '2023-03-20'),
                ('E003', 'Lê Văn C', '0923456789', 'lvc@email.com', 'Nhân viên kho', 7000000, '2023-05-10')
            ]
            
            for employee in sample_employees:
                cursor.execute("""
                    INSERT OR IGNORE INTO employees
                    (employee_code, full_name, phone, email, position, salary, hire_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, employee)
            
            conn.commit()
            print("✓ Database initialized successfully!")
            
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            conn.rollback()
    
    @classmethod
    def close_connection(cls):
        """Close database connection"""
        if cls._connection:
            cls._connection.close()
            cls._connection = None
