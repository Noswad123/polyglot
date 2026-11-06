function fibonacci(length) {
let prev1 = 1;
let prev2 = 1;
const sequence = [];
  for (let i = 0; i < length; i++) {
    if (i % 2 == 0) {
      sequence.push(prev1 + prev2);
      prev2 = sequence[i];
      console.log(sequence[i]);
    } else {
      sequence.push(prev1 + prev2);
      prev1 = sequence[i];
      console.log(sequence[i]);
    }
  }
  sequence.unshift(1);
  return sequence;
}

console.log(fibonacci(20));
