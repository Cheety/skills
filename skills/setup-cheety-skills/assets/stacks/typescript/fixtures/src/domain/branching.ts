export function tier(tage: number): string {
  switch (true) {
    case tage > 60: return 'inkasso';
    case tage > 30: return 'zweite';
    default: return 'erste';
  }
}

export function load(id: number, hole: (id: number) => Promise<string>): Promise<string> {
  return hole(id)
    .then((wert) => wert.trim())
    .catch(() => '');
}
