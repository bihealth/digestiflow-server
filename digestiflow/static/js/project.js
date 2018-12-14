/**
 * Reverse-complement string.
 */
function revComp(seq) {
  function complement(a) {
    return {A: 'T', T: 'A', G: 'C', C: 'G'}[a];
  }

  return (seq || '').split('').reverse().map(complement).join('');
}

