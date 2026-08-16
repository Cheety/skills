export type InvoiceStatus =
  | { readonly status: 'draft' }
  | { readonly status: 'sent'; readonly sentAt: Date }
  | { readonly status: 'dunning'; readonly dunnedAt: Date }
  | { readonly status: 'paid'; readonly bezahltAm: Date }
  | { readonly status: 'cancelled' };

export type InvoiceData = {
  readonly kundeId: number;
  readonly betragCents: number;
};
