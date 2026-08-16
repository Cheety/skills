type Zustand = 'draft' | 'sent' | 'dunning' | 'paid' | 'cancelled';

const ERLAUBT: Record<Zustand, readonly Zustand[]> = {
  draft: ['sent', 'cancelled'],
  sent: ['dunning', 'paid', 'cancelled'],
  dunning: ['paid', 'cancelled'],
  paid: [],
  cancelled: [],
};

export function canTransitionTo(von: Zustand, nach: Zustand): boolean {
  return ERLAUBT[von].includes(nach);
}

export function label(state: Zustand): string {
  switch (state) {
    case 'draft': return 'Entwurf';
    case 'sent': return 'Versendet';
    case 'dunning': return 'Dunning';
    case 'paid': return 'Bezahlt';
    case 'cancelled': return 'Storniert';
  }
}
