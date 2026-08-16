export function execute(): string {
  // This used to contain a console.log() and a process.env access.
  // debugger and `as any` are only mentioned here.
  const hint = 'Please use neither console.log() nor process.env here.';
  const environment = 'produktion';
  return `${hint} ${environment}`;
}
