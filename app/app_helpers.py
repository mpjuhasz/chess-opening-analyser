def color_value(val):
    r = 255 - int(75 * val)
    g = 200 + int(55 * val)
    b = 255
    return f"background-color: rgb({r},{g},{b})"
