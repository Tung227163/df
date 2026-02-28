"""
Product DAO implementation
"""
from typing import List
from .generic_dao import GenericDAO
from ..models.product import Product
from ..utils.database import DatabaseUtil


class ProductDAO(GenericDAO[Product]):
    """Product DAO implementation"""
    
    def create(self, product: Product) -> Product:
        """Create a new product"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO products (product_code, product_name, category, price, 
                                     stock_quantity, unit, supplier, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (product.product_code, product.product_name, product.category, 
                  product.price, product.stock_quantity, product.unit, 
                  product.supplier, product.is_active))
            
            conn.commit()
            product.id = cursor.lastrowid
            return product
        except Exception as e:
            print(f"Error creating product: {e}")
            conn.rollback()
            return None
    
    def find_by_id(self, product_id: int) -> Product:
        """Find product by ID"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        
        if row:
            return self._extract_product_from_row(row)
        return None
    
    def find_by_code(self, code: str) -> Product:
        """Find product by code"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE product_code = ?", (code,))
        row = cursor.fetchone()
        
        if row:
            return self._extract_product_from_row(row)
        return None
    
    def find_all(self) -> List[Product]:
        """Find all active products"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY product_id")
        rows = cursor.fetchall()
        
        return [self._extract_product_from_row(row) for row in rows]
    
    def find_by_name(self, name: str) -> List[Product]:
        """Find products by name"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM products WHERE product_name LIKE ? AND is_active = 1
        """, (f"%{name}%",))
        rows = cursor.fetchall()
        
        return [self._extract_product_from_row(row) for row in rows]
    
    def find_by_category(self, category: str) -> List[Product]:
        """Find products by category"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM products WHERE category LIKE ? AND is_active = 1
        """, (f"%{category}%",))
        rows = cursor.fetchall()
        
        return [self._extract_product_from_row(row) for row in rows]
    
    def sort_by_price(self, ascending=True) -> List[Product]:
        """Sort products by price"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        # Validate order direction to prevent SQL injection
        order = "ASC" if ascending else "DESC"
        assert order in ("ASC", "DESC"), "Invalid order direction"
        
        cursor.execute(f"""
            SELECT * FROM products WHERE is_active = 1 ORDER BY price {order}
        """)
        rows = cursor.fetchall()
        
        return [self._extract_product_from_row(row) for row in rows]
    
    def sort_by_name(self, ascending=True) -> List[Product]:
        """Sort products by name"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        # Validate order direction to prevent SQL injection
        order = "ASC" if ascending else "DESC"
        assert order in ("ASC", "DESC"), "Invalid order direction"
        
        cursor.execute(f"""
            SELECT * FROM products WHERE is_active = 1 ORDER BY product_name {order}
        """)
        rows = cursor.fetchall()
        
        return [self._extract_product_from_row(row) for row in rows]
    
    def update(self, product: Product) -> bool:
        """Update product"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE products SET product_code = ?, product_name = ?, category = ?,
                       price = ?, stock_quantity = ?, unit = ?, supplier = ?, 
                       is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE product_id = ?
            """, (product.product_code, product.product_name, product.category,
                  product.price, product.stock_quantity, product.unit,
                  product.supplier, product.is_active, product.id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            conn.rollback()
            return False
    
    def delete(self, product_id: int) -> bool:
        """Soft delete product"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE products SET is_active = 0 WHERE product_id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting product: {e}")
            conn.rollback()
            return False
    
    def delete_all(self) -> bool:
        """Soft delete all products"""
        conn = DatabaseUtil.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE products SET is_active = 0")
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting all products: {e}")
            conn.rollback()
            return False
    
    def _extract_product_from_row(self, row) -> Product:
        """Extract Product object from database row"""
        product = Product(
            product_id=row['product_id'],
            product_code=row['product_code'],
            product_name=row['product_name'],
            category=row['category'],
            price=row['price'],
            stock_quantity=row['stock_quantity'],
            unit=row['unit'],
            supplier=row['supplier']
        )
        product.is_active = bool(row['is_active'])
        product.created_at = row['created_at']
        product.updated_at = row['updated_at']
        return product
