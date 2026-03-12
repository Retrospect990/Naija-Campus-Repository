-- Campus Pinduoduo: Safe-Buy Escrow System
-- PostgreSQL/Supabase Database Schema
-- Created for secure group-buying transactions

-- ============================================================================
-- 1. CAMPUSES TABLE - University/Campus Information
-- ============================================================================
CREATE TABLE IF NOT EXISTS campuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    location VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Nigeria',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_campuses_name ON campuses(name);
CREATE INDEX idx_campuses_city ON campuses(city);

-- ============================================================================
-- 2. PROFILES TABLE - User Identity (Students and Moderators)
-- ============================================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20),
    university_id VARCHAR(100),
    campus_id UUID REFERENCES campuses(id) ON DELETE SET NULL,
    is_moderator BOOLEAN DEFAULT FALSE,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    account_number VARCHAR(20),
    bank_name VARCHAR(100),
    bank_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_campus ON profiles(campus_id);
CREATE INDEX idx_profiles_moderator ON profiles(is_moderator);
CREATE INDEX idx_profiles_created ON profiles(created_at DESC);

-- ============================================================================
-- 3. PURCHASE_POOLS TABLE - Group Buying Pool Details
-- ============================================================================
CREATE TYPE pool_status AS ENUM ('open', 'locked', 'in_delivery', 'completed', 'refunded', 'cancelled');

CREATE TABLE IF NOT EXISTS purchase_pools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moderator_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    campus_id UUID NOT NULL REFERENCES campuses(id) ON DELETE RESTRICT,
    item_name VARCHAR(255) NOT NULL,
    item_description TEXT,
    category VARCHAR(100),
    image_url TEXT,
    goal_amount DECIMAL(15, 2) NOT NULL,
    raised_amount DECIMAL(15, 2) DEFAULT 0.00,
    pool_status pool_status DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW(),
    deadline TIMESTAMP,
    locked_at TIMESTAMP,
    completed_at TIMESTAMP,
    refunded_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pools_moderator ON purchase_pools(moderator_id);
CREATE INDEX idx_pools_campus ON purchase_pools(campus_id);
CREATE INDEX idx_pools_status ON purchase_pools(pool_status);
CREATE INDEX idx_pools_created ON purchase_pools(created_at DESC);
CREATE INDEX idx_pools_deadline ON purchase_pools(deadline);

-- ============================================================================
-- 4. POOL_PARTICIPANTS TABLE - Student Participation Records
-- ============================================================================
CREATE TABLE IF NOT EXISTS pool_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES purchase_pools(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    amount_contributed DECIMAL(15, 2) NOT NULL,
    confirmation_pin VARCHAR(6),
    receipt_confirmed BOOLEAN DEFAULT FALSE,
    confirmed_at TIMESTAMP,
    joined_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(pool_id, participant_id)
);

CREATE INDEX idx_participants_pool ON pool_participants(pool_id);
CREATE INDEX idx_participants_student ON pool_participants(participant_id);
CREATE INDEX idx_participants_confirmed ON pool_participants(receipt_confirmed);

-- ============================================================================
-- 5. ESCROW_TRANSACTIONS TABLE - IMMUTABLE FUND LEDGER
-- ============================================================================
-- This table records every fund movement and CANNOT be deleted or modified
-- It serves as the immutable audit trail for all transactions
-- ============================================================================
CREATE TYPE transaction_type AS ENUM ('deposit', 'release', 'refund', 'commission');
CREATE TYPE escrow_status AS ENUM ('held', 'released', 'refunded', 'cancelled');

CREATE TABLE IF NOT EXISTS escrow_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES purchase_pools(id) ON DELETE RESTRICT,
    participant_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    transaction_type transaction_type NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    escrow_status escrow_status NOT NULL DEFAULT 'held',
    timestamp TIMESTAMP DEFAULT NOW(),
    reference_number VARCHAR(100) UNIQUE DEFAULT gen_random_uuid()::TEXT,
    description TEXT,
    payment_gateway VARCHAR(50),
    transaction_id_external VARCHAR(255)
);

