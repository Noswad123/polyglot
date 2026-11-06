import { assert } from "chai";
import { strStr } from "./findTheIndexOfTheFirstOccurrenceInAString";

describe(strStr.name, function() {
	it('should find the string', function() {
		const expected = 4;
		const result = strStr('mississippi', 'issip');
		assert.strictEqual(result, expected);
	})
});
