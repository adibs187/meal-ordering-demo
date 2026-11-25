import ast
from pathlib import Path


def test_required_files_exist():
    root = Path(__file__).resolve().parent
    required = [
        "main.py",
        "database.py",
        "seed_demo_data.py",
        "requirements.txt",
        ".env.example",
        "static/index.html",
        "static/styles.css",
        "static/app.js",
        "sql/01_create_database.sql",
        "sql/02_verify_changes.sql",
    ]
    for relative_path in required:
        assert (root / relative_path).is_file(), f"Missing {relative_path}"


def test_use_case_endpoints_are_present():
    source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
    assert '@app.post("/api/menu-items"' in source
    assert '@app.put("/api/menu-items/{item_id}")' in source
    assert '@app.patch("/api/menu-items/{item_id}/stock")' in source


def test_responsive_rtl_interface():
    root = Path(__file__).resolve().parent
    html = (root / "static/index.html").read_text(encoding="utf-8")
    css = (root / "static/styles.css").read_text(encoding="utf-8")
    assert 'dir="rtl"' in html
    assert 'name="viewport"' in html
    assert "@media(max-width:680px)" in css


def test_connection_status_matches_api_and_database_state():
    root = Path(__file__).resolve().parent
    html = (root / "static/index.html").read_text(encoding="utf-8")
    javascript = (root / "static/app.js").read_text(encoding="utf-8")
    assert 'id="serverStatus"' in html
    assert 'id="serverText"' in html
    assert 'setConnection("connected")' in javascript
    assert 'setConnection("error")' in javascript
    assert 'response.status===503' in javascript


def test_seed_contains_five_rows_for_each_table():
    source = Path(__file__).with_name("seed_demo_data.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {"RESTAURANTS", "MENU_ITEMS"}:
                values[target.id] = ast.literal_eval(node.value)
    assert len(values["RESTAURANTS"]) == 5
    assert len(values["MENU_ITEMS"]) == 5
    assert "SELECT TOP 5 RestaurantID" in source
    assert "SELECT TOP 5 ItemID" in source


def test_uc025_updates_only_description_and_price():
    source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
    update_section = source.split('@app.put("/api/menu-items/{item_id}")', 1)[1]
    update_section = update_section.split('@app.patch("/api/menu-items/{item_id}/stock")', 1)[0]
    assert "SET Description=?, Price=?, UpdatedAt=SYSDATETIME()" in update_section
    assert "RestaurantID=?" not in update_section
    assert "ItemName=?" not in update_section
    assert "InStock=?" not in update_section
