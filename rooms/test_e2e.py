import pytest

# below to resolve error async error/ toggle comment
#import os
#os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.django_db
def test_homepage_loads(page, live_server):
    page.goto(live_server.url)

    assert page.locator("h1").inner_text() == "Room List"