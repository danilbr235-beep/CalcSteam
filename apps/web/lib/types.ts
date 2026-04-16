export type UserRole = 'admin' | 'operator' | 'viewer';

export type CodeStatus = 'new' | 'reserved' | 'sent' | 'redeemed' | 'problem' | 'archived';

export type RiskStatus =
  | 'ok'
  | 'low_margin'
  | 'loss'
  | 'no_combo'
  | 'stale_rate'
  | 'low_stock'
  | 'manual_review';

export interface CodeItem {
  id: number;
  batch_id: number;
  supplier_code_type_id: number;
  masked_code: string;
  status: CodeStatus;
  purchase_cost_rub: number;
}

export interface OrderRow {
  id: number;
  external_ref: string;
  sell_nominal_id: number;
  status: string;
  expected_revenue_rub: number;
  manual_review: boolean;
}
