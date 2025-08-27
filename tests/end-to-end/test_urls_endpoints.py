from app.urls.service import SERVER_ADDRESS


def test_short_get_url_flow(client):
    # create a url
    response = client.post(
        "/urls/short-url-public/",
        json={"long_url": "https://example.com/"},
    )

    assert response.status_code == 201
    short_code = response.json()["short_code"]

    # get long url from shorted
    response = client.get(short_code, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"


def test_short_url_private(client, auth_headers):
    response = client.post(
        "/urls/short-url/",
        headers=auth_headers,
        json={"long_url": "https://example.com/"},
    )

    assert response.status_code == 201
    short_code = response.json()["short_code"]
    assert short_code.startswith(f"{SERVER_ADDRESS}/urls/get-url/")

    # without login. auth_header
    response = client.post(
        "/urls/short-url/",
        json={"long_url": "https://example.com/"},
    )
    assert response.status_code == 401

    # failure
    response = client.post(
        "/urls/short-url/",
        headers=auth_headers,
        json={"long_url": "ws://example.com/"},
    )
    assert response.status_code == 422


def test_short_url_public(client):
    response = client.post(
        "/urls/short-url-public/",
        json={"long_url": "https://example.com/"},
    )

    assert response.status_code == 201
    short_code = response.json()["short_code"]
    assert short_code.startswith(f"{SERVER_ADDRESS}/urls/get-url/")

    # failure
    response = client.post(
        "/urls/short-url-public/",
        json={"long_url": "ws://example.com/"},
    )
    assert response.status_code == 422


def test_list_urls(client, auth_headers):
    response = client.get("/urls/list-urls/", headers=auth_headers)
    assert response.status_code == 200

    # without login
    response = client.get("/urls/list-urls/")
    assert response.status_code == 401


def test_get_url(client):
    # non existing url
    non_existing_shor_code = "10"
    response = client.get(
        f"/urls/get-url/{non_existing_shor_code}", follow_redirects=False
    )
    assert response.status_code == 404
    data = response.json()["detail"]
    assert data == f"{non_existing_shor_code} corresponding long url not found"
