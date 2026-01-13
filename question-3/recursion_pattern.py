def draw_inward_indent_edge(t, length, depth):
    """
    Draw a single edge using recursive inward indentation.

    Rules per recursion:
    1) Split the edge into 3 equal segments
    2) Replace the middle segment with two sides of an inward equilateral triangle
    3) Repeat recursively for all 4 resulting segments until depth == 0
    """
    if depth == 0:
        t.forward(length)
        return

    third = length / 3.0

    # Segment 1
    draw_inward_indent_edge(t, third, depth - 1)

    # Inward indentation (two triangle sides)
    t.right(60)
    draw_inward_indent_edge(t, third, depth - 1)

    t.left(120)
    draw_inward_indent_edge(t, third, depth - 1)

    t.right(60)

    # Segment 4
    draw_inward_indent_edge(t, third, depth - 1)
