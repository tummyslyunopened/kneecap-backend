from django.conf import settings
from django.core.management.base import BaseCommand
import ast
import os
import subprocess


def get_template_views(views_py_path):
    """
    Parses the given views.py file and returns a list of view function names
    that call 'render' (i.e., return a template).
    """
    with open(views_py_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    template_views = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for stmt in ast.walk(node):
                if (
                    isinstance(stmt, ast.Call)
                    and isinstance(stmt.func, ast.Name)
                    and stmt.func.id == "render"
                ):
                    template_views.append(node.name)
                    break
    return template_views


def get_urls_for_views(view_names, urls_py_path):
    """
    Given a list of view names and a urls.py file path, returns a dict mapping
    view names to their associated URL patterns.
    """
    with open(urls_py_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    view_to_url = {}

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "path"
        ):
            # Get the view function name
            if len(node.args) >= 2:
                view_func = node.args[1]
                if isinstance(view_func, ast.Name):
                    view_name = view_func.id
                elif isinstance(view_func, ast.Attribute):
                    view_name = view_func.attr
                else:
                    continue

                if view_name in view_names:
                    # Get the URL pattern string
                    url_arg = node.args[0]
                    if isinstance(url_arg, ast.Constant):  # Python 3.8+
                        url_pattern = url_arg.value
                    elif isinstance(url_arg, ast.Str):  # Python <3.8
                        url_pattern = url_arg.s
                    else:
                        continue
                    view_to_url[view_name] = url_pattern

    return view_to_url


try:
    from playwright.sync_api import sync_playwright
except ImportError:
    raise ImportError(
        "Playwright is not installed. This command is intended for development use only."
    )


class Command(BaseCommand):
    help = "A development-only command using Playwright"

    def handle(self, *args, **options):
        self.stdout.write("Starting Playwright command...")

        site_url = getattr(settings, "SITE_URL", None)
        if not site_url:
            raise ValueError("SITE_URL is not defined in settings.")

        # Determine the current commit hash
        try:
            commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        except subprocess.CalledProcessError:
            raise RuntimeError(
                "Failed to determine the current commit hash. Ensure this is a Git repository."
            )

        template_views = get_template_views(
            os.path.join(getattr(settings, "BASE_DIR"), "dashboard", "views.py")
        )

        self.stdout.write(f"Found template views: {template_views}")

        urls_for_views = get_urls_for_views(
            template_views, os.path.join(getattr(settings, "BASE_DIR"), "kneecap", "urls.py")
        )

        self.stdout.write(f"URLs for views: {urls_for_views}")

        os.makedirs(os.path.join(".data", "playwright"), exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for view_name, url_pattern in urls_for_views.items():
                screenshot_path = os.path.join(
                    ".data", "playwright", f"{commit_hash}-{view_name}.png"
                )
                mobile_screenshot_path = os.path.join(
                    ".data", "playwright", f"{commit_hash}-{view_name}-mobile.png"
                )

                page = browser.new_page()
                page.goto(f"http://{site_url}/{url_pattern}")
                page.screenshot(path=screenshot_path)
                self.stdout.write(f"Screenshot saved to {screenshot_path}")

                # Take mobile-sized screenshot
                mobile_page = browser.new_page(viewport={"width": 375, "height": 667})
                mobile_page.goto(f"http://{site_url}/{url_pattern}")
                mobile_page.screenshot(path=mobile_screenshot_path)
                self.stdout.write(f"Mobile screenshot saved to {mobile_screenshot_path}")

            browser.close()

        self.stdout.write("Playwright command completed.")
