# Adding a command to toggle between light and dark theme
    def change_theme(theme):
        set_theme(theme)
        print(f"{COLOR_BG}{COLOR_TEXT}Theme changed to {theme}!\n")

    # ... (existing code)
    if __name__ == "__main__":
        # ... (other existing main logic)
        change_theme('dark')  # Set the default theme to dark