-- Make escrow_transactions immutable using triggers (see triggers section)
CREATE INDEX idx_transactions_pool ON escrow_transactions(pool_id);
CREATE INDEX idx_transactions_participant ON escrow_transactions(participant_id);
CREATE INDEX idx_transactions_type ON escrow_transactions(transaction_type);
CREATE INDEX idx_transactions_status ON escrow_transactions(escrow_status);
CREATE INDEX idx_transactions_timestamp ON escrow_transactions(timestamp DESC);

-- ============================================================================
-- 6. MILESTONE_VERIFICATIONS TABLE - Delivery Confirmations
-- ============================================================================
CREATE TABLE IF NOT EXISTS milestone_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES purchase_pools(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    item_received BOOLEAN DEFAULT FALSE,
    item_condition VARCHAR(50), -- 'perfect', 'minor_damage', 'major_damage'
    confirmed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(pool_id, participant_id)
);

CREATE INDEX idx_verifications_pool ON milestone_verifications(pool_id);
CREATE INDEX idx_verifications_participant ON milestone_verifications(participant_id);
CREATE INDEX idx_verifications_confirmed ON milestone_verifications(item_received);

-- ============================================================================
-- 7. MODERATOR_COMMISSIONS TABLE - Commission Tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS moderator_commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES purchase_pools(id) ON DELETE CASCADE,
    moderator_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    total_pools_amount DECIMAL(15, 2) NOT NULL,
    commission_percentage DECIMAL(5, 2) DEFAULT 10.00,
    commission_amount DECIMAL(15, 2) NOT NULL,
    payout_amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'failed'
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_commissions_moderator ON moderator_commissions(moderator_id);
CREATE INDEX idx_commissions_pool ON moderator_commissions(pool_id);
CREATE INDEX idx_commissions_status ON moderator_commissions(status);

