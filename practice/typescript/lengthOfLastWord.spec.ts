import {assert} from 'chai';
import { lengthOfLastWord } from './lengthOfLastWord';

describe(lengthOfLastWord.name, function() {
	[{input: 'fly me   to   the moon  ', expected: 4}]. forEach(({input, expected}) => {
		it(`should ${input} for ${expected}`, function() {
			const result = lengthOfLastWord(input);
			assert.strictEqual(result, expected);
		})
	})
})
