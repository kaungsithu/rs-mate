from fasthtml.common import *
from monsterui.all import *

app, rt = fast_app(hdrs=Theme.blue.headers())

def PrivilegeBadges(privileges):
    colors = {"USAGE": "primary", "ALTER": "success", "SELECT": "info", "INSERT": "warning"}
    return Div(*[Label(p, cls=f'uk-label-{colors[p]}') for p in privileges])

def SchemaPrivilegesTable():
    return TableFromLists(
        header_data=["Schema", "Schema Privileges", "Default Privileges (Owners → Privileges)", "Manage"],
        body_data=[["Finance", PrivilegeBadges(["USAGE", "ALTER"]),
                   Div(
                       Div(Label("admin", cls="owner"), PrivilegeBadges(["INSERT", "SELECT"])),
                       Div(Label("manager", cls="owner"), PrivilegeBadges(["SELECT"]))
                   ),
                   Div(
                       Button(UkIcon("edit"), "Edit", cls=ButtonT.primary, data_uk_toggle="#edit-modal"),
                       Button(UkIcon("trash"), "Remove", cls=ButtonT.danger)
                   )
        ]],
        cls=(TableT.striped, TableT.hover))

def RelationPrivilegesTable():
    return TableFromLists(
        header_data=["Relation", "Privileges", "Manage"],
        body_data=[["finance.accounts", PrivilegeBadges(["SELECT", "INSERT"]),
                   Div(
                       Button(UkIcon("edit"), "Edit", cls=ButtonT.primary, data_uk_toggle="#edit-modal"),
                       Button(UkIcon("trash"), "Remove", cls=ButtonT.danger)
                   )
        ]],
        cls=(TableT.striped, TableT.hover))

def FilterDropdown():
    return LabelSelect(
        Options("All", "Finance", "Marketing", "Sales"), 
        label="Filter by Schema", id="schema-filter")

def EditPrivilegeModal():
    return Modal(
        ModalHeader(H3("Edit Privileges")),
        ModalBody(
            LabelCheckboxX("USAGE", id="priv_usage", checked=True),
            LabelCheckboxX("ALTER", id="priv_alter", checked=True),
            LabelCheckboxX("INSERT", id="priv_insert"),
            LabelCheckboxX("SELECT", id="priv_select")),
        ModalFooter(
            Button("Cancel", cls=ButtonT.ghost, data_uk_toggle="#edit-modal"),
            Button("Save", cls=ButtonT.primary)),
        id="edit-modal")

def AddPrivilegeModal():
    return Modal(
        ModalHeader(H3("Add Privilege")),
        ModalBody(
            LabelInput("Schema", id="add-schema"),
            LabelInput("Relation (Optional)", id="add-relation"),
            LabelCheckboxX("USAGE", id="add-priv-usage"),
            LabelCheckboxX("ALTER", id="add-priv-alter"),
            LabelCheckboxX("INSERT", id="add-priv-insert"),
            LabelCheckboxX("SELECT", id="add-priv-select")),
        ModalFooter(
            Button("Cancel", cls=ButtonT.ghost, data_uk_toggle="#add-modal"),
            Button("Add", cls=ButtonT.primary)),
        id="add-modal")

@rt
def index():
    return Container(
        H2("User Privileges: analyst_finance"),
        H3("Schema & Default Privileges"),
        Button(UkIcon("plus"), "Add", cls=ButtonT.primary, data_uk_toggle="#add-modal"),
        SchemaPrivilegesTable(),
        H3("Relation Privileges"),
        Button(UkIcon("plus"), "Add", cls=ButtonT.primary, data_uk_toggle="#add-modal"),
        FilterDropdown(),
        RelationPrivilegesTable(),
        EditPrivilegeModal(),
        AddPrivilegeModal(),
        cls=ContainerT.xl)

serve()
