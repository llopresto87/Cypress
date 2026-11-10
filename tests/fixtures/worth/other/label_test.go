package web

// Fixture: a Go test, listed as not checked (go).
import "testing"

func TestLabel(t *testing.T) {
	if Label != "Send" {
		t.Fatal("label")
	}
}
