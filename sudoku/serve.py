from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sudoku import Board, cull_board, generate_board
from wsgiref.simple_server import make_server


@view_config(route_name="render_sudoku")
def render_sudoku(request):
    unit = 3

    page_html = '<table style="border-collapse: collapse; padding: 0;">'

    try:
        values = []
        for x in request.GET["values"].split(","):
            values.append(int(x) if x else None)
    except (ValueError, KeyError):
        return new_board(request)

    if len(values) != unit ** 4:
        return new_board(request)

    board = Board(unit)

    for i, value in enumerate(values):
        if value is not None:
            board[(i // 9, i % 9)] = value

    for row in range(board.rows):
        page_html += '<tr style="padding: 0;">'
        for col in range(board.cols):
            page_html += '<td width=25 height=25 style="text-align: center; padding: 0; border: 1px solid gray;">{}</td>'.format(board[(row, col)] if (row, col) in board else '')
        page_html += "</tr>"

    page_html += "</table>"

    response = request.response
    response.body = bytes(page_html, request.url_encoding)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def new_board(request):
    board = cull_board(generate_board(), 0.6)
    values = [str(value) if value is not None else '' for value in board.values()]
    response = HTTPFound(
        request.route_url(
            "render_sudoku",
            _query=(("values", ",".join(values)),)
        )
    )
    return response


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_route('render_sudoku', '/')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()


if __name__ == '__main__':
    main(None)
