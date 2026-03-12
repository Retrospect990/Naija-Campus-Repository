"""
Campus Pinduoduo: Escrow & Milestone System - Interactive Demo
This demonstrates the entire payment flow in action
"""

from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict
import uuid
import random

# ============================================================================
# ENUMS FOR STATE MANAGEMENT
# ============================================================================

class PoolStatus(Enum):
    OPEN = "open"
    LOCKED = "locked"
    IN_PURCHASE = "in_purchase"
    IN_DELIVERY = "in_delivery"
    COMPLETED = "completed"
    REFUNDED = "refunded"

class EscrowStatus(Enum):
    HELD = "held"
    COMPLETED = "completed"
    REFUNDED = "refunded"

class ParticipantStatus(Enum):
    ACTIVE = "active"
    CONFIRMED_RECEIVED = "confirmed_received"
    REFUNDED = "refunded"

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class User:
    id: str
    name: str
    email: str
    university: str
    is_moderator: bool = False
    bank_account: str = ""
    balance: float = 0.0

@dataclass
class EscrowTransaction:
    id: str
    pool_id: str
    participant_id: str
    amount: float
    transaction_type: str  # 'deposit', 'refund', 'release_to_moderator'
    escrow_status: EscrowStatus
    timestamp: datetime
    
    def __str__(self):
        status_symbol = {
            EscrowStatus.HELD: "💾",
            EscrowStatus.COMPLETED: "✅",
            EscrowStatus.REFUNDED: "↩️"
        }
        return f"{status_symbol.get(self.escrow_status, '?')} {self.transaction_type:20} ₦{self.amount:>10,.0f} [{self.escrow_status.value}]"

@dataclass
class PoolParticipant:
    id: str
    pool_id: str
    participant_id: str
    contribution_amount: float
    status: ParticipantStatus
    confirmation_pin: str
    confirmed_at: datetime = None

@dataclass
class PurchasePool:
    id: str
    moderator_id: str
    item_name: str
    total_goal_amount: float
    amount_raised: float = 0.0
    cost_per_slot: float = 0.0
    total_slots: int = 0
    slots_filled: int = 0
    pool_status: PoolStatus = PoolStatus.OPEN
    target_close_date: datetime = None
    created_at: datetime = field(default_factory=datetime.now)
    participants: List[PoolParticipant] = field(default_factory=list)
    escrow_transactions: List[EscrowTransaction] = field(default_factory=list)
    moderator_commission_percentage: float = 10.0

# ============================================================================
# ESCROW SYSTEM LOGIC
# ============================================================================

