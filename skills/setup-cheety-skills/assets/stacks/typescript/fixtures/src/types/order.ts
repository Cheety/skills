export type OrderData = {
  kundeId: number;   // !! IMMUTABILITY_DTO
  amount: number;    // !! STATE_MONEY_NUMBER
};

export type Order = {
  isPaid: boolean;      // !! STATE_BOOLEAN_FLAGS
  isShipped: boolean;
  hasRefund: boolean;
};
