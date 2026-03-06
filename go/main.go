package main

import (
	"aria/internal/config"
	"aria/internal/tui"
	"fmt"
	"os"
)

func main() {
	// Load configuration (triggers init via import)
	_ = config.Load()
	// Run TUI
	if err := tui.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