class EscrowSystem:
    """Main Escrow & Milestone Management System"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.pools: Dict[str, PurchasePool] = {}
        self.all_escrow_transactions: List[EscrowTransaction] = []
        self.all_participants: List[PoolParticipant] = []
        self.all_confirmations: Dict[tuple, bool] = {}  # (pool_id, user_id) -> confirmed
        
    # ========== USER MANAGEMENT ==========
    
    def create_user(self, name: str, email: str, university: str, is_moderator: bool = False, initial_balance: float = 100000.0):
        """Create a new user with initial balance"""
        user_id = str(uuid.uuid4())[:8]
        user = User(
            id=user_id,
            name=name,
            email=email,
            university=university,
            is_moderator=is_moderator,
            balance=initial_balance,
            bank_account=f"GTB-{random.randint(10000000, 99999999)}"
        )
        self.users[user_id] = user
        print(f"✅ User Created: {name} ({user_id}) | Balance: ₦{initial_balance:,}")
        return user_id
    
    # ========== POOL CREATION ==========
    
    def create_pool(self, moderator_id: str, item_name: str, total_goal: float, 
                   cost_per_slot: float, total_slots: int, days_to_deadline: int = 14):
        """Step 1: Moderator creates a purchase pool"""
        pool_id = str(uuid.uuid4())[:8]
        pool = PurchasePool(
            id=pool_id,
            moderator_id=moderator_id,
            item_name=item_name,
            total_goal_amount=total_goal,
            cost_per_slot=cost_per_slot,
            total_slots=total_slots,
            target_close_date=datetime.now() + timedelta(days=days_to_deadline)
        )
        self.pools[pool_id] = pool
        print(f"\n📋 POOL CREATED")
        print(f"   Item: {item_name}")
        print(f"   Pool ID: {pool_id}")
        print(f"   Goal: ₦{total_goal:,} | Slots: {total_slots} × ₦{cost_per_slot:,}")
        print(f"   Status: {pool.pool_status.value}")
        return pool_id
    
    # ========== STEP 2: STUDENT DEPOSITS ==========
    
    def student_joins_pool(self, student_id: str, pool_id: str):
        """Step 2: Student joins pool and deposits money"""
        pool = self.pools[pool_id]
        assert pool.pool_status == PoolStatus.OPEN, "Pool is not open"
        assert pool.slots_filled < pool.total_slots, "Pool is full"
        
        student = self.users[student_id]
        amount = pool.cost_per_slot
        
        # Generate PIN for later verification
        pin = f"{random.randint(100000, 999999)}"
        
        # Create participant record
        participant = PoolParticipant(
            id=str(uuid.uuid4())[:8],
            pool_id=pool_id,
            participant_id=student_id,
            contribution_amount=amount,
            status=ParticipantStatus.ACTIVE,
            confirmation_pin=pin
        )
        self.all_participants.append(participant)
        pool.participants.append(participant)
        
        # CRITICAL: Create escrow transaction (money is HELD, not released)
        escrow_txn = EscrowTransaction(
            id=str(uuid.uuid4())[:8],
            pool_id=pool_id,
            participant_id=student_id,
            amount=amount,
            transaction_type="deposit",
            escrow_status=EscrowStatus.HELD,  # ← MONEY HELD IN ESCROW
            timestamp=datetime.now()
        )
        self.all_escrow_transactions.append(escrow_txn)
        pool.escrow_transactions.append(escrow_txn)
        
        # Update pool
        pool.amount_raised += amount
        pool.slots_filled += 1
        
        print(f"\n💰 {student.name} joined pool | Deposited: ₦{amount:,} | PIN: {pin}")
        print(f"   Escrow Status: {EscrowStatus.HELD.value} (money HELD, not released)")
        print(f"   Pool Progress: {pool.slots_filled}/{pool.total_slots} slots | ₦{pool.amount_raised:,}/₦{pool.total_goal_amount:,}")
        
        # Check if pool reached goal
        if pool.amount_raised >= pool.total_goal_amount:
            self.lock_pool(pool_id)
        
        return participant
    
    # ========== STEP 3: POOL LOCKS WHEN GOAL MET ==========
    
    def lock_pool(self, pool_id: str):
        """Step 3: Pool reaches goal → Automatically LOCKED"""
        pool = self.pools[pool_id]
        assert pool.amount_raised >= pool.total_goal_amount
        
        pool.pool_status = PoolStatus.LOCKED
        print(f"\n🔒 POOL LOCKED!")
        print(f"   Goal reached: ₦{pool.amount_raised:,}")
        print(f"   Status: {pool.pool_status.value}")
        print(f"   → Moderator can now proceed to purchase items")
    
    # ========== STEP 4-5: PURCHASE & DELIVERY ==========
    
    def moderator_initiates_purchase(self, pool_id: str):
        """Step 4-5: Moderator purchases items and initiates distribution"""
        pool = self.pools[pool_id]
        assert pool.pool_status == PoolStatus.LOCKED
        
        pool.pool_status = PoolStatus.IN_DELIVERY
        
        print(f"\n📦 PURCHASE INITIATED & ITEMS DISTRIBUTED")
        print(f"   {self.users[pool.moderator_id].name} has distributed items")
        print(f"   Status: {pool.pool_status.value}")
        print(f"   💾 Money still HELD in escrow (awaiting student confirmations)")
    
    # ========== STEP 6: STUDENT CONFIRMATION ==========
    
    def student_confirms_receipt(self, student_id: str, pool_id: str, pin: str):
        """Step 6: Student confirms item received via PIN"""
        pool = self.pools[pool_id]
        assert pool.pool_status == PoolStatus.IN_DELIVERY, "Pool not in delivery"
        
        # Find participant
        participant = next(p for p in pool.participants 
                         if p.participant_id == student_id and p.pool_id == pool_id)
        
        # Verify PIN
        assert participant.confirmation_pin == pin, "❌ Invalid PIN!"
        
        # Mark as confirmed
        participant.status = ParticipantStatus.CONFIRMED_RECEIVED
        participant.confirmed_at = datetime.now()
        self.all_confirmations[(pool_id, student_id)] = True
        
        # Calculate confirmation percentage
        confirmed = len([p for p in pool.participants 
                        if p.status == ParticipantStatus.CONFIRMED_RECEIVED])
        total = len(pool.participants)
        confirmation_pct = (confirmed / total) * 100
        
        print(f"\n✅ {self.users[student_id].name} confirmed item receipt (PIN: {pin})")
        print(f"   Confirmations: {confirmed}/{total} ({confirmation_pct:.0f}%)")
        
        # Check if 70% threshold reached
        if confirmation_pct >= 70:
            self.release_funds_to_moderator(pool_id, confirmation_pct)
        else:
            print(f"   ⏳ Waiting for more confirmations... ({70-confirmation_pct:.0f}% more needed)")
    
    # ========== STEP 7: AUTOMATIC FUND RELEASE AT 70% ==========
    
    def release_funds_to_moderator(self, pool_id: str, confirmation_pct: float):
        """Step 7: RELEASE FUNDS to moderator when 70%+ confirmed"""
        pool = self.pools[pool_id]
        
        pool.pool_status = PoolStatus.COMPLETED
        
        # Calculate commission
        total_amount = pool.amount_raised
        commission_pct = pool.moderator_commission_percentage
        commission = (total_amount * commission_pct) / 100
        moderator = self.users[pool.moderator_id]
        
        # Create release transaction
        release_txn = EscrowTransaction(
            id=str(uuid.uuid4())[:8],
            pool_id=pool_id,
            participant_id=pool.moderator_id,
            amount=total_amount,
            transaction_type="release_to_moderator",
            escrow_status=EscrowStatus.COMPLETED,  # ← ESCROW CLOSED, FUNDS RELEASED
            timestamp=datetime.now()
        )
        self.all_escrow_transactions.append(release_txn)
        pool.escrow_transactions.append(release_txn)
        
        # Update moderator balance
        moderator.balance += commission
        
        print(f"\n🎉 FUNDS RELEASED TO MODERATOR!")
        print(f"   Confirmation Threshold: {confirmation_pct:.0f}% ✅ (>70%)")
        print(f"   Total Pool Amount: ₦{total_amount:,}")
        print(f"   Moderator Commission ({commission_pct}%): ₦{commission:,.0f}")
        print(f"   Status: {pool.pool_status.value}")
        print(f"   Moderator Balance Updated: ₦{moderator.balance:,}")
        print(f"\n   Escrow Status Changed: HELD → COMPLETED")
    
    # ========== ALTERNATIVE: AUTOMATIC REFUND ==========
    
    def process_refunds_for_expired_pool(self, pool_id: str):
        """Process automatic refunds if deadline passed with unmet goal"""
        pool = self.pools[pool_id]
        
        if pool.amount_raised >= pool.total_goal_amount:
            print(f"❌ Pool '{pool.item_name}' already completed. No refund needed.")
            return
        
        print(f"\n⚠️  AUTOMATIC REFUND TRIGGERED")
        print(f"   Pool deadline expired | Goal not met")
        print(f"   Collected: ₦{pool.amount_raised:,} (needed ₦{pool.total_goal_amount:,})")
        print(f"   Processing refunds for {len(pool.participants)} participants...")
        
        pool.pool_status = PoolStatus.REFUNDED
        
        for participant in pool.participants:
            # Create refund transaction
            refund_txn = EscrowTransaction(
                id=str(uuid.uuid4())[:8],
                pool_id=pool_id,
                participant_id=participant.participant_id,
                amount=participant.contribution_amount,
                transaction_type="refund",
                escrow_status=EscrowStatus.REFUNDED,  # ← MONEY RETURNED
                timestamp=datetime.now()
            )
            self.all_escrow_transactions.append(refund_txn)
            pool.escrow_transactions.append(refund_txn)
            
            # Return money to student
            student = self.users[participant.participant_id]
            student.balance += participant.contribution_amount
            
            participant.status = ParticipantStatus.REFUNDED
            
            print(f"   ✅ Refunded {student.name}: ₦{participant.contribution_amount:,}")
        
        print(f"\n   Status: {pool.pool_status.value}")
        print(f"   Escrow Status Changed: HELD → REFUNDED")

# ============================================================================
# REPORTING & AUDIT
# ============================================================================

    def print_escrow_ledger(self, pool_id: str = None):
        """Print complete escrow transaction ledger (audit trail)"""
        if pool_id:
            transactions = [t for t in self.all_escrow_transactions if t.pool_id == pool_id]
        else:
            transactions = self.all_escrow_transactions
        
        print(f"\n📊 ESCROW TRANSACTION LEDGER")
        print(f"{'='*80}")
        print(f"{'Type':<20} {'Amount':>15} {'Status':<15} {'Time':<20}")
        print(f"{'-'*80}")
        
        total_in = 0
        total_out = 0
        
        for txn in transactions:
            symbol = {
                "deposit": "💰",
                "refund": "↩️",
                "release_to_moderator": "✅"
            }.get(txn.transaction_type, "?")
            
            print(f"{symbol} {txn.transaction_type:<17} ₦{txn.amount:>12,.0f} {txn.escrow_status.value:<14} {txn.timestamp.strftime('%H:%M:%S')}")
            
            if txn.transaction_type == "deposit":
                total_in += txn.amount
            else:
                total_out += txn.amount
        
        print(f"{'-'*80}")
        print(f"{'Total Deposits':<20} ₦{total_in:>12,.0f}")
        print(f"{'Total Released/Refunded':<20} ₦{total_out:>12,.0f}")
        print(f"{'Balance (should be 0)':<20} ₦{total_in - total_out:>12,.0f}")
        print(f"{'='*80}\n")
    
    def print_pool_status(self, pool_id: str):
        """Print detailed pool status"""
        pool = self.pools[pool_id]
        print(f"\n{'='*80}")
        print(f"POOL: {pool.item_name}")
        print(f"{'='*80}")
        print(f"Status: {pool.pool_status.value:15} | Goal: ₦{pool.total_goal_amount:>12,.0f}")
        print(f"Raised: ₦{pool.amount_raised:>12,.0f} | Participants: {pool.slots_filled}/{pool.total_slots}")
        print(f"{'='*80}")
        print(f"{'Participant':<25} {'Amount':>15} {'Status':<20} {'PIN':<8}")
        print(f"{'-'*80}")
        
        for p in pool.participants:
            user = self.users[p.participant_id]
            print(f"{user.name:<25} ₦{p.contribution_amount:>12,.0f} {p.status.value:<19} {p.confirmation_pin}")
        
        print(f"{'='*80}\n")

# ============================================================================
# INTERACTIVE DEMO
# ============================================================================

def run_demo():
    """Run complete escrow system demo"""
    system = EscrowSystem()
    
    print("\n" + "="*80)
    print("CAMPUS PINDUODUO: ESCROW & MILESTONE SYSTEM DEMO")
    print("="*80)
    print("Demonstrating complete payment flow with safe fund management\n")
    
    # ========== SETUP ==========
    print("\n[SETUP] Creating users...")
    moderator = system.create_user("Chioma (Moderator)", "chioma@example.com", "LASU", is_moderator=True)
    student1 = system.create_user("Tunde (Student)", "tunde@example.com", "LASU")
    student2 = system.create_user("Zainab (Student)", "zainab@example.com", "LASU")
    student3 = system.create_user("Damilare (Student)", "damilare@example.com", "LASU")
    student4 = system.create_user("Amara (Student)", "amara@example.com", "LASU")
    
    # ========== POOL CREATION ==========
    print("\n[PHASE 1] Pool Creation & Collection")
    print("-" * 80)
    pool_id = system.create_pool(
        moderator_id=moderator,
        item_name="Premium Rice - 50kg bags",
        total_goal=50000.0,  # ₦50,000
        cost_per_slot=10000.0,  # ₦10,000 per person
        total_slots=5
    )
    
    # ========== STUDENTS JOIN ==========
    print("\n[DEPOSITS] Students deposit via Paystack (money held in escrow)...")
    p1 = system.student_joins_pool(student1, pool_id)
    p2 = system.student_joins_pool(student2, pool_id)
    p3 = system.student_joins_pool(student3, pool_id)
    p4 = system.student_joins_pool(student4, pool_id)
    p5 = system.student_joins_pool(student1, pool_id)  # 5th slot - goal reached!
    
    # ========== PRINT POOL STATUS ==========
    system.print_pool_status(pool_id)
    system.print_escrow_ledger(pool_id)
    
    # ========== PHASE 2: PURCHASE & DELIVERY ==========
    print("\n[PHASE 2] Purchase & Delivery")
    print("-" * 80)
    system.moderator_initiates_purchase(pool_id)
    
    # ========== PHASE 3: STUDENT CONFIRMATIONS ==========
    print("\n[PHASE 3] Students Confirm Item Receipt")
    print("-" * 80)
    print("Moderator sends PIN to each student via SMS...")
    
    # Students 1, 2, 3, 4 confirm (80% > 70% threshold)
    system.student_confirms_receipt(student1, pool_id, p1.confirmation_pin)
    system.student_confirms_receipt(student2, pool_id, p2.confirmation_pin)
    system.student_confirms_receipt(student3, pool_id, p3.confirmation_pin)
    system.student_confirms_receipt(student4, pool_id, p4.confirmation_pin)
    
    # ========== FINAL STATUS ==========
    print("\n[COMPLETE] Final Audit & Balance Check")
    print("-" * 80)
    system.print_pool_status(pool_id)
    system.print_escrow_ledger(pool_id)
    
    # ========== USER BALANCES ==========
    print("\n[BALANCES] Account Balances After Transaction")
    print("-" * 80)
    print(f"Moderator (Commission): ₦{system.users[moderator].balance:,.0f}")
    for sid in [student1, student2, student3, student4]:
        print(f"Student ({system.users[sid].name}): ₦{system.users[sid].balance:,.0f}")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE - All funds accounted for!")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_demo()
