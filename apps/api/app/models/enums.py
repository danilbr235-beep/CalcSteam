from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    operator = "operator"
    viewer = "viewer"


class CodeStatus(str, Enum):
    new = "new"
    reserved = "reserved"
    sent = "sent"
    redeemed = "redeemed"
    problem = "problem"
    archived = "archived"


class OrderStatus(str, Enum):
    new = "new"
    reserved = "reserved"
    fulfilled = "fulfilled"
    problem = "problem"
    completed = "completed"


class ItemRiskStatus(str, Enum):
    ok = "ok"
    low_margin = "low_margin"
    loss = "loss"
    no_combo = "no_combo"
    stale_rate = "stale_rate"
    low_stock = "low_stock"
    manual_review = "manual_review"
