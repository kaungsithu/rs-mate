"""Skeleton loading components for improved UX."""
from fasthtml.common import *
from monsterui.all import *

__all__ = [
    'mk_skeleton_line', 'mk_skeleton_table_row', 'mk_skeleton_user_table',
    'mk_skeleton_role_table', 'mk_skeleton_group_table', 'mk_skeleton_form',
    'mk_skeleton_card'
]


def mk_skeleton_line(width: str = 'w-full', height: str = 'h-4'):
    """Create a skeleton line placeholder."""
    return Div(
        cls=(width, height, 'bg-gray-300 rounded animate-pulse')
    )


def mk_skeleton_table_row(columns: int = 6):
    """Create a skeleton table row."""
    return Tr(
        *[Td(mk_skeleton_line('w-full', 'h-8')) for _ in range(columns)],
        cls='border-b'
    )


def mk_skeleton_user_table(rows: int = 5):
    """Create skeleton for user table."""
    tbl_headers = ['ID', 'Username', 'Super', 'Groups', 'Roles', 'Actions']
    return Table(
        Thead(Tr(*map(Th, tbl_headers))),
        Tbody(
            *[mk_skeleton_table_row(len(tbl_headers)) for _ in range(rows)],
            cls='list'
        ),
        cls=(TableT.striped)
    )


def mk_skeleton_role_table(rows: int = 5):
    """Create skeleton for role table."""
    tbl_headers = ['ID', 'Role Name', 'Owner', 'Users', 'Nested Roles', 'Actions']
    return Table(
        Thead(Tr(*map(Th, tbl_headers))),
        Tbody(
            *[mk_skeleton_table_row(len(tbl_headers)) for _ in range(rows)],
            cls='list'
        ),
        cls=(TableT.striped)
    )


def mk_skeleton_group_table(rows: int = 5):
    """Create skeleton for group table."""
    tbl_headers = ['ID', 'Group Name', 'Users', 'Actions']
    return Table(
        Thead(Tr(*map(Th, tbl_headers))),
        Tbody(
            *[mk_skeleton_table_row(len(tbl_headers)) for _ in range(rows)],
            cls='list'
        ),
        cls=(TableT.striped)
    )


def mk_skeleton_form(sections: int = 3):
    """Create skeleton for form."""
    return Div(
        *[Div(
            mk_skeleton_line('w-1/4', 'h-4 mb-2'),
            mk_skeleton_line('w-full', 'h-10 mb-4'),
            cls='mb-6'
        ) for _ in range(sections)],
        mk_skeleton_line('w-1/4', 'h-10'),
        cls='space-y-4'
    )


def mk_skeleton_card(content=None):
    """Create skeleton for card."""
    if content is None:
        content = Div(
            mk_skeleton_line('w-1/2', 'h-6 mb-4'),
            mk_skeleton_line('w-full', 'h-8 mb-2'),
            mk_skeleton_line('w-full', 'h-8 mb-2'),
            mk_skeleton_line('w-3/4', 'h-8'),
        )
    return Card(content, cls='animate-pulse')
