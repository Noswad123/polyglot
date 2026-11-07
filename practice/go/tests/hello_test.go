package exercises

import "testing"

var FUNCTION func() string = Hello // polyglot:api

func TestHello(t *testing.T) {
	if result := FUNCTION(); result != "Hello, World!" {
		t.Fatalf("Your result: %q\nExpected result: %q", result, "Hello, World!")
	}
}
