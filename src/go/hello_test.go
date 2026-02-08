package main

import "testing"

func TestHello(t *testing.T) {
	result := Hello()
	expected := "Hello, World!"

	if expected != result {
		t.Errorf("got %q, expexted %q", result, expected)
	} 
}

