from app.auth.model import RegisterUserRequest


def test_register_login_flow(client, test_user):
    # register user
    user_data = RegisterUserRequest(
        email=test_user.email, username=test_user.username, password="string"
    )

    response = client.post("/auth/sign-up/", json=user_data.model_dump())
    assert response.status_code == 201

    # POST /auth/log-in/
    # Content-Type: application/x-www-form-urlencoded
    # username=test@example.com&password=string&grant_type=password
    # OAuth2PasswordRequestForm → expects form-data (not JSON).
    login_response = client.post(
        "/auth/log-in/",
        data={
            "username": test_user.email,
            "password": "string",
            "grant_type": "password",
        },
    )

    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


# signup failure
def test_sign_up_failures(client, test_user):
    user_data = RegisterUserRequest(
        email=test_user.email, username=test_user.username, password="string"
    )

    response = client.post("/auth/sign-up/", json=user_data.model_dump())

    # username & email conflict
    response = client.post("/auth/sign-up/", json=user_data.model_dump())
    assert response.status_code == 409


# login failure
def test_log_in_failures(client, test_user):
    user_data = RegisterUserRequest(
        email=test_user.email, username=test_user.username, password="string"
    )

    client.post("/auth/sign-up/", json=user_data.model_dump())

    # invalid password
    login_response = client.post(
        "/auth/log-in/",
        data={
            "username": test_user.email,
            "password": "strings",
            "grant_type": "password",
        },
    )

    assert login_response.status_code == 401

    # invalid email
    login_response = client.post(
        "/auth/log-in/",
        data={
            "username": "test@gmail.com",
            "password": "string",
            "grant_type": "password",
        },
    )

    assert login_response.status_code == 401
