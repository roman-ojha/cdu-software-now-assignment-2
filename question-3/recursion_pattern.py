import turtle


def draw_inward_indent_edge(t, length, depth):
    """
    Draw a single edge using recursive inward indentation.
    """
    if depth == 0:
        t.forward(length)
        return

    third = length / 3.0

    draw_inward_indent_edge(t, third, depth - 1)

    t.right(60)
    draw_inward_indent_edge(t, third, depth - 1)

    t.left(120)
    draw_inward_indent_edge(t, third, depth - 1)

    t.right(60)
    draw_inward_indent_edge(t, third, depth - 1)


def draw_recursive_polygon(sides, side_length, depth):
    """
    Draw a polygon where each edge uses the recursive indentation pattern.
    """
    screen = turtle.Screen()
    screen.title("HIT137 Assignment 2 - Q3 Recursive Pattern")

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.pensize(1)

    # Rough centering
    t.penup()
    t.goto(-side_length / 2.0, side_length / 3.0)
    t.pendown()

    exterior_angle = 360.0 / sides
    for _ in range(sides):
        draw_inward_indent_edge(t, side_length, depth)
        t.left(exterior_angle)

    screen.mainloop()