-- ============================================================================
-- 8. REFUND_QUEUE TABLE - Pending Refunds
-- ============================================================================
CREATE TABLE IF NOT EXISTS refund_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES purchase_pools(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    amount DECIMAL(15, 2) NOT NULL,
    reason VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processed', 'failed'
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_refunds_participant ON refund_queue(participant_id);
CREATE INDEX idx_refunds_pool ON refund_queue(pool_id);
CREATE INDEX idx_refunds_status ON refund_queue(status);

-- ============================================================================
-- 9. DISPUTES TABLE - Conflict Resolution
-- ============================================================================
CREATE TABLE IF NOT EXISTS disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES purchase_pools(id) ON DELETE CASCADE,
    initiator_id UUID NOT NULL REFERENCES profiles(id) ON DELETE SET NULL,
    respondent_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'under_review', 'resolved', 'closed'
    resolution_notes TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_disputes_pool ON disputes(pool_id);
CREATE INDEX idx_disputes_initiator ON disputes(initiator_id);
CREATE INDEX idx_disputes_status ON disputes(status);

-- ============================================================================
-- 10. ACTIVITY_LOG TABLE - Complete Audit Trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_action ON activity_log(action);
CREATE INDEX idx_activity_timestamp ON activity_log(timestamp DESC);

-- ============================================================================
-- TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Function to prevent deletion/update of escrow_transactions
CREATE OR REPLACE FUNCTION validate_escrow_transaction_immutability()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'Escrow transactions are immutable and cannot be modified or deleted.';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER escrow_transaction_immutable
BEFORE UPDATE OR DELETE ON escrow_transactions
FOR EACH ROW
EXECUTE FUNCTION validate_escrow_transaction_immutability();

-- Function to log pool status changes
CREATE OR REPLACE FUNCTION log_pool_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.pool_status != OLD.pool_status THEN
        INSERT INTO activity_log (action, resource_type, resource_id, details)
        VALUES (
            'POOL_STATUS_CHANGED',
            'purchase_pool',
            NEW.id,
            jsonb_build_object('old_status', OLD.pool_status, 'new_status', NEW.pool_status)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pool_status_log
AFTER UPDATE ON purchase_pools
FOR EACH ROW
EXECUTE FUNCTION log_pool_status_change();

-- Function to update profile timestamps
CREATE OR REPLACE FUNCTION update_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profile_timestamp_update
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE FUNCTION update_profile_timestamp();

-- Function to update pool timestamp
CREATE OR REPLACE FUNCTION update_pool_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pool_timestamp_update
BEFORE UPDATE ON purchase_pools
FOR EACH ROW
EXECUTE FUNCTION update_pool_timestamp();

-- ============================================================================
-- PERFORMANCE VIEWS
-- ============================================================================

-- View for pool completion rate
CREATE OR REPLACE VIEW pool_completion_stats AS
SELECT 
    p.id,
    p.item_name,
    p.goal_amount,
    p.raised_amount,
    ROUND((p.raised_amount / p.goal_amount * 100)::numeric, 2) as progress_percent,
    COUNT(DISTINCT pp.participant_id) as participant_count,
    COUNT(DISTINCT CASE WHEN mv.item_received THEN mv.participant_id END) as confirmed_count,
    ROUND(
        COUNT(DISTINCT CASE WHEN mv.item_received THEN mv.participant_id END)::numeric 
        / 
        NULLIF(COUNT(DISTINCT pp.participant_id), 0) * 100, 2
    ) as confirmation_percent
FROM purchase_pools p
LEFT JOIN pool_participants pp ON p.id = pp.pool_id
LEFT JOIN milestone_verifications mv ON p.id = mv.pool_id AND pp.participant_id = mv.participant_id
GROUP BY p.id, p.item_name, p.goal_amount, p.raised_amount;

-- View for moderator statistics
CREATE OR REPLACE VIEW moderator_stats AS
SELECT 
    p.id as moderator_id,
    p.name,
    COUNT(DISTINCT pp.id) as total_pools,
    SUM(pp.goal_amount) as total_pool_value,
    COUNT(DISTINCT CASE WHEN pp.pool_status = 'completed' THEN pp.id END) as completed_pools,
    COUNT(DISTINCT CASE WHEN pp.pool_status = 'refunded' THEN pp.id END) as failed_pools,
    COALESCE(SUM(mc.commission_amount), 0) as total_commissions
FROM profiles p
LEFT JOIN purchase_pools pp ON p.id = pp.moderator_id
LEFT JOIN moderator_commissions mc ON pp.id = mc.pool_id
WHERE p.is_moderator = TRUE
GROUP BY p.id, p.name;

-- ============================================================================
-- INITIAL DATA (Optional - Remove for production)
-- ============================================================================

-- Insert sample campus
INSERT INTO campuses (name, city, state) 
VALUES ('University of Lagos', 'Lagos', 'Lagos')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- FOREIGN KEY CONSTRAINTS (Already defined above)
-- ============================================================================
-- All foreign keys defined in table creation statements
-- Cascade delete on participant and transaction tables
-- Restrict delete on moderator and campus references

-- ============================================================================
-- DOCUMENTATION
-- ============================================================================
/*
TABLE DESCRIPTIONS:

1. campuses - Represents universities/campuses where pools operate
   - Campus-level isolation: Students only see their campus's pools
   - Used for RLS policies

2. profiles - User accounts (students and moderators)
   - is_moderator flag differentiates role
   - balance field tracks account balance
   - bank details for Flutterwave payouts

3. purchase_pools - The actual group-buying pools
   - States: open → locked → in_delivery → completed/refunded
   - goal_amount: Target amount to be raised
   - raised_amount: Total deposited so far

4. pool_participants - Links students to pools
   - amount_contributed: How much this student contributed
   - confirmation_pin: 6-digit PIN for delivery verification
   - receipt_confirmed: Whether student confirmed receipt

5. escrow_transactions - IMMUTABLE AUDIT LEDGER
   - CANNOT be deleted (enforced by trigger)
   - Records every fund movement
   - Types: deposit, release, refund, commission
   - Statuses: held (in escrow), released, refunded

6. milestone_verifications - Delivery confirmations
   - item_received: Boolean confirmation
   - item_condition: Quality check
   - Uses PIN from pool_participants

7. moderator_commissions - Payout tracking
   - Calculated when funds released
   - Usually 10% of pool amount
   - Tracks payment status

8. refund_queue - Pending refunds
   - Automatic refunds for failed/expired pools
   - Tracks status (pending/processed)

9. disputes - Conflict resolution
   - For initiator vs respondent conflicts
   - Resolution tracked

10. activity_log - Audit trail
    - Every action logged
    - JSONB for flexible details

SECURITY:
- RLS policies (see rls_policies.sql) enforce data isolation
- escrow_transactions immutable (trigger prevents changes)
- Timestamps auto-updated
*/
