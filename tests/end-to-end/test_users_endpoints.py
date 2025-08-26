def test_user_profile(client, auth_headers, test_user):
    response = client.get("/users/profile/", headers=auth_headers)
    assert response.status_code == 200

    user = response.json()
    assert user["email"] == test_user.email
    assert user["username"] == test_user.username


def test_change_password(client, auth_headers, test_user):
    response = client.put(
        "/users/change-password/",
        headers=auth_headers,
        json={"password": "string", "new_password": "new password"},
    )

    assert response.status_code == 200

    # login with old password
    login_response = client.post(
        "/auth/log-in/",
        data={
            "username": test_user.email,
            "password": "string",
            "grant_type": "password",
        },
    )

    assert login_response.status_code == 401

    # login with new password
    login_response = client.post(
        "/auth/log-in/",
        data={
            "username": test_user.email,
            "password": "new password",
            "grant_type": "password",
        },
    )

    assert login_response.status_code == 200


def test_change_username(client, auth_headers, test_user):
    response = client.put(
        "/users/change-username/",
        headers=auth_headers,
        json={"username": "new username"},
    )

    assert response.status_code == 200

    profile_response = client.get("/users/profile/", headers=auth_headers)
    assert profile_response.status_code == 200

    user = profile_response.json()
    assert user["username"] == "new username"
