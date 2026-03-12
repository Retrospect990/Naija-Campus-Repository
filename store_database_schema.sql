-- =============================================================================
-- Campus Pinduoduo: Online Store Database Schema Extension
-- =============================================================================
-- Tables for product catalog, shopping carts, and order management
-- These tables integrate with the existing escrow system
-- =============================================================================

-- ============================================================================
-- 1. PRODUCT & INVENTORY MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS store_product_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE store_product_categories IS 'Product categories (food, beverages, fashion, etc)';

-- Core products table
CREATE TABLE IF NOT EXISTS store_products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES store_product_categories(category_id),
    product_name VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(12, 2) NOT NULL CHECK (price > 0),
    unit VARCHAR(20), -- e.g., "bag", "pack", "piece", "liter"
    quantity_available INTEGER NOT NULL DEFAULT 0 CHECK (quantity_available >= 0),
    supplier_name VARCHAR(100),
    supplier_phone VARCHAR(20),
    average_rating DECIMAL(3, 2),
    rating_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint: same product can't be imported by same supplier at same price
    UNIQUE(category_id, product_name, brand, supplier_name)
);

CREATE INDEX idx_products_category ON store_products(category_id);
CREATE INDEX idx_products_brand ON store_products(brand);
CREATE INDEX idx_products_search ON store_products USING GIN (
    to_tsvector('english', product_name || ' ' || brand || ' ' || description)
);
CREATE INDEX idx_products_active ON store_products(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE store_products IS 'Product catalog with multiple brands per category';
COMMENT ON COLUMN store_products.quantity_available IS 'Stock level for this product variant';
COMMENT ON COLUMN store_products.supplier_name IS 'Supplier/vendor providing this product';

-- Product variants (e.g., sizes, colors) - Optional
CREATE TABLE IF NOT EXISTS store_product_variants (
    variant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES store_products(product_id) ON DELETE CASCADE,
    variant_name VARCHAR(100), -- e.g., "Large", "Red", "500ml"
    variant_price_adjustment DECIMAL(8, 2) DEFAULT 0, -- Additional cost over base price
    quantity_available INTEGER NOT NULL DEFAULT 0,
    sku VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_variants_product ON store_product_variants(product_id);

COMMENT ON TABLE store_product_variants IS 'Size, color, or other variants of products';

-- Product reviews and ratings
CREATE TABLE IF NOT EXISTS store_product_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES store_products(product_id) ON DELETE CASCADE,
    moderator_id UUID NOT NULL REFERENCES groups_members(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    helpful_count INTEGER DEFAULT 0
);

CREATE INDEX idx_reviews_product ON store_product_reviews(product_id);
CREATE INDEX idx_reviews_moderator ON store_product_reviews(moderator_id);

COMMENT ON TABLE store_product_reviews IS 'Product reviews and ratings by moderators';

-- ============================================================================
-- 2. SHOPPING CART MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS shopping_carts (
    cart_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES pools(id) ON DELETE CASCADE,
    moderator_id UUID NOT NULL REFERENCES groups_members(id) ON DELETE CASCADE,
    pool_budget DECIMAL(12, 2) NOT NULL, -- Available funds in pool
    status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, ABANDONED, CONVERTED_TO_ORDER
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    abandoned_at TIMESTAMP
);

CREATE INDEX idx_carts_pool ON shopping_carts(pool_id);
CREATE INDEX idx_carts_moderator ON shopping_carts(moderator_id);
CREATE INDEX idx_carts_active ON shopping_carts(status) WHERE status = 'ACTIVE';

COMMENT ON TABLE shopping_carts IS 'Shopping baskets with budget constraints per pool';
COMMENT ON COLUMN shopping_carts.pool_budget IS 'Total funds available in the pool';

-- Items in shopping cart
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES shopping_carts(cart_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES store_products(product_id),
    variant_id UUID REFERENCES store_product_variants(variant_id),
    quantity_requested INTEGER NOT NULL CHECK (quantity_requested > 0),
    unit_price DECIMAL(12, 2) NOT NULL, -- Price at time of addition (immutable)
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(cart_id, product_id)
);

CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);

COMMENT ON TABLE cart_items IS 'Individual items in shopping cart';
COMMENT ON COLUMN cart_items.unit_price IS 'Price frozen at time of cart addition';

-- ============================================================================
-- 3. ORDER MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS store_orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES pools(id) ON DELETE RESTRICT,
    moderator_id UUID NOT NULL REFERENCES groups_members(id),
    order_number VARCHAR(20) UNIQUE, -- E.g., ORD-2024-00001
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', 
    -- PENDING -> CONFIRMED -> PAID -> PROCESSING -> SHIPPED -> DELIVERED
    -- Can also transition to CANCELLED
    total_amount DECIMAL(12, 2) NOT NULL,
    notes TEXT,
    delivery_address TEXT,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    paid_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_pool ON store_orders(pool_id);
CREATE INDEX idx_orders_moderator ON store_orders(moderator_id);
CREATE INDEX idx_orders_status ON store_orders(status);
CREATE INDEX idx_orders_date ON store_orders(created_at);

COMMENT ON TABLE store_orders IS 'Orders placed from shopping carts';
COMMENT ON COLUMN store_orders.total_amount IS 'Order total deducted from pool balance';
COMMENT ON COLUMN store_orders.status IS 'Order lifecycle: PENDING -> CONFIRMED -> PAID -> PROCESSING -> SHIPPED -> DELIVERED';

-- Order line items (items in each order)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES store_orders(order_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES store_products(product_id),
    variant_id UUID REFERENCES store_product_variants(variant_id),
    quantity_ordered INTEGER NOT NULL CHECK (quantity_ordered > 0),
    unit_price DECIMAL(12, 2) NOT NULL, -- Price at time of order
    line_total DECIMAL(12, 2) NOT NULL, -- unit_price * quantity_ordered
    notes VARCHAR(255)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

COMMENT ON TABLE order_items IS 'Itemized list for each order';

-- Order status history / audit trail
CREATE TABLE IF NOT EXISTS order_status_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES store_orders(order_id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by_user_id UUID REFERENCES users(id),
    change_reason VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status_history_order ON order_status_history(order_id);

COMMENT ON TABLE order_status_history IS 'Audit trail of order status changes';

-- ============================================================================
-- 4. INVENTORY TRACKING & WAREHOUSE
-- ============================================================================

CREATE TABLE IF NOT EXISTS warehouse_inventory (
    inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES store_products(product_id) ON DELETE CASCADE,
    warehouse_location VARCHAR(100), -- e.g., "Lagos HQ", "Abuja Branch"
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    quantity_reserved INTEGER NOT NULL DEFAULT 0, -- For pending/confirmed orders
    reorder_level INTEGER DEFAULT 10,
    reorder_quantity INTEGER DEFAULT 50,
    last_count_date DATE,
    last_restocked_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_id, warehouse_location)
);

CREATE INDEX idx_inventory_product ON warehouse_inventory(product_id);
CREATE INDEX idx_inventory_low_stock ON warehouse_inventory(quantity_on_hand) 
WHERE quantity_on_hand < reorder_level;

COMMENT ON TABLE warehouse_inventory IS 'Physical inventory tracking by warehouse location';
COMMENT ON COLUMN warehouse_inventory.quantity_reserved IS 'Stock allocated to confirmed orders not yet shipped';

-- Stock movements (audit trail)
CREATE TABLE IF NOT EXISTS inventory_movements (
    movement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES store_products(product_id),
    warehouse_location VARCHAR(100),
    movement_type VARCHAR(20), -- 'RESTOCK', 'ORDER', 'RETURN', 'ADJUSTMENT', 'DAMAGE'
    quantity_change INTEGER NOT NULL, -- Positive or negative
    reference_id UUID, -- order_id, movement_id, etc
    notes TEXT,
    created_by_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movements_product ON inventory_movements(product_id);
CREATE INDEX idx_movements_type ON inventory_movements(movement_type);
CREATE INDEX idx_movements_date ON inventory_movements(created_at);

COMMENT ON TABLE inventory_movements IS 'Audit trail of all inventory changes';

-- ============================================================================
-- 5. SALES & ANALYTICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS daily_sales_summary (
    summary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_date DATE NOT NULL UNIQUE,
    total_orders INTEGER DEFAULT 0,
    total_sales_amount DECIMAL(12, 2) DEFAULT 0,
    total_items_sold INTEGER DEFAULT 0,
    unique_moderators INTEGER DEFAULT 0,
    avg_order_value DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_summary_date ON daily_sales_summary(sale_date);

COMMENT ON TABLE daily_sales_summary IS 'Daily aggregated sales metrics';

-- Product-level sales
CREATE TABLE IF NOT EXISTS product_sales (
    product_sales_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES store_products(product_id),
    sale_date DATE NOT NULL,
    quantity_sold INTEGER NOT NULL,
    total_sales DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_id, sale_date)
);

CREATE INDEX idx_product_sales_date ON product_sales(sale_date);
CREATE INDEX idx_product_sales_product ON product_sales(product_id);

COMMENT ON TABLE product_sales IS 'Daily sales metrics per product';

-- ============================================================================
-- 6. INTEGRATION WITH ESCROW SYSTEM
-- ============================================================================

-- Link orders to pool budget deductions
CREATE TABLE IF NOT EXISTS pool_budget_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES pools(id) ON DELETE CASCADE,
    order_id UUID REFERENCES store_orders(order_id) ON DELETE SET NULL,
    transaction_type VARCHAR(20), -- 'ORDER', 'REFUND', 'ADJUSTMENT'
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_trans_pool ON pool_budget_transactions(pool_id);
CREATE INDEX idx_budget_trans_order ON pool_budget_transactions(order_id);

COMMENT ON TABLE pool_budget_transactions IS 'Track how pool budget is spent';

-- ============================================================================
-- 7. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on store tables
ALTER TABLE store_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE store_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_reviews ENABLE ROW LEVEL SECURITY;

-- ===== Product Visibility =====
-- Everyone can view active products
CREATE POLICY products_readable ON store_products
    FOR SELECT USING (is_active = TRUE);

-- Only admins can insert/update/delete products
CREATE POLICY products_insertable ON store_products
    FOR INSERT WITH CHECK (
        (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
    );

CREATE POLICY products_updatable ON store_products
    FOR UPDATE USING (
        (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
    );

CREATE POLICY products_deletable ON store_products
    FOR DELETE USING (
        (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
    );

-- ===== Shopping Cart =====
-- Moderators can only see/edit their own carts
CREATE POLICY cart_own ON shopping_carts
    FOR ALL USING (
        moderator_id = (SELECT member_id FROM groups_members WHERE id = auth.uid() LIMIT 1)
    );

-- ===== Orders =====
-- Moderators can only see their own orders
CREATE POLICY order_own ON store_orders
    FOR SELECT USING (
        moderator_id = (SELECT member_id FROM groups_members WHERE id = auth.uid() LIMIT 1)
    );

-- Only correct moderator can place orders
CREATE POLICY order_insert ON store_orders
    FOR INSERT WITH CHECK (
        moderator_id = (SELECT member_id FROM groups_members WHERE id = auth.uid() LIMIT 1)
    );

-- Admins can update order status
CREATE POLICY order_update_admin ON store_orders
    FOR UPDATE USING (
        (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
    );

-- ===== Reviews =====
-- Moderators can see all reviews
CREATE POLICY reviews_readable ON store_product_reviews
    FOR SELECT USING (TRUE);

-- Moderators can write their own reviews
CREATE POLICY reviews_insertable ON store_product_reviews
    FOR INSERT WITH CHECK (
        moderator_id = (SELECT id FROM groups_members WHERE user_id = auth.uid() LIMIT 1)
    );

-- ============================================================================
-- 8. SAMPLE DATA INSERTION
-- ============================================================================

-- Insert product categories
INSERT INTO store_product_categories (category_name, description, display_order) VALUES
    ('Food', 'Staples and bulk food items', 1),
    ('Beverages', 'Drinks and beverages', 2),
    ('Fashion', 'Clothing and apparel', 3),
    ('Electronics', 'Tech and gadgets', 4),
    ('Home & Garden', 'Home essentials', 5),
    ('Books & Supplies', 'Educational materials', 6),
    ('Cosmetics', 'Beauty and personal care', 7),
    ('Sports', 'Sports and fitness', 8)
ON CONFLICT (category_name) DO NOTHING;

-- Sample products (aligned with store_system.py demo data)
INSERT INTO store_products (category_id, product_name, brand, price, unit, quantity_available, supplier_name, average_rating)
SELECT 
    (SELECT category_id FROM store_product_categories WHERE category_name = 'Food'),
    'Rice', 'Uncle Ben''s', 25000.00, 'bag', 100, 'Northern Supplies', 4.5
WHERE NOT EXISTS (SELECT 1 FROM store_products WHERE brand = 'Uncle Ben''s' AND product_name = 'Rice')
UNION ALL
SELECT 
    (SELECT category_id FROM store_product_categories WHERE category_name = 'Food'),
    'Rice', 'Golden Harvest', 22000.00, 'bag', 120, 'Eastern Foods', 4.3
WHERE NOT EXISTS (SELECT 1 FROM store_products WHERE brand = 'Golden Harvest' AND product_name = 'Rice')
UNION ALL
SELECT 
    (SELECT category_id FROM store_product_categories WHERE category_name = 'Food'),
    'Beans', 'Local Premium', 12000.00, 'bag', 80, 'Agro Mart', 4.2
WHERE NOT EXISTS (SELECT 1 FROM store_products WHERE brand = 'Local Premium' AND product_name = 'Beans')
UNION ALL
SELECT 
    (SELECT category_id FROM store_product_categories WHERE category_name = 'Food'),
    'Palm Oil', 'Queen Taste', 15000.00, 'bottle', 60, 'Oil Traders', 4.0
WHERE NOT EXISTS (SELECT 1 FROM store_products WHERE brand = 'Queen Taste' AND product_name = 'Palm Oil')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 9. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Quick lookups for common queries
CREATE INDEX IF NOT EXISTS idx_carts_by_moderator_pool ON shopping_carts(moderator_id, pool_id)
WHERE status = 'ACTIVE';

CREATE INDEX IF NOT EXISTS idx_orders_by_pool_status ON store_orders(pool_id, status)
WHERE status IN ('PENDING', 'CONFIRMED', 'PAID');

CREATE INDEX IF NOT EXISTS idx_products_by_category_price ON store_products(category_id, price)
WHERE is_active = TRUE;

-- Full-text search
CREATE INDEX IF NOT EXISTS idx_products_tsv ON store_products 
USING GIN (to_tsvector('english', product_name || ' ' || brand || ' ' || description));

-- ============================================================================
-- 10. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Cart summary with budget info
CREATE OR REPLACE VIEW cart_summary_view AS
SELECT 
    sc.cart_id,
    sc.pool_id,
    sc.moderator_id,
    sc.pool_budget,
    COUNT(DISTINCT ci.product_id) as item_count,
    SUM(ci.quantity_requested) as total_quantity,
    SUM(ci.quantity_requested * ci.unit_price) as cart_total,
    sc.pool_budget - COALESCE(SUM(ci.quantity_requested * ci.unit_price), 0) as remaining_budget,
    ROUND(100.0 * COALESCE(SUM(ci.quantity_requested * ci.unit_price), 0) / sc.pool_budget, 1) as budget_used_percent,
    sc.status
FROM shopping_carts sc
LEFT JOIN cart_items ci ON sc.cart_id = ci.cart_id
GROUP BY sc.cart_id, sc.pool_id, sc.moderator_id, sc.pool_budget, sc.status;

-- View: Order summary
CREATE OR REPLACE VIEW order_summary_view AS
SELECT 
    so.order_id,
    so.order_number,
    so.pool_id,
    so.moderator_id,
    so.status,
    COUNT(DISTINCT oi.product_id) as item_count,
    SUM(oi.quantity_ordered) as total_quantity,
    so.total_amount,
    so.created_at,
    so.expected_delivery_date
FROM store_orders so
LEFT JOIN order_items oi ON so.order_id = oi.order_id
GROUP BY so.order_id, so.order_number, so.pool_id, so.moderator_id, so.status, so.total_amount, so.created_at, so.expected_delivery_date;

-- View: Low stock products
CREATE OR REPLACE VIEW low_stock_products_view AS
SELECT 
    sp.product_id,
    sp.product_name,
    sp.brand,
    sp.price,
    sp.unit,
    sp.quantity_available,
    wi.reorder_level,
    wi.reorder_quantity,
    CASE 
        WHEN sp.quantity_available <= 0 THEN 'OUT_OF_STOCK'
        WHEN sp.quantity_available < wi.reorder_level THEN 'LOW_STOCK'
        ELSE 'OK'
    END as stock_status
FROM store_products sp
LEFT JOIN warehouse_inventory wi ON sp.product_id = wi.product_id
WHERE sp.is_active = TRUE AND sp.quantity_available < COALESCE(wi.reorder_level, 20)
ORDER BY sp.quantity_available ASC;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

SELECT 'Campus Pinduoduo Online Store Schema - Successfully Created!' as status;
