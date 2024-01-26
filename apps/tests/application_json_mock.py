
JSON_data = """{
    "description": "asdasdasd",
    "name": "asdasd",
    "slug": "application_slug",
    "owner": {
        "username": "owner_user_name",
        "first_name": "",
        "last_name": "",
        "email": "admin1@mail.ru",
        "is_staff": true,
        "is_active": true,
        "date_joined": "2023-10-09T09:10:20.261413Z"
    },
    "responses": [
        {
            "status_code": 201,
            "creator": null,
            "resources": [
                {
                    "description": "application_resource_description",
                    "method": "GET",
                    "proxy_destination_address": null,
                    "response_type": "CUSTOM",
                    "slug": "application_resource_slug",
                    "tail": "dadas",
                    "creator": null,
                    "is_enabled": true,
                    "inject_stubborn_headers": false,
                    "hooks": [
                        {
                            "action": "webhook",
                            "lifecycle": "before",
                            "order": 1,
                            "timeout": 0,
                            "request": {
                                "name": "hook_request_name",
                                "query_params": {
                                    "q1": "333",
                                    "ddd": "fff"
                                },
                                "uri": "http://127.0.0.1/ffff/adadad",
                                "method": "GET",
                                "creator": {
                                    "username": "creator_name",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "admin@mail.ru",
                                    "is_staff": true,
                                    "is_active": true,
                                    "date_joined": "2023-10-09T09:10:20.261413Z"
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}"""
